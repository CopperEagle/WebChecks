"""Provides utilities for dealing with string/binary and files."""


import re
from hashlib import md5
from typing import Tuple
from mimetypes import guess_all_extensions, guess_type, guess_extension
from .Error import InputError
from .url import extract_local_path_without_args, remove_args_from_url


def text_to_binary(text : str) -> bytes:
    """Convert a UTF-8 encoded string into binary."""
    return bytes(text, "utf-8")

def binary_to_text(text : bytes) -> str:
    """Convert bytes to UTF-8 encoded str"""
    return text.decode("utf-8")

def get_file_name_from_url(url : str, fext : str = "") -> str:
    """Gets the file name of the webresource that is pointed to by the URL.
    Optionally will ensure that the file name ends with a specified file extension.
    If empty (e.g. https://domain.com/), it will return MAINPAGE with optional file extension.

    Parameters:
    -------------
    url: str
        The URL of that resource.
    fext: str
        Some file extension like 'js' or '.txt'
    """
    if fext != "" and not fext.startswith("."):
        fext = "." + fext
    path = extract_local_path_without_args(url)
    if path in ("/", ""):
        return f"MAINPAGE{fext}"
    if path.startswith("/"):
        path = path[1:]
    path = path.replace("/", "_")
    if not path.endswith(fext):
        path = path + fext
    #print(f"For {url} returned name {path}")
    if len(path) > 150: # there are some maximums...
        path = (fext.join(path.split(fext)[:-1]))
        path = path[:150]
        path = path + fext
    return path


_FILE = re.compile(r"(.*)\.([a-zA-Z0-9\-]+)")

# pylint: disable-next=unused-argument
def refd_content_may_have_fileformat(url : str, fmt : str, content = None) -> bool:
    """Tries to guess, given just the url, the file type that the request to that
    url would return. Keep in mind that this cannot be definitively answered 
    just using the url as urls may resolve even nondeterministically, url usually
    specify no file format at all, etc. If true then you know it likely is, if 
    False it may still be but potentially unlikely.
    
    Ignores the content.

    Parameters:
    -------------
    url: str
        The URL of that resource.
    fext: str
        Some file extension like 'js' or '.txt'
    content: DEPRECATED
    """

    if not fmt.startswith("."):
        fmt = "." + fmt
    if guess_type(url)[0] is None:
        try:
            lp = remove_args_from_url(url)
            if lp == url:
                return False
            return refd_content_may_have_fileformat(lp, fmt) 
        except InputError:
            return False
    return fmt in guess_all_extensions(guess_type(url)[0], False)



def hash_string(s : str) -> str:
    """Hashes a string using MD5."""
    if isinstance(s, str):
        s = s.encode("utf-8")
    return md5(s).digest()


def get_file_type_from_response_header(header : dict, throw_error : bool = True) -> Tuple[str, str]:
    """Given the header, it will try to guess the file type of the data returned.
    If no data is there or the header is invalid, it optionally throws the error
    if throwError is specified.

    Returns a tuple (file_type, guessed_extension)
    where file_type is the mime file type and guessed_extension is the 
    corresponding file extension

    Parameters:
    -------------
    header: dict
        Response header.
    throw_error: str
        Throw an error if header is invalid or the header belongs to a response without data.

    """
    try:
        fc = header["content-type"]
        if fc is None: # weird server?

            if header["Content-type"] is not None:
                fc = header["Content-type"]

            elif header["content-Type"] is not None:
                fc = header["content-Type"]

            elif header["Content-Type"] is not None:
                fc = header["Content-Type"]

            else:
                return ("", "")

        if isinstance(fc, bytes):
            fc = binary_to_text(fc)

        if ";" in fc:
            fc = fc.split(";")
            for elt in fc:
                if "/" in elt:
                    fc = elt
                    break
        ft = fc.split("/")[0]
    except:
        if throw_error:
            raise
        return ("", "")
    guess = guess_extension(fc)
    if guess is None:
        return (ft, "")

    return ft, guess
