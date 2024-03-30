import os
import unittest
from webchecks import Project
from webchecks.config import config
from webchecks.utils.constants import *
from webchecks.access.Gateway import GateWay
from webchecks.access.RobotsFile import RobotsFile


l = """
Sitemap: disissomehttp

User-agent: Googlebot-Image
Disallow:
Allow: /*

# Google AdSense
User-agent: Mediapartners-Google*
Disallow:

# Common Crawl
User-agent: CCBot # TODO ...
# another comment
# a long one
Disallow: /

User-agent: GPTBot #nah
Disallow: /
User-agent: ChatGPT-User
Disallow: /

# Global
User-agent: *
Disallow: /cgi-bin/
Disallow: /wp/wp-admin/
Disallow: /comments/
Disallow: /category/*/*
Disallow: */trackback/
Disallow: */comments/
Disallow: /search
Allow: /search/hey/superspecial.omg
# may need revisioning
Disallow: /civis/account/
Disallow: /civis/admin.php
Allow: /access_this/
Disallow: /access_this/but_not_this.ok?

"""


class URLTest(unittest.TestCase):


    def test_robotsfile_parsing(self):
    
        rob = RobotsFile() 
        rules = rob.parse_robotstxt(l)
        self.assertTrue(rob.check_rules(rules, "/"))
        self.assertTrue(rob.check_rules(rules, "/category/okay.txt"))
        self.assertTrue(rob.check_rules(rules, "/search/hey/superspecial.omg"))
        self.assertTrue(rob.check_rules(rules, "/access_this/please.ok"))
        self.assertFalse(rob.check_rules(rules, "/access_this/but_not_this.ok?"))
        
        self.assertFalse(rob.check_rules(rules, "/category/o/okay.txt?test"))
        self.assertFalse(rob.check_rules(rules, "/dude/trackback/okay.txt?testest"))
        self.assertFalse(rob.check_rules(rules, "/trackback/okay.txt?andtest"))

        config[AGENT_NAME] = "GPTBot"
        rules = rob.parse_robotstxt(l) ## requires regenerating rules
        self.assertFalse(rob.check_rules(rules, "/category/o/okay.txt?test"))
        self.assertFalse(rob.check_rules(rules, "/happy.txt"))
        self.assertFalse(rob.check_rules(rules, "/trackback/okay.txt"))
        self.assertFalse(rob.check_rules(rules, "/"))

_PROJECT_NAME = "TESTINGDRYRUNGATEWAY123123212312"

class GatewayTest(unittest.TestCase):
    
    def test_dryrun_gateway(self):
        configcopy = config.copy()
        config[ENABLE_JAVASCRIPT] = False
        config[LOGGING_LEVEL] = LOG_ERROR
        config[WHITELIST_DOMAINS] = ("noexistent-website-2221212.org",)

        proj = Project(_PROJECT_NAME, "noexistent-website-2221212.org")
        proj.quiet_exit()

        gw = GateWay()
        self.assertFalse(gw.add_to_queue("noexistent-website-2221212.org"))
        self.assertFalse(gw.add_to_queue("noexistent-website-2221212.org/hello.txt"))
        self.assertFalse(gw.add_to_queue("txt"))
        self.assertFalse(gw._verify_is_url(""))
        self.assertEqual(gw._ensure_https_protocol("hello.com"), "https://hello.com")
        self.assertEqual(gw._ensure_https_protocol("ftp://hello.com"), "https://hello.com")
        self.assertFalse(gw._permitted_link("hello.com"))
        self.assertTrue(gw.done())
        # we ask for nonexistent URLs, so...
        print("THE LOGGED ERRORS YOU SEE ABOVE ARE AS EXPECTED.")

        for k, v in configcopy.items():
            config[k] = v
        self.delete(_PROJECT_NAME)

    def delete(self, path):
        for base, dirs, filenames in os.walk(top=path):
            for fn in filenames:
                file = os.path.join(base, fn)
                os.remove(file)

            for d in dirs:

                dirpath = os.path.join(base, d)
                self.delete(dirpath)
        os.rmdir(path)

        
