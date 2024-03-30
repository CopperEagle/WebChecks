"""
Defines the constants, most are for the config dictionary.
Rather than using strings as keys directly, these constants are used.
This allows easier development (typo errors fail non silently) but also if the 
user prints config, it is still human readable.
"""

WHITELIST_DOMAINS = "whitelist_domains"
WHITELIST_TLD = "whitelist_tld"
BLINDLY_TRUSTED_TLD = "blindly_trusted_tld"
BLACKLISTED_TLD = "blacklisted_tld"
DEFAULT_ALLOWED_PROTOCOLS = "default_allowed_protocol"
DEFAULT_ALLOWED_FILE_EXTENSIONS = "default_allowed_file_extensions"
FILEEXTENSIONS = "fileextensions"
DEFAULT_PER_PROFILE_CONTENT_STORAGE_LOCATION = "default_per_profile_content_storage_location"
RESULT_STORAGE_LOCATION = "result_storage_location"
CACHE_STORAGE_LOCATION = "cache_storage_location"
COMPRESS_CONTENT = "compress_content"
UNGUIDED_ACCESS_POLICY = "unguided_access_policy"
DEFAULT_ROBOTS_TXT_POLICY = "default_robots_txt_policy"

WHITELISTED_DOMAINS_ONLY =  "whitelisted_domains_only"
WHITELISTED_TLD_ONLY = "whitelisted_tld_only"
ENABLE_BLINDLY_TRUSTED_TLD = "enable_blindly_trusted_tld"
SINGLE_DOMAIN_ONLY = "single_domain_only"
ALLOW_REDIRECT = "allow_redirect"

ENABLE_JAVASCRIPT = "enable_javascript"
LOCATION_FIREFOX_DRIVER = "location_firefox_driver"
PROFILE_FIREFOX_BROWSER = "profile_firefox_browser"
BROWSER_CLEAN_SHEET_SETUP = "browser_clean_sheet_setup"
DEFAULT_TIMEOUT_IN_SEC = "default_timeout_in_sec"

KEYWORDS = "keywords"
LOGGING_LEVEL = "logging_level"
LOGGING_LINKS = "logging_links"
LOGGING_FILE = "logging_file"

LOG_DEBUG = 0
LOG_INFO = 1
LOG_WARNING = 2
LOG_ERROR = 3

UNTRUSTED = "untrusted"
TRUSTED   = "trusted"

AGENT_NAME = "agent_name"
USER_AGENT = "user_agent"

DO_CRAWL = "do_crawl"

ACCESS_DEFAULT_INTERVAL = "avg_delay_between_accesses_to_same_domain"
ACCESS_DEFAULT_MIN_WAIT = "min_delay_between_accesses_to_same_domain"
ENFORCE_HTTPS = "enforce_https"
