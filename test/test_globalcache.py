 
import unittest
import os
from hashlib import md5

from webchecks import Project
from webchecks.archive.GlobalCache import GlobalCache
from webchecks.profiles.ProfileConstants import *
from webchecks.utils.Error import OptionsError
from webchecks.profiles.BaseProfile import BaseProfile
from webchecks.config import *


_PROJECT_NAME = "TESTINGDRYRUNGLOBALCACHE123123212312"

class GlobalCacheTest(unittest.TestCase):

    def test_dryrun_1(self):
        config[LOGGING_LEVEL] = LOG_ERROR
        configcopy = config.copy()
        
        proj = Project(_PROJECT_NAME, "website.org")
        proj.quiet_exit()
        glc = GlobalCache()
        ## yeah, ugly. It's because we open many Projects during testing,
        ## so we need to reinitialize.
        glc.__init__()
        glc.store_link_location("link_a", "link_b")
        self.assertEqual(glc.get_link_location("link_a"), ("link_b",))
        glc.store_link_location("link_a", "link_b2")
        glc.store_link_location("link_a", "link_b3")
        glc.store_link_location("link_c", "link_d")
        self.assertEqual(glc.get_link_location("link_a"), ("link_b",))
        self.assertEqual(glc.get_link_location("link_c"), ("link_d",))

        glc.store("domain", "content", "name", 10000)
        self.assertEqual(glc.load("domain", "name", False), ("content", md5(b"content").digest()))
        glc.store("domain2", "content22", "name", 10000)
        glc.store("domain3", "content44", "name", 10000)
        self.assertEqual(glc.load("domain2", "name", False), ("content22", md5(b"content22").digest()))
        self.assertEqual(glc.load("domain3", "name", False), ("content44", md5(b"content44").digest()))
        glc.store("newdomain", "content", "name", 0)
        self.assertEqual(glc.load("newdomain", "name", False), (None, None))





        self.delete(_PROJECT_NAME)
        
        for k, v in configcopy.items():
            config[k] = v
        

    def delete(self, path):
        for base, dirs, filenames in os.walk(top=path):
            for fn in filenames:
                file = os.path.join(base, fn)
                os.remove(file)

            for d in dirs:

                dirpath = os.path.join(base, d)
                self.delete(dirpath)
        os.rmdir(path)

