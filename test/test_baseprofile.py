 
import unittest

from webchecks.profiles.ProfileConstants import *
from webchecks.utils.Error import OptionsError
from webchecks.profiles.BaseProfile import BaseProfile
from webchecks.config import *

class SomeWebsiteProfile(BaseProfile):
    def __init__(self):
        super(SomeWebsiteProfile, self).__init__("somewebsite.com")
        self._set_access_algorithm(ACCESS_EXPONENTIAL_RND_MIN, 80, 60)

class SomeWebsiteProfile2(BaseProfile):
    def __init__(self):
        super(SomeWebsiteProfile2, self).__init__("somewebsite2.com")
        self._set_access_algorithm(ACCESS_EXPONENTIAL_RND, 80, 60)

class SomeWebsiteProfile3(BaseProfile):
    def __init__(self):
        super(SomeWebsiteProfile3, self).__init__("somewebsite3.com")
        self._set_access_algorithm(ACCESS_EQUISPACED, 80, 60)

_website = """<html><head></head><body>
<p> This is some text where <a href="https://different.com">this</a>
is <a href="//otherdifferent.com">linked</a> and thus <a href="/nice">
there</a> are more <a href="#Summary">links</a><a href="">.</a>
</body>"""


class ProjectTest(unittest.TestCase):

    def test_baseprofile(self):
        profile = SomeWebsiteProfile()
        profile._get_wait_time_equispaced(10)
        profile._get_wait_time_equispaced_rnd(10)
        profile._get_wait_time_equispaced_rnd_min(10)
        self.assertTrue(profile.get_archive())
        self.assertFalse(profile.get_urls_visited())
        links = set(profile.get_links("https://base.com", _website))
        self.assertEqual(links, 
            set(["https://different.com", "otherdifferent.com",
                "base.com/nice"]),
                f"Got {links}")
        profile = SomeWebsiteProfile2()
        links = set(profile.get_links("https://base.com", _website))
        self.assertEqual(links, 
            set(["https://different.com", "otherdifferent.com",
                "base.com/nice"]),
                f"Got {links}")
        profile = SomeWebsiteProfile3()
        links = set(profile.get_links("https://base.com", _website))
        self.assertEqual(links, 
            set(["https://different.com", "otherdifferent.com",
                "base.com/nice"]),
                f"Got {links}")
        