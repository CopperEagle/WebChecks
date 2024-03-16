import unittest
from webchecks.utils.url import *
from webchecks.utils.timedqueue import *
class URLTest(unittest.TestCase):


    urls = [
        "https://hello.world.com", "hi.com", "ok.ok.ok.world.zip", "hi.net/ok.ok/yes",
        "friendly.net/service?ok=malicious.redirect.com", "nor.is-.this/some/url.ok",
        "file://your/file.mp4/https://youtube.com", "hello?.ok.no", "this[]isno.url", 
        "hi", "", "/thisis_https://match.this.url",
        "ftp://no", "ftp://.noturl"
    ]

    isurl = [True, True, True, True, True, True, False, False, False, False, False, False, False, False]
    tld = ["com", "com", "zip", "net", "net", "this"]
    domain_names = ["world", "hi", "world", "hi", "friendly", "is-"]
    domains = ["world.com", "hi.com", "world.zip", "hi.net", "friendly.net", "is-.this"]
    protocols = ["https", None, None, None, None, None]

    def test_data_integrity(self):
        self.assertEqual(len(self.urls), len(self.isurl), "Test url.py: Testcase - result length mismatch.")

    def test_URL_extract(self): 
        for i in range(len(self.urls)):
            url = self.urls[i]
            if self.isurl[i]:
                self.assertTrue(is_url(url), f"Test url.py: Rejected valid url {url}.")

                t = extract_tld(url)
                dn = extract_domain_name(url)
                d = extract_domain(url)
                p = extract_protocol(url)

                self.assertEqual(t, self.tld[i], f"Test url.py: Bad self.tld {t}, expected {self.tld[i]}.")
                self.assertEqual(dn, self.domain_names[i], f"Test url.py: Bad domain name {dn},\
                 expected {self.domain_names[i]}.")
                self.assertEqual(d, self.domains[i], f"Test url.py: Bad domain {d}, expected {self.domains[i]}.")
                self.assertEqual(p, self.protocols[i], f"Test url.py: Bad protocol {p}, expected {self.protocols[i]}.")
            else:
                self.assertFalse(is_url(url), f"Test url.py: Accepted invalid url {url}.")

    def test_URL_manipulate(self):
        self.assertEqual(change_protocol("ftp", "hi.net/ok.ok/yes"), "ftp://hi.net/ok.ok/yes",
            "Test url.py: Change protocol on basic test failed.")

        new_prot = change_protocol("ftp", "https://accounts.google.com/ServiceLogin?service=youtube&uilel=3&passive=true&continue=https%3A%2F%2Fwww.youtube.com%2Fsignin%3Faction_handle_signin%3Dtrue%26app%3Ddesktop%26hl%3Den%26next%3Dhttps%253A%252F%252Fwww.youtube.com%252F&hl=en")
        solution = "ftp://accounts.google.com/ServiceLogin?service=youtube&uilel=3&passive=true&continue=https%3A%2F%2Fwww.youtube.com%2Fsignin%3Faction_handle_signin%3Dtrue%26app%3Ddesktop%26hl%3Den%26next%3Dhttps%253A%252F%252Fwww.youtube.com%252F&hl=en"
        self.assertEqual(new_prot, solution, "Test url.py: Change protocol on Google Link failed.")
        

        with self.assertRaises(ValueError, msg=f"Test url.py: Changed protocol on mini invalid url link."):
            change_protocol("ftp", "https://url")
        
        with self.assertRaises(ValueError, msg=f"Test url.py: Changed protocol on basic invalid url link."):
            change_protocol("ftp", "/thisis_https://match.this.url")

        with self.assertRaises(ValueError, msg=f"Test url.py: Added second protocol."):
            add_protocol("ftp", "https://match.this.url")

        with self.assertRaises(ValueError, msg=f"Test url.py: Added protocol on invalid url link."):
            add_protocol("ftp", "/thisis_https://match.this.url") #change?


class QueueTest(unittest.TestCase):
    """Test for the timedqueue. Should add more tests."""
    def testrun(self):
        q = TimedQueue()
        time = 0
        q.enqueue("a", 1, 1, time)
        q.enqueue("b", 2, 1, time)
        q.enqueue("b", 3, 3, time)
        time = 2
        self.assertIn(q.dequeue(time), (1, 2))
        self.assertIn(q.dequeue(time), (1, 2))
        self.assertIsNone(q.dequeue(time))
        time = 3
        self.assertIsNone(q.dequeue(time))
        time = 5
        self.assertEqual(q.dequeue(time), 3)
        self.assertIsNone(q.dequeue(time))
        self.assertIsNone(q.dequeue(time))
        time = 1000
        self.assertIsNone(q.dequeue(time))

    def testrun2(self):
        q = TimedQueue()
        time = 0
        q.enqueue("a", 1, 1, time)
        q.enqueue("b", 2, 1, time)
        q.enqueue("c", 2, 1, time)
        q.enqueue("d", 2, 1, time)
        q.enqueue("e", 2, 1, time)
        q.enqueue("a", 3, 3, time)
        time = 2
        self.assertIn(q.dequeue(time), (1, 2))
        self.assertIn(q.dequeue(time), (1, 2))
        self.assertIn(q.dequeue(time), (1, 2))
        self.assertIn(q.dequeue(time), (1, 2))
        self.assertIn(q.dequeue(time), (1, 2))
        self.assertIsNone(q.dequeue(time))
        q.enqueue("b", 3, 1, time)
        q.enqueue("a", 4, 995, time)
        time = 3
        self.assertEqual(q.dequeue(time), 3)
        self.assertIsNone(q.dequeue(time))
        time = 5
        self.assertEqual(q.dequeue(time), 3) # one late
        self.assertIsNone(q.dequeue(time))
        self.assertIsNone(q.dequeue(time))
        time = 1000
        self.assertEqual(q.dequeue(time), 4)
        self.assertIsNone(q.dequeue(time))



        
            

if __name__ == '__main__':
    unittest.main()