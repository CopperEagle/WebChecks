import unittest

from webchecks.utils.url import *
from webchecks.utils.Error import InputError

class URLCase:
    def __init__(self, link, isurl, protocol, domain_name, domain, tld, fqdn, loc_path_n_arg, loc_path_no_arg):
        self.link = link
        self.isurl = isurl
        self.proto = protocol
        self.domain_name = domain_name
        self.domain = domain
        self.tld = tld
        self.fqdn = fqdn
        self.loc_path_n_arg = loc_path_n_arg
        self.loc_path_no_arg = loc_path_no_arg

        self.local = False
        self.sulo = False
        self.ref = False

    def set_local(self):
        self.local = True
        return self

    def set_sulo(self):
        self.sulo = True
        return self

    def set_ref(self):
        self.ref = True
        return self

def URL(link, isurl, protocol = None, domain_name = None, domain = None, 
        tld = None, fqdn = None, loc_path_n_arg = None, loc_path_no_arg = None):
    return URLCase(link, isurl, protocol, domain_name, domain, tld, fqdn, loc_path_n_arg, loc_path_no_arg)

class URLTest(unittest.TestCase):

    cases = [
        
        URL("hi.com", True, None, "hi", "hi.com", "com", "hi.com", "", ""),
        URL("hi.com/", True, None, "hi", "hi.com", "com", "hi.com", "/", "/"),
        URL("ok.ok.ok.world.zip", True, None, "world", "world.zip", "zip", "ok.ok.ok.world.zip", "", ""),
        URL("friendly.net/service?ok=malicious.redirect.com", True, None, "friendly", "friendly.net", 
            "net", "friendly.net", "/service?ok=malicious.redirect.com", "/service"),
        URL("nor.is-.this/some/url.ok", True, None, "is-", "is-.this", 
            "this", "nor.is-.this", "/some/url.ok", "/some/url.ok"),

        URL("https://hello.world.com", True, "https", "world", "world.com", "com", "hello.world.com", "", ""),

        URL("ftp://friendly.net/service?query=big&where=10", True, "ftp", "friendly", "friendly.net", 
            "net", "friendly.net", "/service?query=big&where=10", "/service"),

        URL("ftp://ok.friendly2.friendly.net/service?query=big&where=10", True, "ftp", "friendly", 
            "friendly.net", "net", "ok.friendly2.friendly.net", "/service?query=big&where=10", "/service"),
        URL("ftp://ok.friendly2.friendly.net/service?query=big&where=10#ThisAWESOMEparagraph", True, "ftp", "friendly",
             "friendly.net", "net", "ok.friendly2.friendly.net", "/service?query=big&where=10#ThisAWESOMEparagraph", "/service"),

        URL("", False).set_local(),
        URL("hi", False).set_local(),
        URL("hello?.ok.no", False).set_local(),
        URL("this[]isno.url", False).set_local(),
        URL("/thisis_https://match.this.url", False).set_local(),
        URL("file://your/file.mp4/https://youtube.com", False).set_local(),
        URL("file:///root/home/you/file.mp4", False).set_local(),
        URL("ftp://no", False).set_local(),
        URL("ftp://.noturl", False).set_local(),
        URL("//noturl.com", False).set_local().set_sulo(),
        URL("#noturl.com", False).set_local().set_ref(),
        URL("#Summary", False).set_local().set_ref(),
        URL("#Summary", False).set_local().set_ref()
    ]

    def test_URL_extract(self): 
        for case in self.cases:
            url = case.link
            if case.isurl:
                self._test_extract_isurl(url, case)
            else:
                self._test_extract_noturl(url, case)


        self.assertFalse(is_url(None))

        self.assertFalse(url_is_local(None))

        with self.assertRaises(InputError):
            url_is_referencial(None)

        with self.assertRaises(InputError):
            url_is_superlocal(None)

    def _test_extract_isurl(self, url, case):
        self.assertTrue(is_url(url), f"Test url.py: Rejected valid url '{url}'.")
        self.assertFalse(url_is_local(url), f"Test url.py: Accepted as local url: '{url}'.")
        self.assertFalse(url_is_superlocal(url), f"Test url.py: Accepted as sulo url '{url}'.")
        self.assertFalse(url_is_referencial(url), f"Test url.py: Accepted as ref url '{url}'.")

        p = extract_protocol(url)
        d = extract_domain(url)      
        dn = extract_domain_name(url)
        t = extract_tld(url)
        fqd = extract_fully_qualified_domain_name(url)
        lpa = extract_local_path_and_args(url)
        lpna = extract_local_path_without_args(url)

        self.assertEqual(p, case.proto, f"Test url.py: URL '{url}' - Bad protocol '{p}', expected '{case.proto}'.")
        self.assertEqual(d, case.domain, f"Test url.py: URL '{url}' - Bad domain '{d}', expected '{case.domain}'.")
        self.assertEqual(dn, case.domain_name, f"Test url.py: URL '{url}' - Bad domain name '{dn}', "
         f"expected '{case.domain_name}'.")
        self.assertEqual(t, case.tld, f"Test url.py: URL '{url}' - Bad self.tld '{t}', expected '{case.tld}'.")
        self.assertEqual(fqd, case.fqdn, f"Test url.py: URL '{url}' - Bad fqdn '{fqd}', expected '{case.fqdn}'.")
        self.assertEqual(lpa, case.loc_path_n_arg, f"Test url.py: URL '{url}' - Bad local path and argument '{lpa}',"
            f" expected '{case.loc_path_n_arg}'.")
        self.assertEqual(lpna, case.loc_path_no_arg, f"Test url.py: URL '{url}' - Bad local path and argument '{lpna}',"
            f" expected '{case.loc_path_no_arg}'.")
        self.assertEqual(
            change_protocol("yes", remove_args_from_url(url)), 
            change_protocol(
                "yes",
                merge_url(
                    extract_fully_qualified_domain_name(url),
                    extract_local_path_without_args(url)
                )
            ),
            f"Test url.py: Cannot merge properly."
        )

    def _test_extract_noturl(self, url, case):
        self.assertFalse(is_url(url), f"Test url.py: URL '{url}' - Accepted invalid url '{url}'.")
        self.assertEqual(case.local, url_is_local(url), f"Test url.py: Accepted as local url: '{url}'.")
        self.assertEqual(case.sulo, url_is_superlocal(url), f"Test url.py: Accepted as sulo url '{url}'.")
        self.assertEqual(case.ref, url_is_referencial(url), f"Test url.py: Accepted as ref url '{url}'.")
        with self.assertRaises(InputError):
            p = extract_protocol(url)

        with self.assertRaises(InputError):
            d = extract_domain(url)

        with self.assertRaises(InputError):
            dn = extract_domain_name(url)

        with self.assertRaises(InputError):
            t = extract_tld(url)

        with self.assertRaises(InputError):
            fqd = extract_fully_qualified_domain_name(url)

        with self.assertRaises(InputError):
            lpa = extract_local_path_and_args(url)

        with self.assertRaises(InputError):
            lpa = extract_local_path_without_args(url)

        with self.assertRaises(InputError):
            lpna = extract_local_path_without_args(url)


    def test_URL_manipulate(self):
        self.assertEqual(change_protocol("ftp", "hi.net/ok.ok/yes"), "ftp://hi.net/ok.ok/yes",
            "Test url.py: Change protocol on basic test failed.")

        new_prot = change_protocol("ftp", "https://accounts.google.com/ServiceLogin?service=youtube&uilel=3&passive=true&continue=https%3A%2F%2Fwww.youtube.com%2Fsignin%3Faction_handle_signin%3Dtrue%26app%3Ddesktop%26hl%3Den%26next%3Dhttps%253A%252F%252Fwww.youtube.com%252F&hl=en")
        solution = "ftp://accounts.google.com/ServiceLogin?service=youtube&uilel=3&passive=true&continue=https%3A%2F%2Fwww.youtube.com%2Fsignin%3Faction_handle_signin%3Dtrue%26app%3Ddesktop%26hl%3Den%26next%3Dhttps%253A%252F%252Fwww.youtube.com%252F&hl=en"
        self.assertEqual(new_prot, solution, "Test url.py: Change protocol on Google Link failed.")
        

        with self.assertRaises(InputError, msg=f"Test url.py: Changed protocol on mini invalid url link."):
            change_protocol("ftp", "https://url")
        
        with self.assertRaises(InputError, msg=f"Test url.py: Changed protocol on basic invalid url link."):
            change_protocol("ftp", "/thisis_https://match.this.url")

        with self.assertRaises(ValueError, msg=f"Test url.py: Added second protocol."):
            add_protocol("ftp", "https://match.this.url")

        with self.assertRaises(InputError, msg=f"Test url.py: Added protocol on invalid url link."):
            add_protocol("ftp", "/thisis_https://match.this.url") #change?

    def test_URL_test(self):
        allowtld = ("edu", "com")
        allowdom = (r"(.*\.)?wiki.org", "cool.com")

        domains = (
            "", "/", "a", "#hey", "bc.de", "wiki.net", "edu.net", "http://now.net", "com://edu.net", "edu.net/upload?file.com",
             "https://edu.net/file?this=new&that=too",

            "research.edu", "anything.com", "http://this.com/service?speed=nice", "wiki.org", "en.wiki.org", 
             "en.wiki.org/hello", "en.wiki.org/hello?this=speed", "ftp://wiki.org/upload?speed=inf", "ftp://cool.com", "https://cool.com",
            )

        for i in range(4):
            with self.assertRaises(InputError, msg=f"Test url.py : URL '{domains[i]}' is_legal_tld should throw because it is not an url."):
                is_legal_tld(domains[i], allowtld)

        for i in range(4, 11):
            self.assertFalse(is_legal_tld(domains[i], allowtld), f"Test url.py: URL '{domains[i]}' Accepted nonpermitted TLD.")

        for i in range(11, len(domains)):
            if i in range(14, 19):
                self.assertFalse(is_legal_tld(domains[i], allowtld), f"Test url.py: URL '{domains[i]}' Accepted nonpermitted TLD.")
            else:
                self.assertTrue(is_legal_tld(domains[i], allowtld), f"Test url.py: URL '{domains[i]}' Denied permitted TLD.")

        for i in range(4):
            with self.assertRaises(InputError, msg=f"Test url.py : URL '{domains[i]}' is_legal_domain should throw because it is not an url."):
                is_legal_domain(domains[i], allowdom)

        for i in range(4, 14):
            self.assertFalse(is_legal_domain(domains[i], allowdom), f"Test url.py: URL '{domains[i]}' Accepted nonpermitted domain.")

        for i in range(14, len(domains)):
            self.assertTrue(is_legal_domain(domains[i], allowdom), f"Test url.py: URL '{domains[i]}' Denied permitted domain.")