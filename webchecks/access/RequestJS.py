"""Provides the RequestJS class which sends requests and does realtime
rendering of the result, thus executing (and requesting) Javascript."""

import re
import time
import atexit
from typing import Tuple, Collection
from bs4 import BeautifulSoup


from webchecks.config import * # pylint: disable=wildcard-import
from webchecks.monitor.Report import Report
from webchecks.utils.file_ops import refd_content_may_have_fileformat
from webchecks.utils.messaging import logging, logging_push_where, logging_pop_where
from webchecks.utils.url import remove_args_from_url
from .security import is_allowed_url

try: # optional requirements .. here they go
    from seleniumwire import webdriver
    from seleniumwire.utils import decode as sw_decode
    from selenium.webdriver.firefox.service import Service as FirefoxService
    from selenium.webdriver.firefox.options import Options
    from selenium.common.exceptions import TimeoutException
except ImportError:
    print("Enabling JavaScript requires selenium and selenium-wire. Please install both \
using 'pip3 install selenium, selenium-wire'.")


class URLPair:
    """Represents a pair of URLs. One is being edited to add e.g. protocol.
    However, it is necessary to keep the original URL too."""
    def __init__(self, original_url, url):
        self.url = url
        self.original_url = original_url


class RequestJS: # pragma: no cover
    """Session manager for the requests where JS is enabled."""
    def __init__(self):
        self.reporter = Report() # pylint: disable=no-value-for-parameter
        self._requests = []
        self.js_checktable = {}
        self.compiled_js = False

        logging("Initiating Firefox...", LOG_INFO)
        if config[LOCATION_FIREFOX_DRIVER] != "":
            s = FirefoxService(config[LOCATION_FIREFOX_DRIVER])
        else:
            s = FirefoxService()

        options = Options()
        if config[PROFILE_FIREFOX_BROWSER] != "":
            options.add_argument("-profile")
            options.add_argument(config[PROFILE_FIREFOX_BROWSER])
        self.driver = webdriver.Firefox(service=s, options=options)

        self.driver.request_interceptor = self._requ_interceptor
        self.driver.response_interceptor = self._resp_interceptor
        if config[DEFAULT_TIMEOUT_IN_SEC] > 0:
            self.driver.set_page_load_timeout(config[DEFAULT_TIMEOUT_IN_SEC])
        if config[BROWSER_CLEAN_SHEET_SETUP]:
            self.driver.delete_all_cookies()

        atexit.register(self.driver.close)

        ## Wait for startup to complete.
        time.sleep(1)
        logging("Firefox initialization complete.", LOG_INFO)

    def request_resource(self, linkpair : URLPair) -> Collection[Tuple[bytes, dict, str]]:
        """Request a resource.

        Parameters:
        -------------
        linkpair : URLPair
            The user supplied link and the link which has potentially added the https protocol.
        """
        if not self.compiled_js:
            self._last_minute_js_table_compile()
        link = linkpair.url
        logging_push_where("RequestJS.request_resource")
        logging(f"About to access {link}", LOG_INFO)
        self.reporter.report(link)
        del self.driver.requests
        try:
            self.driver.get(link)
        except TimeoutException:
            logging(f"Timeout Exception accessing {link}", LOG_WARNING)
        except:
            logging(f"Seems link there is a connection issue for {link}", LOG_ERROR)
            logging_pop_where()
            return [(b"", {}, linkpair.original_url)]

        ## Primarily for Ubuntu systems using the snap version of Firefox
        ## weird selenium-wire bug loading but not showing requests
        if len(self.driver.requests) == 0:
            logging("No requests visible. Refresh...")
            time.sleep(2)
            self.driver.refresh()
            if len(self.driver.requests) == 0:
                logging(f"Seems link there is a connection issue for {link}", LOG_ERROR)
                return [(b"", {}, linkpair.original_url)]

        ret = []
        for req in self.driver.requests:
            if req.response is None:
                logging(f"Internal problem: Dubious request {req.url}")
                continue

            if req.response.status_code == 304:
                # redirecting
                pass # can do some logging later but that will do for now
            elif req.response.status_code == 429:
                logging(f"Exceeding ratelimit for {link} and corresponding domain.", LOG_ERROR)
                # this means that the user has exceeded the rate that the
                # server officially wants to allow...
            elif req.response.status_code != 200:
                logging(f"Request error {req.response.status_code} accessing {req.url}")
                #ret.append((b"", {}, req.url))
            else: # 200, yes
                response = req.response
                # https://stackoverflow.com/questions/67306915/selenium-wire-response-object-way-to-get-response-body-as-string-rather-than-b
                res_entry = (
                    sw_decode(
                        req.response.body,
                        req.response.headers.get('Content-Encoding', 'identity')
                        ),
                    response.headers,
                    req.url
                    )
                ret.append(res_entry)
        logging_pop_where()
        return ret

    def _requ_interceptor(self, request):

        url = request.url
        # if url fetches from bad source, it will abort no matter what
        # if not is_allowed_url(url):
        #     #request.url = ""
        #     request.abort()
        #     return
        # print("PASS ", url)

        ## if it is a JS from source that is JS-blacklisted,
        ## it will not even request it

        a = refd_content_may_have_fileformat(url, "js")
        b = refd_content_may_have_fileformat(remove_args_from_url(url), "js")
        if a or b:
            ## note may have false negative: so content that is javascript
            ## but does not have .js ending may not be checked. Will be detected later
            if not self._allow_running_js(url):
                #request.url = ""
                request.abort()
                return
        

    def _resp_interceptor(self, request, response):
        ## just making sure that even if there is a request that slipped
        ## through the request_interceptor by concealing the file type using
        ## an un/misinformative url does not get its code executed.
        url = request.url
        if response.headers is None:
            logging(f"NONE HEADERS {request.url}")
            return
        # if not is_allowed_url(url):
        #     response.headers["content-length"] = 0
        #     response.headers.set_payload(b"")
        #     response.body = b""
        #     return

        if response.headers["content-type"] is None:
            logging(f"No content type {request.url}")
            a = refd_content_may_have_fileformat(url, "js")
            b = refd_content_may_have_fileformat(remove_args_from_url(url), "js")
            if a or b:
            ## note may have false negative: so content that is javascript
            ## but does not have .js ending may not be checked. Will be detected later
                if not self._allow_running_js(url):
                    logging(f"DROPPING js disallowed {request.url}")
                    response.headers["content-length"] = 0
                    response.headers["Content-Length"] = 0
                    response.headers.set_payload(b"")
                    response.body = b""
                    return
            return
        if "javascript" in response.headers["content-type"]:
            if not self._allow_running_js(request.url):
                logging(f"DROPPING js disallowed {request.url}")
                response.headers["content-length"] = 0
                response.headers["Content-Length"] = 0
                response.headers.set_payload(b"")
                response.body = b""
                return
        ## made it through thus report should know
        self.reporter.report(url)
        return
        ## sometimes fetching from the url is fine but the user still
        ## does not want to execute Javascript from that source.
        ## enable that by stripping out all <script> tags.
        ## however, in some occasions we may strip out content e.g. code visible to the viewer
        ## TODO find out whether this strips out stuff that shouldn't
        ## if "html" in response.headers["content-type"]:
        ##     if not self._allow_running_js(request.url):
        ##         self._strip_script_out(response)

    def _strip_script_out(self, response):
        s = response.body
        bsp = BeautifulSoup(s, 'html.parser')
        ## src empty indicating inlined Javascript
        ## anything else is controlled by ooutgoing request filtering
        ## TODO this can be tricked by setting src=' ' or some other nonpath string.
        ## thus as a remedy ALL will be stripped for now.
        for node in bsp.find_all('script'):
            node.extract()
        response.body = bsp.prettify()

    def _last_minute_js_table_compile(self):
        """Compile the js allowed table right before the run."""
        self.compiled_js = True
        for (key, is_trusted) in javascript_checklist.items():
            if key == "*":
                continue
            k = r"(.*\.)*" + key
            self.js_checktable[re.compile(k)] = is_trusted

    def _allow_running_js(self, url):

        for (key, is_trusted) in self.js_checktable.items():
            if re.search(key, url):
                return is_trusted == TRUSTED
        return javascript_checklist["*"] == TRUSTED
