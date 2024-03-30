"""Provides the RequestNoJS class which sends requests without any realtime
rendering of the result, thus not executing (or even requesting) Javascript."""

from typing import Tuple, Collection

import requests

from webchecks.profiles.profileDB import fetch_profile
from webchecks.monitor.Report import Report
from webchecks.utils.url import extract_domain
from webchecks.utils.messaging import logging, logging_push_where, logging_pop_where

from webchecks.config import config, DEFAULT_TIMEOUT_IN_SEC, LOG_ERROR, LOG_INFO




class RequestNoJS: # pragma: no cover
    """Sessionmanager for the NonJS requests."""

    def __init__(self):
        self.sessions = {}
        self.reporter = Report() # pylint: disable=no-value-for-parameter

    def _get_session(self, domain : str):
        """Get a session for a given domain."""
        try:
            return self.sessions[domain]
        except KeyError:
            s = requests.Session()
            profile = fetch_profile(domain)
            s.headers.update(profile.get_headers())
            self.sessions[domain] = s
            return s

    def request_resource(self, linkpair) -> Collection[Tuple[bytes, dict, str]]:
        """Request a resource. Returns a list containing the 
        response content in bytes, the response header and the original URL provided by the user.

        Parameters:
        ------------
        linkpair : URLPair
            A linkpair object containing the URL to request and the URL originally entered by the 
            user. Remember they may be different as the Gateway may have needed to add the protocol.
        """
        link = linkpair.url
        domain = extract_domain(link)
        session = self._get_session(domain)
        logging_push_where("RequestNoJS.request_resource")
        logging(f"About to access {link}", LOG_INFO)
        #log_link(link)
        self.reporter.report(link)
        try:
            if config[DEFAULT_TIMEOUT_IN_SEC] > 0:
                response = session.get(link, timeout = config[DEFAULT_TIMEOUT_IN_SEC])
            else:
                response = session.get(link)
            #logging(f"{response.request.headers}")
        except:
            logging(f"Seems link there is a connection issue for {link}", LOG_ERROR)
            logging_pop_where()
            return [(b"", {}, linkpair.original_url)]

        if response.status_code//100 != 2: # status not 20x
            logging(f"Request error {response.status_code} accessing {link}", LOG_INFO)
            logging_pop_where()
            return [(b"", {}, linkpair.original_url)]

        logging_pop_where()
        return [(response.content, response.headers, linkpair.original_url)]
