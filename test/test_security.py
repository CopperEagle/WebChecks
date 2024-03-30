import unittest

from webchecks.access.security import *
from webchecks.utils.Error import InputError
from webchecks.access.Gateway import GateWay


class SecurityTest(unittest.TestCase):
    """Test for the security.py file"""


    links = [
        # No local link
        "okay.com",
        # No local link to speak of
        "okay.com/",
        # innocent
        "okay.com/hey",
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

        "site.com/?link=https%2525252525253A//site.com/goto/this%2525252525253Fat%2525252525253Dthat.addr",

        "https://arstechnica.com/store/product/subscriptions/",

        "https://huggingface.co/codellama/CodeLlama-7b-Instruct-hf?text=The+fallowing+analyzes+the+sentiment+of+a+given+string.%0A%0Astring%3A+%22This+text+is+good.%22%0A%0Aanalysis%3A",

        "https://www.youtube.com/@NoCopyrightSounds",

        "hello.world.com",

        "hello.world.com/link/to/file.mp4",

        "hello.world.com/link/to/file.mp4?res_x=680&res_y=320",

    ]
    def test_generic_redirect(self):

        isredirect = [False, False, False, True, True, True, True, True, True, True, False, False, False, False, False, False]
        for i in range(len(self.links)):
            self.assertEqual(isredirect[i], is_generic_redirect(self.links[i]), f" Test security.py: Mismatch detecting redirect for index {i}.")

        with self.assertRaises(InputError, msg="Test security.py: is_generic_redirect should throw InputError if not URL"):
            is_generic_redirect("/hey")

    def test_security_check_link(self):
        self._test_1()
        self._test_2()
        self._test_3()
        self._test_4()


    def _test_1(self):
        config[WHITELISTED_DOMAINS_ONLY] = True
        config[WHITELISTED_TLD_ONLY] = False
        config[ENABLE_BLINDLY_TRUSTED_TLD] = False
        config[SINGLE_DOMAIN_ONLY] = False
        config[ALLOW_REDIRECT] = False
        config[WHITELIST_DOMAINS] = [r"(.*\.)?wiki(.*)\.org", r"(.*\.)?wiki\.org", "fulldomain.com"]

        self.assertTrue(is_allowed_url("wiki.org"))
        self.assertTrue(is_allowed_url("en.wiki.org"))
        self.assertTrue(is_allowed_url("https://wiki.org"))
        self.assertTrue(is_allowed_url("https://cool.en.wiki.org"))
        self.assertTrue(is_allowed_url("https://en.wiki.org/this/is/cool.html?query=10#Summary"))
        self.assertTrue(is_allowed_url("en.wiki.org/this/is/cool.html?query=10#Summary"))
        self.assertTrue(is_allowed_url("ok.en.wiki.org/this/is/cool.html?query=10#Summary"))
        self.assertTrue(is_allowed_url("fulldomain.com/this/is/cool.html?query=10#Summary"))
        self.assertTrue(is_allowed_url("wikimedia.org/this/is/cool.html?query=10#Summary"))
        self.assertFalse(is_allowed_url("https://en.wiki.com/this/is/cool.html?query=10&site=https%3A%2F%2Fwww.somesite.com#Summary"))


        self.assertFalse(is_allowed_url("cool.com"))
        self.assertFalse(is_allowed_url("nice.org"))
        self.assertFalse(is_allowed_url("okay.en.fulldomain.com/this/is/cool.html?query=10#Summary"))
        self.assertFalse(is_allowed_url("en.wiki.com/this/is/cool.html?query=10#Summary"))
        self.assertFalse(is_allowed_url("en.wiki.org/this/is/cool.html?query=10&site=https%3A%2F%2Fwww.somesite.com"))
        self.assertFalse(is_allowed_url("wikimedia.org/this/is/web.html?query=10&site=https%3A%2F%2Fwww.somesite.com"))
        self.assertFalse(is_allowed_url("https://en.wiki.org/this/is/cool.html?query=10&site=https%3A%2F%2Fwww.somesite.com#Summary"))


    def _test_2(self):
        config[WHITELISTED_DOMAINS_ONLY] = True
        config[WHITELISTED_TLD_ONLY] = True
        config[ENABLE_BLINDLY_TRUSTED_TLD] = False
        config[SINGLE_DOMAIN_ONLY] = False
        config[ALLOW_REDIRECT] = False
        config[WHITELIST_DOMAINS] = [r"(.*\.)?wiki(.*)\.org", r"(.*\.)?wiki\.org", "fulldomain.com"]
        config[WHITELIST_TLD] = ["org"]

        self.assertTrue(is_allowed_url("wiki.org"))
        self.assertTrue(is_allowed_url("en.wiki.org"))
        self.assertTrue(is_allowed_url("https://wiki.org"))
        self.assertTrue(is_allowed_url("https://cool.en.wiki.org"))
        self.assertTrue(is_allowed_url("https://en.wiki.org/this/is/cool.html?query=10#Summary"))
        self.assertTrue(is_allowed_url("en.wiki.org/this/is/cool.html?query=10#Summary"))
        self.assertTrue(is_allowed_url("ok.en.wiki.org/this/is/cool.html?query=10#Summary"))
        self.assertTrue(is_allowed_url("wikimedia.org/this/is/cool.html?query=10#Summary"))
        self.assertFalse(is_allowed_url("https://en.wiki.com/this/is/cool.html?query=10&site=https%3A%2F%2Fwww.somesite.com#Summary"))


        self.assertFalse(is_allowed_url("cool.com"))
        self.assertFalse(is_allowed_url("nice.org"))
        self.assertFalse(is_allowed_url("fulldomain.com/this/is/cool.html?query=10#Summary"))
        self.assertFalse(is_allowed_url("okay.en.fulldomain.com/this/is/cool.html?query=10#Summary"))
        self.assertFalse(is_allowed_url("en.wiki.com/this/is/cool.html?query=10#Summary"))
        self.assertFalse(is_allowed_url("en.wiki.org/this/is/cool.html?query=10&site=https%3A%2F%2Fwww.somesite.com"))
        self.assertFalse(is_allowed_url("wikimedia.org/this/is/web.html?query=10&site=https%3A%2F%2Fwww.somesite.com"))
        self.assertFalse(is_allowed_url("https://en.wiki.org/this/is/cool.html?query=10&site=https%3A%2F%2Fwww.somesite.com#Summary"))

    def _test_3(self):
        config[WHITELISTED_DOMAINS_ONLY] = True
        config[WHITELISTED_TLD_ONLY] = True
        config[ENABLE_BLINDLY_TRUSTED_TLD] = True
        config[SINGLE_DOMAIN_ONLY] = False
        config[ALLOW_REDIRECT] = True
        config[WHITELIST_DOMAINS] = [r"(.*\.)?wiki(.*)\.org", r"(.*\.)?wiki\.org", "fulldomain.com"]
        config[WHITELIST_TLD] = ["org"]
        config[BLINDLY_TRUSTED_TLD] = ["net"]

        self.assertTrue(is_allowed_url("wiki.org"))
        self.assertTrue(is_allowed_url("en.wiki.org"))
        self.assertTrue(is_allowed_url("https://wiki.org"))
        self.assertTrue(is_allowed_url("https://cool.en.wiki.org"))
        self.assertTrue(is_allowed_url("https://en.wiki.org/this/is/cool.html?query=10#Summary"))
        self.assertTrue(is_allowed_url("en.wiki.org/this/is/cool.html?query=10#Summary"))
        self.assertTrue(is_allowed_url("ok.en.wiki.org/this/is/cool.html?query=10#Summary"))
        self.assertTrue(is_allowed_url("wikimedia.org/this/is/cool.html?query=10#Summary"))

        self.assertFalse(is_allowed_url("cool.com"))
        self.assertFalse(is_allowed_url("nice.org"))
        self.assertFalse(is_allowed_url("fulldomain.com/this/is/cool.html?query=10#Summary"))
        self.assertFalse(is_allowed_url("okay.en.fulldomain.com/this/is/cool.html?query=10#Summary"))
        self.assertFalse(is_allowed_url("en.wiki.com/this/is/cool.html?query=10#Summary"))
        self.assertTrue(is_allowed_url("en.wiki.org/this/is/cool.html?query=10&site=https%3A%2F%2Fwww.somesite.com"))
        self.assertTrue(is_allowed_url("wikimedia.org/this/is/web.html?query=10&site=https%3A%2F%2Fwww.somesite.com"))
        self.assertTrue(is_allowed_url("https://en.wiki.org/this/is/cool.html?query=10&site=https%3A%2F%2Fwww.somesite.com#Summary"))
        self.assertFalse(is_allowed_url("https://en.wiki.com/this/is/cool.html?query=10&site=https%3A%2F%2Fwww.somesite.com#Summary"))

        self.assertTrue(is_allowed_url("https://okay2.hm.hey.net/"))
        self.assertTrue(is_allowed_url("https://en.wiki.net/this/is/cool.html?query=10&site=https%3A%2F%2Fwww.somesite.com#Summary"))
        self.assertTrue(is_allowed_url("https://en.someschool.net/this/is/cool.html?query=10&site=https%3A%2F%2Fwww.somesite.com#Summary"))

    def _test_4(self):
        config[WHITELISTED_DOMAINS_ONLY] = True
        config[WHITELISTED_TLD_ONLY] = True
        config[ENABLE_BLINDLY_TRUSTED_TLD] = True
        config[SINGLE_DOMAIN_ONLY] = (r"(.*\.)?wiki\.org", "fulldomain.com")
        config[ALLOW_REDIRECT] = True
        config[WHITELIST_DOMAINS] = [r"(.*\.)?wiki(.*)\.org", r"(.*\.)?wiki\.org", "fulldomain.com"]
        config[WHITELIST_TLD] = ["org"]
        config[BLINDLY_TRUSTED_TLD] = ["net"]
        config[BLACKLISTED_TLD] = ["badtld"]

        with self.assertRaises(InputError):
            is_allowed_url("wiki.org")

        config[SINGLE_DOMAIN_ONLY] = r"(.*\.)?wiki\.org"

        self.assertTrue(is_allowed_url("wiki.org"))
        self.assertTrue(is_allowed_url("en.wiki.org"))
        self.assertTrue(is_allowed_url("https://wiki.org"))
        self.assertTrue(is_allowed_url("https://cool.en.wiki.org"))
        self.assertTrue(is_allowed_url("https://en.wiki.org/this/is/cool.html?query=10#Summary"))
        self.assertTrue(is_allowed_url("en.wiki.org/this/is/cool.html?query=10#Summary"))
        self.assertTrue(is_allowed_url("ok.en.wiki.org/this/is/cool.html?query=10#Summary"))
        self.assertFalse(is_allowed_url("wikimedia.org/this/is/cool.html?query=10#Summary"))

        self.assertFalse(is_allowed_url("cool.com"))
        self.assertFalse(is_allowed_url("nice.org"))
        self.assertFalse(is_allowed_url("fulldomain.com/this/is/cool.html?query=10#Summary"))
        self.assertFalse(is_allowed_url("okay.en.fulldomain.com/this/is/cool.html?query=10#Summary"))
        self.assertFalse(is_allowed_url("en.wiki.com/this/is/cool.html?query=10#Summary"))
        self.assertTrue(is_allowed_url("en.wiki.org/this/is/cool.html?query=10&site=https%3A%2F%2Fwww.somesite.com"))
        self.assertFalse(is_allowed_url("wikimedia.org/this/is/web.html?query=10&site=https%3A%2F%2Fwww.somesite.com"))
        self.assertTrue(is_allowed_url("https://en.wiki.org/this/is/cool.html?query=10&site=https%3A%2F%2Fwww.somesite.com#Summary"))
        self.assertFalse(is_allowed_url("https://en.wiki.com/this/is/cool.html?query=10&site=https%3A%2F%2Fwww.somesite.com#Summary"))

        self.assertTrue(is_allowed_url("https://okay2.hm.hey.net/"))
        self.assertTrue(is_allowed_url("https://en.wiki.net/this/is/cool.html?query=10&site=https%3A%2F%2Fwww.somesite.com#Summary"))
        self.assertTrue(is_allowed_url("https://en.someschool.net/this/is/cool.html?query=10&site=https%3A%2F%2Fwww.somesite.com#Summary"))

        self.assertFalse(is_allowed_url("https://en.wiki.badtld/this/is/cool.html?query=10&site=https%3A%2F%2Fwww.somesite.com#Summary"))
        self.assertFalse(is_allowed_url("https://en.wiki.badtld/this/is"))
        self.assertFalse(is_allowed_url("wiki.badtld/this/"))


        
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


