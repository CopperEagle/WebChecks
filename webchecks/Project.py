"""This module provides the Project class, the main interface to the user."""
import os
import atexit
from typing import Type, Union, Collection, Callable

from webchecks.access import AccessHead, Gateway
from webchecks.profiles.BaseProfile import BaseProfile
from webchecks.profiles.profileDB import add_profile, profiledb
from webchecks.monitor.Report import Report
from webchecks.archive.AccessNode import AccessNode
from webchecks.utils.messaging import logging, LOG_INFO, LOG_WARNING, LOG_ERROR

# almost all constants and we need many of them
# pylint: disable-next=wildcard-import
from webchecks.config import *

class Project:
    """
    The main interface to the user. All options are changed through this interface.
    No options are permanently stored (for now).
    """
    # pylint is confused by the re expressions in the docstrings...
    # pylint: disable=anomalous-backslash-in-string

    def __init__(self, project_root : str, initial_seed_urls : Union[str, Collection[str]]):
        """
        Constructor.

        Parameters
        ---------
        project_root : str
            Name of the project. It will create a directory with that same name.
        initial_seed_urls : str or list of str
            Initial URLs to begin with
        """
        logging(F"Starting up project with root {project_root}", LOG_INFO)
        if project_root in ("", "."):
            raise ValueError("Project root must contain at least one letter... "
                "and better don't start it with a '.'.")
        self.root = project_root
        if isinstance(initial_seed_urls, str):
            self.initial_seed_urls = (initial_seed_urls,)
        elif type(initial_seed_urls) in (tuple, list):
            self.initial_seed_urls = initial_seed_urls
        else:
            raise ValueError("Type of initial_seed_urls should be str or list of str")
        self.open = open
        self.initial_seed_urls = initial_seed_urls
        self.keywords = None
        self.profiles = []
        self.reporter = Report(project_root, project_root, initial_seed_urls)
        self._setup()
        self.acc_node = AccessNode()
        atexit.register(self.__report)

    def quiet_exit(self):
        """Disables exiting functions that do backup and print some things.
        May diable automatic saving mechanisms, among other things.
        DO NOT USE THIS UNLESS YOU REALLY KNOW WHAT YOU ARE DOING.
        It may CORRUPT the project if improperly used.
        """
        atexit.unregister(self.__report)
        for _, profile in profiledb.items():
            profile.quiet_exit()

    def seek(self, keywords = None): # pylint: disable=unused-argument
        """Not yet implemented. Ignore."""
        logging("Keywords are not yet properly implemented. WILL BE IGNORED.", LOG_ERROR)
        #  still needs some work
        # if not type(keywords) == tuple:
        #     raise ValueError("Keywords must be tuple.")
        # if len(keywords) == 0:
        #     keywords = None
        # else:
        #     for i in range(len(keywords)):
        #         if not type(keywords[i]) == str:
        #             raise ValueError("Keywords must be tuple of strings.")
        # self.keywords = keywords
        # self.reporter.setup(keywords)

    # pylint: disable-next=unused-argument
    def add_content_handler(self, handler : Callable[[str, dict, bytes], None]):
        """Not implemented yet. Ignore."""
        return

    def access_node(self) -> Type[AccessNode]:
        """Get the interface through which to access all content that was accessed."""
        return self.acc_node

    def _setup(self):
        logging("Initializing project")
        try:
            os.mkdir(self.root)
        except:
            pass
        config[RESULT_STORAGE_LOCATION] = os.path.join(self.root, config[RESULT_STORAGE_LOCATION])
        config[CACHE_STORAGE_LOCATION] = os.path.join(self.root, config[CACHE_STORAGE_LOCATION])
        try:
            os.mkdir(config[RESULT_STORAGE_LOCATION])
        except:
            logging(f"Mkdir for {config[RESULT_STORAGE_LOCATION]} failed."
                " May exist already or missing permissions.", LOG_INFO)
            for domain in os.listdir(config[RESULT_STORAGE_LOCATION]):
                if domain == ".cache":
                    continue
                add_profile(BaseProfile(domain))

        logging("Finished initializing")

    def __report(self):
        s = self.reporter.print()
        with self.open(os.path.join(self.root, "REPORT.txt"), "w") as f:
            f.write(s)
        print(s)

    def run(self, n_seconds : int):
        """Crawl for the specified amount of seconds.
        Note that it is a rough estimate. It will still finish the current access
        before terminating.

        Parameters
        ---------
        n_seconds : int
            Number of seconds to crawl.
        """

        gateway = Gateway.GateWay() # new Gateway, in case of multiple runs...
        accesshead = AccessHead.AccessHead(self.initial_seed_urls)
        accesshead.run(gateway, n_seconds)

    def enable_javascript(self, enable : bool):
        """Enable Javascript. This requires Seleniumwire. 

        Parameters
        ---------
        enable : bool
            Boolean value whether to enable javascript. Default value is False.
        """
        config[ENABLE_JAVASCRIPT] = enable

    def enable_crawl(self, enable : bool):
        """Whether to visit links found in retreived HTML pages. By default, 
        it is enabled. If false, then only the seed URLs are visited.

        Parameters
        ---------
        enable : bool
            Boolean value whether to enable crawling.
            Default value is True.
        """
        config[DO_CRAWL] = enable

    def set_timeout(self, timeout_s : int):
        """Set the timeout value in seconds.
        

        Parameters
        ---------
        timeout_s : int
            Number of seconds before the access is interrupted.
            Default value is 20 seconds.
        """
        config[DEFAULT_TIMEOUT_IN_SEC] = timeout_s

    def sec_set_allowed_websites(self, whitelisted_domains : Collection[str]):
        """Part of the security policy.
        
        Set the whitelisted websites that are allowed to be visited.
        The argument is a list of regular expressions for the domains allowed.
        Example:

            proj.set_allowed_websites((r"(.*\.)?wikipedia\.org",))
        Allowing all wikipedia pages, regardless of language (like en.wikipedia.org).
        Note that if the prefix r'(.*\.)?' was omitted then subdomains would not be allowed.

        By default, this list is empty and ignored (i.e. all websites are allowed by default).

        Parameters
        ---------
        whitelisted_domains : Collection of str
            Set of domains that can be visited.
        """
        config[WHITELISTED_DOMAINS_ONLY] = True
        config[WHITELIST_DOMAINS] = whitelisted_domains

    def sec_allow_all_websites(self):
        """Part of the security policy.

        This resets all security policies to basically zero guardrails.
        Will warn the user when doing so to help debugging.
        """
        logging("Resetting all security guards. Make sure this is not a bug.", LOG_WARNING)
        config[WHITELISTED_DOMAINS_ONLY] = False
        config[WHITELISTED_TLD_ONLY] = False
        config[ENABLE_BLINDLY_TRUSTED_TLD] = False
        config[ALLOW_REDIRECT] = True
        config[WHITELISTED_TLD_ONLY] = []
        config[WHITELIST_DOMAINS] = []
        config[BLINDLY_TRUSTED_TLD] = []

    def sec_whitelisted_tld_only(self, whitelisted_tld : Collection[str]):
        """Part of the security policy.

        Require that any domain allowed must have this TLD ('.com', etc.) unless
        they have a TLD that is blindly trusted. (see sec_blindly_trusted_tld)
        This sets an additional requirement for the domains that you want to allow.

        Parameters
        ---------
        whitelisted_tld : Collection of str
            Set of TLDs that are allowed.
            Default value is empty list and ignored. Note: Omit the '.'
        """
        config[WHITELISTED_TLD_ONLY] = True
        config[WHITELIST_TLD] = whitelisted_tld

    def sec_blindly_trusted_tld(self, blindly_trusted_tlds : Collection[str]):
        """Part of the security policy.

        Pass a list of TLDs (for example 'edu', ...) that automatically allow
        websites with this TLD to be visited. Note that for these domains, 
        no other security policy can disallow these. On the other hand, this
        does not blacklist any domain per se.
        NOTE: Omit the '.'

        Parameters
        ---------
        blindly_trusted_tlds : Collection of str
            Set of tlds for which any domain with this tld is immediately trusted.
            Default value is empty list and ignored.
        """
        config[ENABLE_BLINDLY_TRUSTED_TLD] = True
        config[BLINDLY_TRUSTED_TLD] = blindly_trusted_tlds

    def sec_single_domain_only(self, single_domain_only : str):
        """Part of the security policy.

        Redundant and deprecated feature. Use sec_set_allowed_websites instead.
        """
        logging("sec_single_domain_only is deprecated. Use sec_set_allowed_websites", LOG_WARNING)
        config[SINGLE_DOMAIN_ONLY] = single_domain_only

    def sec_allow_generic_redirect(self, allow_redirect : bool):
        """Part of the security policy.
        
        If False, it will try to avoid generic redirects. (best efforts for now).
        A generic redirect is when the link has another target link in its argument.
        The layout usually is such that it may allow any redirect. Example:
        
        https://site.com/login?ssrc=head&returnurl=https%3a%2f%2fbadsite.com%2f

        This link would not be fallowed if set to False.

        Parameters
        ---------
        allow_redirect : bool
            Boolean value whether to allow generic (URL driven) redirect. Default value is False.
        """
        config[ALLOW_REDIRECT] = allow_redirect

    def set_compress_text(self, compress_text : bool):
        """Specify whether html results should be compressed if they are stored.

        Parameters
        ---------
        compress_text : bool
            Whether to do compression. Default value is True.
        """
        config[COMPRESS_CONTENT] = compress_text

    def install_profile(self, profile : Type[BaseProfile]):
        """Install the user defined profile that you have written.
        Currently this will not remember the profile after shutdown.
        Thus you need to pass it on everytime you run your script. May change somewhen,
        but that will probably just copy your code into the project folder."""
        if profile.domain in profiledb:
            # Only one can execute the shutdown functionality.
            profiledb[profile.domain].quiet_exit() 
        add_profile(profile)

    def set_logging_level(self, log_level : int):
        """Set the logging level.

        Parameters
        ---------
        log_level : int
            One of LOG_DEBUG, LOG_INFO, LOG_WARNING, LOG_ERROR from webchecks.utils.constants
        """
        if log_level not in (LOG_DEBUG, LOG_INFO, LOG_WARNING, LOG_ERROR):
            raise ValueError(
                f"log_level should be one of {(LOG_DEBUG, LOG_INFO, LOG_WARNING, LOG_ERROR)}"
                ", being LOG_DEBUG, LOG_INFO, LOG_WARNING, LOG_ERROR constants in utils.constants.")
        config[LOGGING_LEVEL] = log_level

    def set_browser_driver_location(self, path : str):
        """If you enable Javascript: Can specify the location of your browser driver that
        selenium can use. Note that as far as I know, you usually don't need to specify it.
        Sometimes it is still useful. (Like in snap environments, etc.)

        Parameters
        ---------
        path : str
            Path to driver. Default value is empty string.

        """
        config[LOCATION_FIREFOX_DRIVER] = path

    def set_browser_use_profile(self, path : str):
        """If you enable Javascript: Can specify the location of the used profile.
        Note that you usually do not need to specify this - unless you are on Ubuntu, 
        and install your browsers using snap. (-> profiles are somewhere in ~/snap 
        directory)

        Parameters
        ---------
        log level : int
            One of LOG_DEBUG, LOG_INFO, LOG_WARNING, LOG_ERROR from webchecks.utils.constants
            Default value is empty string.
        """
        config[PROFILE_FIREFOX_BROWSER] = path

    def sec_set_allow_javascript_for_domain(self, domain : str):
        """Set this domain to be allowed. If '*', then by default domains are trusted
        unless explicitly blacklisted using sec_set_disallow_javascript_for_domain.

        Parameters
        ---------
        domain : str
            Allow that domain to execute Javascript.
            Default value is all domains are trusted given JS is enabled.
        """
        javascript_checklist[domain] = TRUSTED

    def sec_set_disallow_javascript_for_domain(self, domain : str):
        """Set this domain to be disllowed. If '*', then by default domains are NOT trusted
        unless explicitly whitelisted using sec_set_allow_javascript_for_domain.

        Parameters
        ---------
        domain : str
            Disallow that domain to execute Javascript.
            Default value is all domains are trusted given JS is enabled.
        """
        javascript_checklist[domain] = UNTRUSTED

    def sec_reset_javascript_permissions_for_domains(self):
        """Reset the table for Javascript allowanes. Note: By default this allows all!"""
        javascript_checklist.clear()
        javascript_checklist["*"] = TRUSTED

    def sec_enforce_https(self, enforce_https : bool):
        """Make sure that any requested link always uses the HTTPS (encrypted) protocol.

        Parameters
        ---------
        enforce_https : bool
            Whether to ensure any link accessed uses an encrypted connection over the web.
            By default this is True.
        """
        config[ENFORCE_HTTPS] = enforce_https

    def set_min_wait(self, min_wait : int):
        """Minimum wait time between two accesses to the same domain.

        Parameters
        ---------
        min_wait : int
            Number if seconds. Default value is 20 seconds.
        """
        config[ACCESS_DEFAULT_MIN_WAIT] = min_wait
        for (_, profile) in profiledb.items():
            profile.update_access_pattern()

    def set_avg_wait(self, avg_wait : int):
        """Average wait time between two accesses to the same domain.

        Parameters
        ---------
        avg_wait : int
            Number if seconds. Default value is 25 seconds.
        """
        config[ACCESS_DEFAULT_INTERVAL] = avg_wait
        for (_, profile) in profiledb.items():
            profile.update_access_pattern()
