"""Provides utilities to extract information and modify URLs."""

import re
from typing import Collection
from mimetypes import guess_type

from .Error import InputError

URL = re.compile(r"^(([a-z]*)://)?(([a-zA-Z0-9\-]+\.)*)([a-zA-Z0-9\-]+)\.([a-z]+)(/.*)?$")

def __extract(url : str):
    if not isinstance(url, str):
        raise InputError("URL is not string type thus not a url.")
    m = re.match(URL, url)
    if not m:
        raise InputError(f"Tried to extract url information from {url}"
            " which appears to be no valid url.")
    return m

def extract_protocol(url : str) -> str:
    """Returns, given some url, the protocol that it uses.
    If there is none present, it will return None.
    If the string passed in is not an url, it will raise an InputError.
    """

    return __extract(url).group(2)

def extract_domain_name(url : str) -> str:
    """Returns, given some url, the domain name.
    If the string passed in is not an url, it will raise an InputError.

    Example:
    
    extract_domain_name('https://hello.world.com/ok') == 'world'
    extract_domain_name('hello.world.com/ok') == 'world'
    """

    return __extract(url).group(5)

def extract_fully_qualified_domain_name(url : str) -> str:
    """Returns the FQDN.
    If the string passed in is not an url, it will raise an InputError.
    """
    subdom = __extract(url).group(3)
    if subdom is None:
        subdom = ""
    return subdom + extract_domain(url)

def extract_domain(url : str) -> str:
    """Returns for given url, the domain.
    If the string passed in is not an url, it will raise an InputError.
    
    extract_domain('https://ok.world.go') == 'world.go'
    """

    return "".join([extract_domain_name(url), ".", extract_tld(url)])

def extract_tld(url : str) -> str:
    """Returns, given some url, the top level domain name.

    If the string passed in is not an url, it will raise an InputError.
    """

    return __extract(url).group(6)

def extract_local_path_and_args(url : str) -> str:
    """Given url, it returns the local path and arguments in the url.

    If the string passed in is not an url, it will raise an InputError.
    """

    s = __extract(url).group(7)
    if s is None:
        return ""
    return s

def add_protocol(protocol : str, url : str) -> str:
    """Adds a protocol to an url that has no protocol yet specified.
    If the url passed in already has a protocol, it will raise a ValueError.
    If the string passed in is not an url, it will raise an InputError.
    """

    m = __extract(url)
    if m.group(2) is not None:
        raise ValueError(f"Url {url} to add protocol {protocol} \
        already has a protocol, {m.group(2)}.")
    return "".join([protocol, "//:", url])

def change_protocol(protocol : str, url : str) -> str:
    """Changes the protocol (if any present) to the given protocol.
    """

    m = __extract(url)

    after = "" if m.group(7) is None else m.group(7)
    return "".join([f"{protocol}://", m.group(3), m.group(5), ".",
        m.group(6), after])

def is_url(url : str) -> bool:
    """For a given string returns whether it has the format of an url.

    If nonstring then False.
    """

    try:
        if __extract(url):
            return True
        return False
    except InputError:
        return False

def is_legal_tld(url : str, allowed_tlds : Collection[str]) -> bool:
    """For given url and a set/tuple/list of permitted tlds returns whether
    the given url has a permitted tld.
    """
    ed = extract_tld(url)
    for ad in allowed_tlds:
        if re.match(ad, ed):
            return True
    return False
    #return extract_tld(url) in allowed_tdls

def is_legal_domain(url : str, allowed_domains : Collection[str]) -> bool:
    """For a given url tells whether its domain is in the set/tuple/list
    of permitted domains.
    InputError if url not str.
    """
    dom = extract_fully_qualified_domain_name(url)
    for ad in allowed_domains:
        if re.match(ad, dom):
            return True
    return False
    #return extract_domain(url) in allowed_domains

def url_is_referencial(url : str) -> bool:
    """Returns bool whether the local URL refers to the same page, just a different section.
    InputError if not str.

    Example:
        '#Summary'
    """
    if not isinstance(url, str):
        raise InputError("url_is_referencial: URL should be string.")
    if url.startswith("#"):
        return True
    return False


def url_is_local(url : str) -> bool:
    """Assumes that the given string must either be a local path or a full url.
    When in doubt, it will treat it as a nonlocal link. 

    TODO this may be bad...
    """

    if url is None:
        return False
    if not is_url(url):
        return True
    # okay LOOKS like a full url...
    # problem: may mistake file extension for a TLD
    if extract_protocol(url) is not None:
        return False # local paths have no protocol
    if extract_local_path_and_args(url) is not None:
        return False # local paths have no further local path

    if guess_type(url)[0] is not None:
        return True # okay the file extension is recognized
    return False

def url_is_superlocal(link : str):
    """ Returns whether the link is 'superlocal': Leaving out just the protocol.
    //okay.com in an href is superlocal. It just copies the protocol.

    If not a string then it will raise an InputError."""

    if not isinstance(link, str):
        raise InputError("url_is_referencial: URL should be string.")
    if link.startswith("//"):
        return is_url(link[2:])
    return False

def merge_url(domain : str, local : str) -> str:
    """Assumes that domain and local are a legitimate url and a legitimate local path,
    respectively."""
    if local == "":
        return domain
    if (domain[-1] == "/" and local[0] == "/"):
        return domain + local[1:]
    if (domain[-1] == "/" or local[0] == "/"):
        return domain + local
    return domain + "/" + local

def merge_ref_url(base : str, ref : str) -> str:
    """Merge a base URL and a local reference ('#...'). Just makes sure that
    there is no '/' inbetween the two.' """
    if base.endswith("/"):
        base = base[:-1]
    if ref.startswith("/"):
        ref = ref[1:]
    return base + ref

def remove_args_from_url(link : str) -> str:
    """Remove the query and the reference from the URL."""
    return (link.split("?")[0]).split("#")[0]

def extract_local_path_without_args(link : str) -> str:
    """Remove domain name, query and local reference from the URL."""
    l = extract_local_path_and_args(link)
    if l == "":
        return ""
    return remove_args_from_url(l)

def strip_query_from_url(url : str) -> str:
    """Deprecated, uses the remove_args_from_url."""
    return remove_args_from_url(url)

def strong_strip_query_from_url(url : str) -> str:
    """Removes the query and local reference from the URL and makes sure that the URL
    does not end with a '/'.
    """
    u = strip_query_from_url(url)
    if u.endswith("/"):
        u = u[:-1]
    return u
