import unittest
from webchecks.config import config
from webchecks.utils.constants import *
from webchecks.access.RobotsFile import RobotsFile
from webchecks.access.security import *
from webchecks.access.Gateway import GateWay

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


class SecurityTest(unittest.TestCase):
    """Test for the security.py file"""


    links = [ 
        # youtube sign in link. double encoded link
        "https://accounts.google.com/ServiceLogin?service=youtube&uilel=3&passive=true&continue=https%3A%2F%2Fwww.youtube.com%2Fsignin%3Faction_handle_signin%3Dtrue%26app%3Ddesktop%26hl%3Den%26next%3Dhttps%253A%252F%252Fwww.youtube.com%252F&hl=en",
        # stackoverflow login
        "https://stackoverflow.com/users/login?ssrc=head&returnurl=https%3a%2f%2fstackoverflow.com%2f",
        # githib stuff
        "https://github.com/login?return_to=https%3A%2F%2Fgithub.com%2Fsomedude%2Fproject%2Ftree%2Fmain%2Fdemo",
        # level 2 encode only
        "https://accounts.google.com/ServiceLogin?service=youtube&uilel=3&passive=true&continue=%2Fsignin%3Faction_handle_signin%3Dtrue%26app%3Ddesktop%26hl%3Den%26next%3Dhttps%253A%252F%252Fwww.youtube.com%252F&hl=en",
        # level 2 no protocol
        "https://accounts.someweb.page/ServiceLogin?service=youtube&next=youtube.com%252F&hl=en",
        # basic redirect without protocol in main link
        "duckduckgo.com/l/?uddg=https%3A%2F%2Fen.wikipedia.org%2Fwiki%2FLK%2D99&rut=bae021c08e0a5f23e2053e417bed0a783979f39de27b0d1f86899cfc35a5fb6b",

        "https://arstechnica.com/store/product/subscriptions/",

        "https://huggingface.co/codellama/CodeLlama-7b-Instruct-hf?text=The+fallowing+analyzes+the+sentiment+of+a+given+string.%0A%0Astring%3A+%22This+text+is+good.%22%0A%0Aanalysis%3A",

        "https://www.youtube.com/@NoCopyrightSounds",

        "hello.world.com"

    ]
    def test_generic_redirect(self):

        isredirect = [True, True, True, True, True, True, False, False, False, False]
        for i in range(len(self.links)):
            self.assertEqual(isredirect[i], is_generic_redirect(self.links[i]), f" Test security.py: Mismatch detecting redirect for index {i}.")


        
    ### TEST_ is_allowed(url): only subcomponents are checked so far.
    ### TODO: add test for entire function, even if it is fairly simple

    # Test requires Internet connection as it fetches the Robots.txt file.
    #def test_gateway(self):
    #    config[ACCESS_DEFAULT_MIN_WAIT] = 0
    #    config[ACCESS_DEFAULT_INTERVAL] = 0

    #    expect = ["https://android.hello.com/index.html", "https://hello.com/hi", "https://www.hello.com/hi"]

    #    a = GateWay()

    #    a.add_to_queue("android.hello.com/hi")
    #    a.add_to_queue("www.android.hello.com/hi/okay.html")
    #    a.add_to_queue("www.android.hello.com/index.html")
    #    a.add_to_queue("http://hello.com/hi")
    #    a.add_to_queue("https://hello.com/hi")
    #    a.add_to_queue("https://www.hello.com/hi")
    #    a.add_to_queue("https://www.marvel.com/hi")
    #    a.add_to_queue("android.hello.com/hi/?so=https%3A%2F%2Fhello.world.com%2Fthis%2Fis%2Fa%2Flink.html")

    #    j = 0    
    #    for i in a.process_queue():
    #        self.assertIn(i, expect)
    #        j += 1
    #    self.assertEqual(len(expect), j)


    
            

if __name__ == '__main__':
    unittest.main()