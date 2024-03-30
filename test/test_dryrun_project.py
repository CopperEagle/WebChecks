 
import unittest
import os

from webchecks import Project
from webchecks.profiles.ProfileConstants import *
from webchecks.utils.Error import OptionsError
from webchecks.profiles.BaseProfile import BaseProfile
from webchecks.config import *

class SomeWebsiteProfile(BaseProfile):
    def __init__(self):
        super(SomeWebsiteProfile, self).__init__("somewebsite.com")
        self._set_access_algorithm(ACCESS_EXPONENTIAL_RND_MIN, 80, 60)


_PROJECT_NAME = "TESTINGDRYRUNPROJECT123123212312"

class ProjectTest(unittest.TestCase):

    def test_dryrun_1(self):
        config[LOGGING_LEVEL] = LOG_ERROR
        configcopy = config.copy()
        
        proj = Project(_PROJECT_NAME, "website.org")
        proj.install_profile(SomeWebsiteProfile())
        proj.quiet_exit()
        self.delete(_PROJECT_NAME)
        
        for k, v in configcopy.items():
            config[k] = v

        # Project root exists...
        os.mkdir(_PROJECT_NAME) 
        proj2 = Project(_PROJECT_NAME, "en.website.org")
        proj2.install_profile(SomeWebsiteProfile())
        proj2.quiet_exit()
        for k, v in configcopy.items():
            config[k] = v

        # Project exists... 
        proj3 = Project(_PROJECT_NAME, "website2.org")
        proj3.enable_crawl(True)
        proj3.set_timeout(200)
        proj3.sec_allow_all_websites()
        proj3.sec_set_allowed_websites(("wikipedia.org",))
        proj3.sec_whitelisted_tld_only(("good",))
        proj3.sec_blindly_trusted_tld(("excellent",))
        proj3.sec_single_domain_only("island.web")
        proj3.sec_allow_generic_redirect(True)
        proj3.set_compress_text(True)
        proj3.set_logging_level(LOG_ERROR)

        with self.assertRaises(ValueError):
            proj3.set_logging_level(10)

        proj3.set_browser_driver_location("here")
        proj3.set_browser_use_profile("there")
        proj3.sec_reset_javascript_permissions_for_domains()
        proj3.sec_set_allow_javascript_for_domain("goodjs.com")
        proj3.sec_set_disallow_javascript_for_domain("badjs.com")
        proj3.sec_enforce_https(True)
        proj3.set_min_wait(10)
        proj3.set_avg_wait(5)


        proj3.install_profile(SomeWebsiteProfile())
        proj3.quiet_exit()
        self.delete(_PROJECT_NAME)


        self.assertEqual(config[DO_CRAWL], True)
        self.assertEqual(config[DEFAULT_TIMEOUT_IN_SEC], 200)
        self.assertEqual(config[WHITELIST_DOMAINS], ("wikipedia.org",))
        self.assertEqual(config[WHITELIST_TLD], ("good",))
        self.assertEqual(config[BLINDLY_TRUSTED_TLD], ("excellent",))
        self.assertEqual(config[SINGLE_DOMAIN_ONLY], "island.web")
        self.assertEqual(config[ALLOW_REDIRECT], True)
        self.assertEqual(config[COMPRESS_CONTENT], True)
        self.assertEqual(config[LOGGING_LEVEL], LOG_ERROR)
        self.assertEqual(config[LOCATION_FIREFOX_DRIVER], "here")
        self.assertEqual(config[PROFILE_FIREFOX_BROWSER], "there")
        
        self.assertEqual(config[ENFORCE_HTTPS], True)
        self.assertEqual(config[ACCESS_DEFAULT_MIN_WAIT], 10)
        self.assertEqual(config[ACCESS_DEFAULT_INTERVAL], 5)

        self.assertEqual(javascript_checklist["goodjs.com"], TRUSTED)
        self.assertEqual(javascript_checklist["badjs.com"], UNTRUSTED)
        self.assertEqual(javascript_checklist["*"], TRUSTED)

        proj3.sec_set_disallow_javascript_for_domain("*")

        self.assertEqual(javascript_checklist["*"], UNTRUSTED)

        for k, v in configcopy.items():
            config[k] = v
        config[LOGGING_LEVEL] = LOG_INFO

    def test2(self):
        class SomeWebsiteProfile2(BaseProfile):
            def __init__(self):
                super(SomeWebsiteProfile2, self).__init__("somewebsite.com")
                self._set_access_algorithm(200, 80, 60)
        with self.assertRaises(OptionsError):
            SomeWebsiteProfile2()
        

    def delete(self, path):
        for base, dirs, filenames in os.walk(top=path):
            for fn in filenames:
                file = os.path.join(base, fn)
                os.remove(file)

            for d in dirs:

                dirpath = os.path.join(base, d)
                self.delete(dirpath)
        os.rmdir(path)

