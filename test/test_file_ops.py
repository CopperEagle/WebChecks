 
import unittest

from webchecks.utils.file_ops import *

class URLCase:
    def __init__(self, url, ext, fp):
        self.url = url
        self.ext = ext
        self.fp = fp


class FileOpsTest(unittest.TestCase):

    cases = [
        # same extension
        URLCase("ok.com/html.txt", "txt", "html.txt"),
        URLCase("ok.com/jey/html.txt", ".txt", "jey_html.txt"),
        URLCase("https://ok.com/this.js?this=query", "js", "this.js"),
        URLCase("https://ok.com/dfjfadc89n3z932z93bz3298zb393z29832z893cz3cn382z43"
            "8z3984z3249832zn3z4z44382zn8c43zn432n9c329znc3z98n2c398cz3294839z43289"
            "c4zn389z4cz3298cz3894nz324893zc483382cz2984z32c4849czncr84z98z3832cn32"
            "89z832z4c983z48cnz3ncnz834zn32894c8nz849vn48vz489xm983xz38zx439zn4x28.js", "js", 
            "dfjfadc89n3z932z93bz3298zb393z29832z893cz3cn382z438z3984z3249832zn3z4z44"
            "382zn8c43zn432n9c329znc3z98n2c398cz3294839z43289c4zn389z4cz3298cz3894nz324893z.js"),

        # switching extensions
        URLCase("ok.com/this.js", "png", "this.js.png"),
        URLCase("ok.com/this.js", ".png", "this.js.png"),
        URLCase("https://ok.com/this.js", "png", "this.js.png"),
        URLCase("https://ok.com/this.js?this=query", "png", "this.js.png"),
        URLCase("https://subdom.ok.com/this.js?this=query", "png", "this.js.png"),
        URLCase("https://ok.com/", "html", "MAINPAGE.html"),
        URLCase("https://ok.com", "html", "MAINPAGE.html"),
        URLCase("https://ok.com/dfjfadc89n3z932z93bz3298zb393z29832z893cz3cn382z43"
            "8z3984z3249832zn3z4z44382zn8c43zn432n9c329znc3z98n2c398cz3294839z43289"
            "c4zn389z4cz3298cz3894nz324893zc483382cz2984z32c4849czncr84z98z3832cn32"
            "89z832z4c983z48cnz3ncnz834zn32894c8nz849vn48vz489xm983xz38zx439zn4x28.mj", "js", 
            "dfjfadc89n3z932z93bz3298zb393z29832z893cz3cn382z438z3984z3249832zn3z4z44"
            "382zn8c43zn432n9c329znc3z98n2c398cz3294839z43289c4zn389z4cz3298cz3894nz324893z.js"),
        



    ]

    def test_binary(self):

        self.assertEqual(b"AB0\x12", text_to_binary("AB0\x12"))
        self.assertEqual("AB0\x12", binary_to_text(b"AB0\x12"))

    def test_get_name(self):
        for case in self.cases:
            self.assertEqual(get_file_name_from_url(case.url, case.ext), case.fp, "Testing file_ops.py: get_name_from_url error.")

    def test_fmt_guess(self):
        for i in range(4):
            case = self.cases[i]
            self.assertTrue(refd_content_may_have_fileformat(case.url, case.ext), f"Testing file_ops: URL '{case.url}' is indeed '{case.ext}'")

        for i in range(4, len(self.cases)):
            case = self.cases[i]
            self.assertFalse(refd_content_may_have_fileformat(case.url, case.ext), f"Testing file_ops: URL '{case.url}' is not necessarily '{case.ext}'")

        case = URLCase("/ok.com/html.txt", "txt", "html.txt")
        self.assertTrue(refd_content_may_have_fileformat(case.url, case.ext))

    def test_hash(self):
        self.assertEqual(hash_string(b"hello"), b']A@*\xbcK*v\xb9q\x9d\x91\x10\x17\xc5\x92')
        self.assertEqual(hash_string("hello"), b']A@*\xbcK*v\xb9q\x9d\x91\x10\x17\xc5\x92')


    def test_guess_header(self):
        header = {"content-type" : None, "content-Type" : None,
        "Content-type" : None, "Content-Type" : None}
        self.assertEqual(get_file_type_from_response_header(header, False), ("", ""))

        header = {"content-type" : "text/html", "content-Type" : None,
        "Content-type" : None, "Content-Type" : None}
        self.assertEqual(get_file_type_from_response_header(header, False), ("text", ".html"))

        header = {"content-type" : b"text/html", "content-Type" : None,
        "Content-type" : None, "Content-Type" : None}
        self.assertEqual(get_file_type_from_response_header(header, True), ("text", ".html"))

        header = {"content-type" : b"text/html;", "content-Type" : None,
        "Content-type" : None, "Content-Type" : None}
        self.assertEqual(get_file_type_from_response_header(header, True), ("text", ".html"))

        header = {"content-type" : b"", "content-Type" : None,
        "Content-type" : None, "Content-Type" : None}
        self.assertEqual(get_file_type_from_response_header(header, True), ("", ""))

        header = {"content-Type" : None,
        "Content-type" : None, "Content-Type" : None}
        with self.assertRaises(KeyError):
            get_file_type_from_response_header(header, True)
        get_file_type_from_response_header(header, False)