"""This module provides the AccessHead class."""

import time
from typing import Union, Set

from webchecks.access.Gateway import GateWay
from webchecks.profiles.profileDB import fetch_profile
from webchecks.utils.url import extract_fully_qualified_domain_name
from webchecks.utils.file_ops import get_file_type_from_response_header
from webchecks.utils.messaging import logging
from webchecks.config import config, LOG_INFO, DO_CRAWL


class AccessHead:
    """Accesshead maintains the run and initiates accesses."""
    def __init__(self, initial_seed_urls):
        self.gateway = None
        self.initial_seed_urls = \
            [initial_seed_urls] if isinstance(initial_seed_urls, str) else initial_seed_urls

    def run(self, gateway : GateWay, max_time_s : Union[int, float] = 1000): # pragma: no cover
        """Main loop. Does the run for the specified number of seconds.

        Parameters:
        -------------
        gateway : GateWay
            The gateway to sends requests to.
        max_time_s : int or float
            The number of seconds to do the run.
        """

        self.gateway = gateway
        for url in self.initial_seed_urls:
            if not gateway.add_to_queue(url):
                raise ValueError(
                	f"REJECTED initial seed {url}. Conflicting security policy likely "
					"the case. See log for more info. If you need more information, "
					"you may change LOGGING_LEVEL."
				)

        start_timestamp = time.time()
        while True:

            links = []
            for content, resp_header, link in gateway.process_queue():
                domain = extract_fully_qualified_domain_name(link)
                profile = fetch_profile(domain)
                profile.consume_retreived_content(link, resp_header, content)
                links += self.fetch_links(content, resp_header, link) ## seeking links...

            for sublink in links:
                gateway.add_to_queue(sublink)

            if gateway.done():
                logging("Done: No more links to process. Early terminating.", LOG_INFO)
                break

            if time.time() - start_timestamp >= max_time_s:
                logging("Maximum time reached. Aborting the process.", LOG_INFO)
                break
            time.sleep(0.1)


    def fetch_links(self, text : bytes, resp_header : dict, link: str) -> Set[str]:
        """Get links to enter next given a finished request.

        Parameters:
        --------------
        text : bytes
            The data of the response.
        resp_header : dict
            The header of the response.
        link : str
            The original link corresponding to this response.
        """
        if not config[DO_CRAWL]:
            return []
        if len(text) == 0:
            return []
        # fetching further links currently only supported from html files.
        if get_file_type_from_response_header(resp_header)[1] != ".html":
            return []
        if isinstance(text, bytes):
            text = text.decode("utf-8") # to str

        profile = fetch_profile(extract_fully_qualified_domain_name(link))

        return profile.get_links(link, text)
