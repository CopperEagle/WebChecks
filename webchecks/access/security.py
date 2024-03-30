"""Implements the checks of the security policy."""


import re
from urllib.parse import unquote

from webchecks.utils.url import is_legal_domain, is_legal_tld, extract_local_path_and_args, \
    is_url, extract_domain
from webchecks.utils.check import input_check
from webchecks.config import * # pylint: disable=wildcard-import



SUBLINK = re.compile(r"(([a-z]*)://)?(([a-zA-Z0-9\-]+\.)*)([a-zA-Z0-9\-]+)\.([a-z]+)(/.*)?")


def is_allowed_url(url : str) -> bool:
    """For a given url returns whether it is in the allowed_domains set/tuple/list.
    
    Expects that the format of the link is valid urlwhise.

    Parameters:
    -------------
    url: str
        The URL to be checked.

    Makes use of the fallowing settings in config:

    Configurations used:
    ------------------------
    WHITELISTED_DOMAINS_ONLY: 
        If true, will allow only expicitly allowed domains.
    WHITELISTED_TLD_ONLY: 
        If true, allow only urls with explicitly allowed tld.
    ENABLE_BLINDLY_TRUSTED_TLD: 
        If true, any website with blindly trusted tld will be trusted.
    ALLOW_REDIRECT: 
        If false, filters generic redirects (url specifing in its argument
        another destination that is not local to this link). Note this may not prevent
        a redirect initiated by the server (Error code).
    SINGLE_DOMAIN_ONLY: 
        If not None but a URL, then only URLs that have the 
        same domain are allowed.
    """

    whitelisted_domains_only = config[WHITELISTED_DOMAINS_ONLY]
    whitelisted_tld_only = config[WHITELISTED_TLD_ONLY]
    enable_blindly_trusted_tld = config[ENABLE_BLINDLY_TRUSTED_TLD]
    single_domain_only = config[SINGLE_DOMAIN_ONLY]
    allow_redirect = config[ALLOW_REDIRECT]

    res = True

    if single_domain_only:
        input_check(isinstance(single_domain_only, str),
        # and is_url(single_domain_only), allows re
        "security.py: Restricting to single domain requires single_domain_only to be "
        "the corresponding URL of that allowed domain.")
        res = is_legal_domain(url, (single_domain_only,))
        # extract_domain(single_domain_only) == extract_domain(url)

    ## TODO allow only explicitly allowed fileextensions

    ## allow only explicitly allowed websites
    if whitelisted_domains_only:
        res &= is_legal_domain(url, config[WHITELIST_DOMAINS])

    ## allow only explicitly allowed TLDs
    if whitelisted_tld_only:
        res &=  is_legal_tld(url, config[WHITELIST_TLD])
    ## prevent generic redirects. These may be created by any webuser using a comment functionality
    if not allow_redirect:
        res &= not is_generic_redirect(url)
    ## blindly trusted tlds
    if enable_blindly_trusted_tld and is_legal_tld(url, config[BLINDLY_TRUSTED_TLD]):
        res = True
    ## avoid explicitly forbidden tlds
    if is_legal_tld(url, config[BLACKLISTED_TLD]):
        res = False
    return res


def is_generic_redirect(url : str):
    """Detects generic redirects (url specifing in its argument
    another destination that is not local to this link). Note this may not prevent
    a redirect initiated by the server.

    Parameters:
    -------------
    url: str
        The URL to be checked.
    """
    url = extract_local_path_and_args(url)
    dec_url = unquote(url)
    ## Note that a link may be escaped multiple times. (Example youtube link
    ## to sign in.)
    iteration = 0
    while url != dec_url:
        if re.search(SUBLINK, url) is not None:
            return True
        url = dec_url
        dec_url = unquote(dec_url)
        iteration += 1

        if iteration > 5: # anything deeper that that should be deemed suspicious
            return True
    return False
