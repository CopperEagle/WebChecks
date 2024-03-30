"""Provides the RobotsFile class which manages robots.txt files for any domain required."""

import os
import re
from functools import partial
from typing import List, Callable

from webchecks.archive.GlobalCache import GlobalCache, DURATION_DAY
from webchecks.utils.url import extract_local_path_without_args, extract_fully_qualified_domain_name
from webchecks.config import config, UNGUIDED_ACCESS_POLICY, LOG_ERROR, AGENT_NAME, LOG_INFO
from webchecks.utils.messaging import logging



class RobotsFile:
    """Class that manages Robots.txt file. Provides the check_robots_txt method
    that allows to check if a given link is allowed to be accessed by the policy."""

    def __init__(self):
        self.globalcache = GlobalCache() # this is a singleton
        self.robots_txt_hashes = {}
        self.rules = {}

    def check_robots_txt(self, link : str, gateway) -> bool:
        """For a given link, return whether it is allowed.

        Parameters:
        -------------
        link : str
            The URL in question.
        gateway : 
            The gateway to potentially request accessing the robots.txt file. 
            The latter will be cached for a week."""
        domain = extract_fully_qualified_domain_name(link)
        path = extract_local_path_without_args(link)

        if path == "/robots.txt": # allowed by tautological requirement
            return True

        # okay so we need to get the robots.txt file...
        filehash = self.globalcache.get_hash(domain, "robots.txt")
        recent_hash = self._get_hash(domain)
        if filehash == recent_hash: ## okay is still up to date
            return self.check_rules(self.rules[domain], path)
        if recent_hash == b"" and filehash is not None: # hash not None means okay still up to date
            logging(f"Successfully loaded cached robots.txt for domain {domain}.", LOG_INFO)
            self.robots_txt_hashes[domain] = filehash
            self.rules[domain] = self.parse_robotstxt(
                self.globalcache.load(domain, "robots.txt")[0]
                )
            return self.check_rules(self.rules[domain], path)

        # else the content is out of date.
        content, filehash = self._get_file(domain, gateway)
        self.robots_txt_hashes[domain] = filehash
        if content in ("", b""):
            logging(f"Failed to fetch robots.txt: {domain}. "
                "Applying unguided_access_policy.", LOG_ERROR)
            return config[UNGUIDED_ACCESS_POLICY] == "free"
        self.rules[domain] = self.parse_robotstxt(content)
        return self.check_rules(self.rules[domain], path)

    def _get_hash(self, domain):
        try:
            return self.robots_txt_hashes[domain]
        except KeyError:
            self.robots_txt_hashes[domain] = b''
            return b''


    def _get_file(self, domain : str, gateway):
        robolink = os.path.join(domain, "robots.txt")
        content = gateway.express_request(robolink)[0].decode("utf-8")
        if len(content) == 0:
            return "", 0
        filehash = self.globalcache.store(domain, content, "robots.txt", DURATION_DAY)
        return (content, filehash)

    def parse_robotstxt(self, content : str) -> List[Callable[str, bool]]:
        """Parse the robots.txt file. Returns a list of functions that take some
        URL and return True of False. Use check_rules to use effectively.

        Parameters:
        -------------
        content : str
            The content of the robots file.
        """

        file = content.split("\n")
        agent = None
        rules = []

        for line in file:
            line = line.strip() # remove leading and trailing whitespace
            line = line.replace(" ", "").replace("\t", "")

            if line.startswith("#"): # comment
                continue

            if "#" in line:
                line = line.split("#")[0]

            if line.startswith("User-agent:"): # agent declaration
                agent = line.split(":")[1].strip()
                continue

            # relevant allow clause
            if agent in ("*", config[AGENT_NAME]) and line.startswith("Allow:"):
                rl = line.split(":")[1].strip()
                if rl == "":
                    continue
                rl = rl.replace("*", "(.*)") # get it into re form
                if rl.endswith("/"): # implicit wildcard made explicit
                    rl = rl + ".*"
                def check(s, rule):
                    if re.match(rule, s):
                        return True, "!"
                    return True, ""
                rules.append(partial(check, rule = re.compile(rl)))

            # relevant disallow clause
            if agent in ("*", config[AGENT_NAME]) and line.startswith("Disallow:"):
                rl = line.split(":")[1].strip()
                if rl == "":
                    continue
                rl = rl.replace("*", "(.*)")
                if rl.endswith("/"):
                    rl = rl + ".*"
                def check(s, rule):
                    if re.match(rule, s):
                        return False, "!"
                    return True, ""
                rules.append(partial(check, rule = re.compile(rl)))

        return rules

    def check_rules(self, rules : List[Callable[str, bool]], link : str,
            is_full_url : bool = False) -> bool:
        """Check if the robots.txt rules allow a URL given
        the return from parse_robots_txt.

        Parameters:
        -------------
        rules : List of functions
            The output from the parsing run.
        link : str
            The url in question.
        is_full_url : str
            Is the URL given a full URL or has the domain name already been removed?
        """

        if is_full_url:
            link = extract_local_path_without_args(link)
        res = True
        for rule in rules:
            l = rule(link)
            res &= l[0]
            if l[1] == "!":
                res = l[0]
        return res
