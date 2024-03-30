"""Provides the BaseProfile class."""

import time
from typing import Collection, Union
from functools import partial
from random import expovariate


from bs4 import BeautifulSoup

from webchecks.archive.FileArchive import FileArchive
from webchecks.utils.Error import OptionsError
from webchecks.utils.check import input_check
from webchecks.utils.url import url_is_local,url_is_superlocal, url_is_referencial,\
  merge_url, extract_fully_qualified_domain_name, merge_ref_url, strip_query_from_url
from webchecks.utils.messaging import logging

# pylint: disable=wildcard-import
from webchecks.config import *
from .ProfileConstants import *



class BaseProfile:
    """
    Base profile. It provides reasonable defaults for the header fields, access frequency and
        a set of default processing algorithms.

    What does a profile do:

    #1 Specify the access pattern: In what frequency the website will be requested and whether
        the access timings should be randomized to some extent.

    #2 Specify the exact form that the request headers should have when accessing the page.

    #3 For a given result comming from that very request, what exactly should be done?
        To serve common storage needs, profiles can use classes from the Archive
        module to store and manage the data.

    #4 For given result, provided that the result is a html webpage, find and provide further
        links that should be accessed.
    """
    def __init__(self, domain):
        logging(f"Create profile {domain}")
        self.domain = domain

        self.headers = {
            "User-Agent": config[USER_AGENT],
            "Accept": "text/html,application/xhtml+xml,application/xml;"
            			"q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            #"Referer": self.domain,
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "TE": "trailers"
            }
        self._set_access_algorithm(ACCESS_EXPONENTIAL_RND_MIN, config[ACCESS_DEFAULT_INTERVAL],
            config[ACCESS_DEFAULT_MIN_WAIT])
        self._access_pattern_is_default = True

        self.archive = FileArchive(self)

        self.links_visited = self.archive.load_links_visited()
        self.waiting_links = set([])

        self.archive.save_at_shutdown(self._get_links_visited)

    def quiet_exit(self):
        """Disables exiting functions that do backup and print some things.
        DO NOT USE THIS UNLESS YOU REALLY KNOW WHAT YOU ARE DOING.
        It may CORRUPT the project if improperly used."""
        self.archive.quiet_exit()


    def get_domain(self) -> str:
        """Get the domain name."""
        return self.domain

    def get_wait_time(self) -> Union[None, int, float]: # pylint: disable=method-hidden
        """Returns the wait time between the current and next request in seconds.
        WILL BE OVERRIDDEN once the access algorithm is set."""
        return

    def update_access_pattern(self):
        """Call if default average/minimum wait between accesses to same domain is changed."""
        if self._access_pattern_is_default:
            self._set_access_algorithm(
                ACCESS_EXPONENTIAL_RND_MIN,
                config[ACCESS_DEFAULT_INTERVAL],
                config[ACCESS_DEFAULT_MIN_WAIT]
            )
            self._access_pattern_is_default = True


    def get_headers(self):
        """Get default http request header. Does not include cookies."""
        return self.headers

    def get_archive(self):
        """Returns the FileArchive Object that manages this domains 
        subdirectory in the project directory."""
        return self.archive

    def get_urls_visited(self):
        """Get list of visited URLs for the given domain."""
        return self.links_visited


    def get_links(self, url : str, html_source : str) -> Collection[str]:
        """Given some webpage, it fetches the links that are on
        the webpage. This default implementation fetches ALL links.
        Per-profile specialisations may choose to return only some links.
        
        Note that all links will be subjected to security policy filtering
        which will be enforced by the gateway.
        
        Also note that it will not return links that have already been visited or
        are already in the waiting queue.

        Parameters:
        -------------
        url : str
            The url of that content. Useful for local links on that page.
        html_source : str
            The page to be analyzed.
        """
        html_soup = BeautifulSoup(html_source, 'html.parser')
        links = []
        atags = html_soup.find_all("a")
        for tag in atags:
            link = tag.get("href")
            if link in (None, ""):
                continue
            if url_is_superlocal(link): ## means it just copies the protocol '//newpage.com'
                link = link.replace("//", "")
            elif url_is_referencial(link):
                localref = url.split("#")[0]
                link = merge_ref_url(localref, link)
                continue
            elif url_is_local(link):
            	# rather than self.domain
                link = merge_url(extract_fully_qualified_domain_name(url), link)
            links.append(link)

        return self._register_urls(links)

    def consume_retreived_content(self, url : str, resp_header : dict, content : bytes):
        """After a webaccess happened, this function is called. The main purpose is to
        process the data and store it.
        """
        if content in (b"", ""):
            self._deregister_url(url)
            return

        metadata = f"Retrived {time.asctime()}\nURL {url}"
        self.archive.save_content(url, resp_header, content, metadata) # returns filename
        self._deregister_url(url)

    def _get_links_visited(self):
        return self.links_visited

    def _modify_header(self, field : str, value : str):
        """Insert another field into the http request header. 
        If value is None, then the field will be deleted."""
        if value is None:
            try:
                del self.headers[field]
            except KeyError:
                pass
            return

        self.headers[field] = value

    def _set_access_algorithm(self, algorithm, avg_wait_time : float = 1,
    		min_wait_time : float = 0.1) -> None:
        """Set the access algorithm that steers at what interval 
        this domain is being accessed. 

        Parameters:
        ------------
        algorithm: Option from profiles/ProfileConstants: 
            ACCESS_EXPONENTIAL_RND_MIN: Ensures that while random,
            	the wait time has at least some minimum.
            ACCESS_EXPONENTIAL_RND: Exponential distribution with 
            	given average. Randomized, more unpredictable.
            ACCESS_EXPONENTIAL_RND_MIN: Ensures that while random, 
            	the wait time has at least some minimum.
        
        avg_wait_time: int or float
        	Average wait time. Must be greater than 0
        min_wait_time: int or float
        	Min wait time. Ignored unless algorithm is ACCESS_EXPONENTIAL_RND_MIN
        """
        input_check(avg_wait_time > 0, "avg_wait_time > 0")
        self._access_pattern_is_default = False

        if algorithm == ACCESS_EQUISPACED:
            self.get_wait_time = self._get_wait_time_equispaced

        elif algorithm == ACCESS_EXPONENTIAL_RND:
            self.get_wait_time = partial(
            	self._get_wait_time_equispaced_rnd,
            	avg_wait_time = avg_wait_time
            	)

        elif algorithm == ACCESS_EXPONENTIAL_RND_MIN:
            self.get_wait_time = partial(
            	self._get_wait_time_equispaced_rnd_min,
            	avg_wait_time = avg_wait_time,
                min_wait_time = min_wait_time
                )

        else:
            raise OptionsError("algorithm",
            		(
            			"ACCESS_EQUISPACED",
            			"ACCESS_EXPONENTIAL_RND", 
                		"ACCESS_EXPONENTIAL_RND_MIN"
                	)
                )

    def _get_wait_time_equispaced(self, avg_wait_time : float = 1) -> float:
        return avg_wait_time

    def _get_wait_time_equispaced_rnd(self, avg_wait_time : float = 1) -> float:
        return expovariate(1.0/avg_wait_time)

    def _get_wait_time_equispaced_rnd_min(self, avg_wait_time : float = 1,
    		min_wait_time : float = 0.1) -> float:
        return max(min_wait_time, expovariate(1.0/avg_wait_time))

    def _deregister_url(self, url : str):
        """Should be called after the link was accessed by the gateway to tell it
        that this link is no longer in the waiting position. Depending on the policy
        this may start a timer after which this URL may be reaccessible."""
        self.links_visited.add(strip_query_from_url(url))
        try:
            self.waiting_links.remove(url)
        except KeyError:
            pass # seed_urls are not stored here.

    def _register_urls(self, urls : Collection[str]):
        """Any potentially accessed link must be registered before submitted
        to the gateway. This filters links that should not be revisited.
        It seperately also filters links that are currently in the gateway pipeline.
        The default policy does not allow any reaccessing which may be too restrictive
        for some applications."""
        urls = list(set(urls))
        ## avoid requeries within set TODO make this optional
        for i in range(len(urls) - 1, -1, -1):
            for j in range(i - 1, -1, -1):
                try:
                    link1 = urls[i]
                    link2 = urls[j]
                except IndexError: ## too many deletions
                    break
                if self.__match(strip_query_from_url(link1), strip_query_from_url(link2)):
                    del urls[i]

        links = set(urls)
        links = (links - self.links_visited) - self.waiting_links # visit only new pages
        urls = set([])
        for link in links:
            if self._not_redundant_url(link):
                urls.add(link)
        self.waiting_links |= urls

        return list(urls)

    def _not_redundant_url(self, url):
        """Decides whether the link has already been accessed or is at least
        inside the gateway pipeline.

        Note that the query inside a link will be ignored to determine equality."""
        # For now a poor mans way... the thing is also that
        # sometimes a query can make a big difference...
        url = strip_query_from_url(url)
        for link in self.waiting_links:
            if self.__match(strip_query_from_url(link), url):
                return False

        for link in self.links_visited:
            if self.__match(link, url):
                return False
        return True

    def __match(self, s, t):
        if s == t or s[:-1] == t or s == t[:-1]:
            return True
        return False
