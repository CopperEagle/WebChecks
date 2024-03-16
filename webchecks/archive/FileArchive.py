
import os
import typing
import pickle
import atexit
from typing import Callable, Any, Union, Set
from lzma import compress, decompress, LZMAError

from .GlobalCache import GlobalCache
from webchecks.utils.file_ops import get_file_name_from_url, get_file_type_from_response_header
from webchecks.monitor.Report import Report
from webchecks.utils.url import strong_strip_query_from_url
from webchecks.utils.messaging import logging
from webchecks.config import config, COMPRESS_CONTENT, RESULT_STORAGE_LOCATION, \
        DEFAULT_PER_PROFILE_CONTENT_STORAGE_LOCATION, LOG_ERROR



class FileArchive(object):
    """Manages an isolated storage location for a profile (domain).
    Handles organisation, storing and retreiving of content and metadata using the filesystem.
    Also allows to store other data relevant for the profile such as the set of visited links.
    Allows for compression."""
    def __init__(self, profile):
        root = os.path.join(
			config[RESULT_STORAGE_LOCATION],
			config[DEFAULT_PER_PROFILE_CONTENT_STORAGE_LOCATION].replace(
				"%PROFILE_DOMAIN_NAME", profile.get_domain()
			)
		)
		
        self.content_dir = os.path.join(root, "content")
        self.meta_dir = os.path.join(root, "metadata")
        self.visited_links_path = os.path.join(self.meta_dir, "store_visited_links.dump")
        self._locate_dir(self.content_dir)
        self._locate_dir(self.meta_dir)
        self.profile = profile
        self.reporter = Report()
        self.cache = GlobalCache()

    def _locate_dir(self, location):
        logging(f"Creating {location}")
        try:
            os.makedirs(location)
        except:
            pass

    def load_links_visited(self) -> Set[str]:
        """Load and return the set of links that were visited.
        If, during the previous run, the profile has handed it over
        using save_at_shutdown, then it will return that set. Otherwhise
        it will return the empty set."""
        try:
            links_visited = self.load_saved_at_shutdown(self.visited_links_path)
            logging(f"Successfully loaded visited links for {self.profile.get_domain()}.")
        except FileNotFoundError:
            links_visited = set([])
        return links_visited

    def load_saved_at_shutdown(self, location : str) -> Any:
        """Load an Object that was previously stored using the 'save_at_shutdown' method.

        Parameters:
        ------------
        location: str
            Location of the object ot be retreived.
        """
        with open(location, "rb") as f:
            return pickle.load(f)

    def _save_at_shutdown(self, func, location):
        with open(location, "wb") as f:
            pickle.dump(func(), f)

    def save_at_shutdown(self, func : Callable[None, Any], location : Union[str, None] = None):
        """Handle over a function that is executed upon shutdown and whose result will be stored
        at the specified location. 

        Parameters:
        -------------
        func: Callable None -> Any
            The function to be called upon shutdown,
        location: str or None
            The location where the output is to be stored. If None, then it will default
            to the location for the visited links.
        """
        if location is None:
            location = self.visited_links_path
        atexit.register(self._save_at_shutdown, func, location)     

    def compress(self, text : bytes) -> bytes:
        """Compress some sequence of bytes.
        
        Parameters:
        -------------
        text: bytes
            The text to be compressed.
        """
        return compress(text)
        
    def decompress(self, text : bytes) -> bytes:
        """
        Decompress sequence of bytes.
        Parameters:
        -------------
        text: bytes
            The text to be decompressed.
        """
        
        try: # for all reasons, text should be bytes... optimistic try
            return decompress(text)
        except TypeError: # unless user at profile level did some ops...
            if type(text) == str:
                return decompress(text.encode("utf-8"))
            raise
        except LZMAError: # some legacy support
            return decompress(bytes.fromhex(text))
    
    def retreive_content(self, fpath : str, path_only : bool = False, metadata : bool = False) -> str:
        """
        Retreive some content at a given file path. Raises FileNotFoundError if the file cannot be found.

        Parameters:
        -------------
        fpath : str
            The filepath.
        path_only : bool
            Returns the file path after sanitization. The latter includes rewriting
            a link to be relative to the root project directory and checking
            if it exists. (FileNotFoundError if not.)
        matadata : bool
            Return (project) metadata of that file.
        """
        fpath = self._sanitize_fpath(fpath)        
        if path_only:
            return fpath

        meta_dir = fpath.split("content/")
        meta_dir = "".join((meta_dir[0],"content/", meta_dir[1], "metadata/", "content/".join(meta_dir[2:]), ".txt"))
        md = self._read(meta_dir)
        if metadata:
            return md
        
        decompress = "True" in md.split("\n")[0]
        
        if decompress:
            return self.decompress(self._read(fpath, "rb"))
        return self._read(fpath)


    def save_content(self, url : str, resp_header : dict, content : bytes, metadata : str = ""):
        """Save the content retreived from a given URL.

        Parameters:
        -------------
        url : str
            The url for that content.
        resp_header : dict
            The response header of that request.
        content : bytes
            The data retreived.
        metadata : str
            Additional metadata that should be included.

        """
        try:
            ftype, fext = get_file_type_from_response_header(resp_header)
        except ValueError:
            logging(f"Unsupported filetype from {resp_header}. Will not be stored.", LOG_ERROR, where = "FileArchive.save_content")
            return # do not save, not yet supported.
        name = get_file_name_from_url(url, fext)
        fn = os.path.join(self.content_dir, name)
        self.cache.store_link_location(strong_strip_query_from_url(url), name)
        #self.reporter.report_received(url, resp_header, content, fn, fext)

        compressed = False

        if config[COMPRESS_CONTENT] and ftype == "text":
            if type(content) == str:
                content = text_to_binary(content)
            content = compress(content)
            compressed = True
        
        wtype = "w" if type(content) == str else "wb"
        with open(fn, wtype) as f:
            fsize = f.write(content)
        
        self._save_metadata(url, metadata, name + ".txt", compressed, fsize)
        return name

    def _save_metadata(self, url : str, msg : str, fname : str, compressed : bool, fsize : int):
        header = f"compressed : {compressed}\nname : {fname}\nbytes : {fsize}\n"
        msg = "".join((header, msg))
        fname = os.path.join(self.meta_dir, fname)
        with open(fname, "w") as f:
            f.write(msg)

    def _read(self, fpath, mode = "r"):
        base = "" if mode == "r" else b""
        with open(fpath, mode) as f:
            return base.join(f.readlines())
    
    def _sanitize_fpath(self, fpath):
        if not os.path.exists(fpath):
            try1 = os.path.join(self.content_dir, fpath)
            if os.path.exists(try1):
                return try1
            try2 = os.path.join(self.meta_dir, fpath)
            if os.path.exists(try2):
                return try2
            raise FileNotFoundError(f"Cannot find file {fpath} for domain {self.profile.get_domain()}")
        return fpath

