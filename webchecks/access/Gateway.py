"""Provides the Gateway class. It does all access filtering, implementing the security policy."""

import time
from typing import Tuple, Collection

from webchecks.profiles.profileDB import fetch_profile
from webchecks.utils.url import extract_fully_qualified_domain_name, \
	change_protocol, is_url, extract_protocol
from webchecks.utils.timedqueue import TimedQueue
from webchecks.utils.messaging import logging, log_link
from webchecks.config import config, ENABLE_JAVASCRIPT, LOG_INFO, LOG_ERROR, \
	LOG_DEBUG, ENFORCE_HTTPS

from .security import is_allowed_url
from .RequestNoJS import RequestNoJS
from .RobotsFile import RobotsFile

class URLPair:
    """Pair of URLs."""
    def __init__(self, original_url, url):
        self.url = url
        self.original_url = original_url



class GateWay:
    """ Main Gateway that sends all requests. It does so while fulfilling
    requirements about frequency of requests and appearance of the requests.

    Requests are always evenly distributed over time to avoid bursty traffic,
    they are checked and restricted (as much as possible, given the security policy).

    If enforce_https is true, it will ensure any link accessed uses the https protocol.
    """


    def __init__(self):
        self.queue = TimedQueue()
        self.robotsfile = RobotsFile()
        if not config[ENABLE_JAVASCRIPT]:
            logging("Javascript is disabled.", LOG_INFO)
            self.sender = RequestNoJS()
        else:
            logging("Javascript is enabled.", LOG_INFO)
            from .RequestJS import RequestJS
            # only here import to make selenium-wire install optional
            self.sender = RequestJS()

    def add_to_queue(self, link : str) -> bool:
        """Add link to queue. If fix_link it will look at the link and sanitize it.
        Will additionally perform checks to see whether the link points to the correct domain.
        Returns true if the URL link was accepted and added.

        Parameters:
        -------------
        link : str
            The link to be requested in the future.
        """

        original_url = link # we may modify the link here.. However, we mask this to the outside
        if not self._verify_is_url(link):
            return False

        link = self._ensure_https_protocol(link)

        if not self._permitted_link(link):
            logging(f"Link not permitted. Not adding to sending queue: {link}", LOG_DEBUG)
            return False

        domain = extract_fully_qualified_domain_name(link)
        profile = fetch_profile(domain)
        self.queue.enqueue(domain, URLPair(original_url, link),
            profile.get_wait_time(), time.time())
        logging(f"Added to queue {link}")
        return True

    def process_queue(self) -> Tuple[bytes, dict, str]: # pragma: no cover
        """Generator that processes the link queue. Does not sleep. 
        Given that links have a dont-use-before-date this means the behaviour
        is dependent on WHEN this generator is called. This call may not process 
        anything in one instance but a second later it may do so.
        
        Yields (retreived_content, response_header, link)."""

        elt = self.queue.dequeue(time.time())
        while elt is not None:
            responses = self._request_resource(elt)
            yield from responses
            elt = self.queue.dequeue(time.time())

    def done(self) -> bool:
        """Returns true if there is nothing more to process."""
        return self.queue.isempty()

    def _request_resource(self, linkpair : str) -> Collection[Tuple[bytes, dict, str]]: # pragma: no cover
        link = linkpair.url
        log_link(link)
        return self.sender.request_resource(linkpair)

    def _verify_is_url(self, url: str) -> bool:
        """Verifies that the link has the format of a url."""
        if not is_url(url):
            logging(f"Rejecting link because it does not seem to be an url: {url}")
            return False
        return True

    def _ensure_https_protocol(self, url: str) -> str:
        """Ensures that the link uses the https protocol."""

        protocol = extract_protocol(url)
        link = url
        if protocol == "":
            return change_protocol("https", url)

        if protocol != "https" and config[ENFORCE_HTTPS]:
            link = change_protocol("https", url)
            #logging(f"Found link with non-https protocol {url}. Changed to {link}")
        return link

    def _permitted_link(self, link : str) -> bool:
        """Checks whether the security policy allows accessing this link.
        Furthermore it will check whether the robots.txt file allows it -
        provided that the profile specifies to do so."""
        if not is_allowed_url(link):
            logging(f"Not accessing url: Security policy disallows {link}", LOG_DEBUG)
            return False

        if not self.robotsfile.check_robots_txt(link, self):
            logging(f"Not accessing url: robots.txt policy disallows {link}", LOG_INFO)
            return False
        return True

    def express_request(self, link : str) -> Tuple[bytes, dict, str]: # pragma: no cover
        """Requests a SINGLE resource without putting the link into the queue.
        It will still check the link whether it satisfies the security policy
        but if it does, it will attempt to fetch it directly.
        This is soley used for the Robots.txt file.

        Parameters:
        -------------
        link : str
            The link to be requested.
        """

        original_url = link
        if not self._verify_is_url(link):
            return (b"", {}, original_url)

        link = self._ensure_https_protocol(link)

        if not self._permitted_link(link):
            logging(f"Link not permitted. Not allowing as express_request: {link}", LOG_DEBUG)
            return (b"", {}, original_url)

        ret = self._request_resource(URLPair(original_url, link))
        # now get single request corresponding to user request
        for req in ret:
            if req[2] in (original_url, link):
                return req
        # problem: redirects can change url arbitrarily... especially a problem with selenium
        # we want only one result... selenium may give many
        if len(ret) == 1:
            return ret[0]
        ## if robots.txt in there then 100% this is it
        for req in ret:
            if "robots.txt" in req[2]:
                return req
        logging("Express request failed, probably due to opaque redirect.", LOG_ERROR)
        return (b"", {}, original_url)
