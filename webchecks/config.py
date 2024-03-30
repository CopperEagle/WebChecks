"""Provides the project's configuration dictionary."""

# pylint: disable-next=wildcard-import
from webchecks.utils.constants import *

### The user should not modify these directly. Instead, use the Project interface.
### Some are not yet used or cannot yet be modified by the user... for good reason.
config = {

    LOGGING_LEVEL : LOG_INFO,
    LOGGING_FILE : 'scraper.log', ## disable by setting ""
    LOGGING_LINKS : 'links.log',

    KEYWORDS : [],
    DO_CRAWL : True,

    ## DEFAULT SECURITY POLICY
    ENABLE_JAVASCRIPT : True,
    USER_AGENT :  "Python webclient",
    ENFORCE_HTTPS: True,

    WHITELISTED_DOMAINS_ONLY : False,
    WHITELISTED_TLD_ONLY : False,
    ENABLE_BLINDLY_TRUSTED_TLD : False,
    SINGLE_DOMAIN_ONLY : None,
    ALLOW_REDIRECT : False,
    WHITELIST_DOMAINS : [],
    WHITELIST_TLD : (),
    BLINDLY_TRUSTED_TLD : (),
    BLACKLISTED_TLD : (),

    LOCATION_FIREFOX_DRIVER : '',
    # put the root directory your default profile path here, you can check
    # it by opening Firefox and then pasting 'about:profiles' into the url field
    PROFILE_FIREFOX_BROWSER : '',
    BROWSER_CLEAN_SHEET_SETUP : True,
    DEFAULT_TIMEOUT_IN_SEC : 20,

    # allows other directories like /metadata for project-level metadata
    RESULT_STORAGE_LOCATION : "content",
    CACHE_STORAGE_LOCATION : "content/.cache",
    COMPRESS_CONTENT : True,
    ## these are defalt policies for profiles.
    ## per profile specifications can be made if required.
    DEFAULT_PER_PROFILE_CONTENT_STORAGE_LOCATION : "%PROFILE_DOMAIN_NAME",
    DEFAULT_ALLOWED_PROTOCOLS : ("https",),

    ## THIS IS CURRENTLY IGNORED.
    #DEFAULT_ALLOWED_FILE_EXTENSIONS : ("html", "xhtml", "pdf"),

    ## Robots.txt policy
    # free or strict : determines what to do if no robots.txt file available
    UNGUIDED_ACCESS_POLICY : "strict",
    AGENT_NAME : "Python webclient",

    ## Default minimum delay between two accesses to the same domain
    ACCESS_DEFAULT_MIN_WAIT : 20,
    ACCESS_DEFAULT_INTERVAL : 25
}



javascript_checklist =  {
    ## the default setting for any website not explicitly listed here
    "*" : TRUSTED
    # "goodsite.com" : TRUSTED
    # "badsite.com" : UNTRUSTED
}
