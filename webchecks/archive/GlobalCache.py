"""Provides the GlobalCache class, a persistent cache for the entire project."""

import os
import time
import sqlite3
from typing import Tuple, Union
from webchecks.utils.file_ops import hash_string
from webchecks.utils.singleton import singleton
from webchecks.config import config, CACHE_STORAGE_LOCATION

DURATION_DAY = 60 * 60 * 24


@singleton
class GlobalCache:
    """Persistent file cache singleton service that is to be used for all profiles. Allows to
    cache files spanning multiple runs."""

    def __init__(self):
        self.root = config[CACHE_STORAGE_LOCATION]
        self._locate_dir()
        self.metadb = os.path.join(self.root, "meta.db")
        create_db = not os.path.exists(self.metadb)
        self.db = sqlite3.connect(self.metadb)
        if create_db:
            #print("Creating DB")
            self._create_db()

    def __del__(self):
        self.db.commit()
        self.db.close()

    def _locate_dir(self):
        try:
            os.makedirs(self.root)
        except:
            pass

    def _create_db(self):
        cu = self.db.cursor()
        cu.execute("CREATE TABLE metadata(domain, name, hash, sec_before_refresh)")
        cu.execute("CREATE TABLE links(weblink, localfilelink)")

    def store_link_location(self, weblink : str, localfilelink : str):
        """
        Store a mapping between the URL and the corresponding local link where
        the content retreived is stored.

        Parameters:
        -------------
        weblink : str
            The URL.
        localfilelink : str
            The location where the content is stored.
        """
        cu = self.db.cursor()
        cu.execute("INSERT INTO links VALUES (?, ?)",
            (weblink, localfilelink))
        self.db.commit()

    def get_link_location(self, weblink : str) -> str:
        """
        Get the local location where the content for a given URL is stored. 
        None if it is not stored.

        Parameters:
        -------------
        weblink : str
            The URL for which the local address is needed.
        """
        cu = self.db.cursor()
        for link in cu.execute("SELECT localfilelink FROM links WHERE weblink = ?", (weblink,)):
            return link
        return None

    def store(self, domain : str, content : Union[str, bytes], name : str,
            sec_before_refresh : Union[int, float]) -> Union[None, str]:
        """
        Store (cache) some content.
        Returns the hash of the content stored or None if not stored.
        (It refuses to store if sec_before_refresh <= 0, see below.)

        Parameters:
        -------------
        domain : str
            The domain name for which the content is to be stored. Allows to prevent clashes
            between domains.
        content : str or bytes
            The data to be stored.
        name : str
            The name which will be used to retreive this content later.
        sec_before_refresh : int or float
            When the data will no longer be valid, in seconds.
            If negative or 0, it will return None and will not store.

        """
        if 0 >= sec_before_refresh:
            return None

        sec_before_refresh += time.time()
        filehash = hash_string(content)
        filepath = os.path.join(self.root, domain)
        try:
            os.makedirs(filepath)
        except:
            pass
        filepath = os.path.join(filepath, name)
        mode = "wb" if isinstance(content, bytes) else "w"
        with open(filepath, mode) as f:
            f.write(content)
        cu = self.db.cursor()
        cu.execute("INSERT INTO metadata VALUES (?, ?, ?, ?)",
            (domain, name, filehash, sec_before_refresh))
        self.db.commit()
        return filehash

    def load(self, domain : str, name : str,
            is_binary : bool = False) -> Tuple[Union[None, str, bytes], Union[None, str]]:
        """
        Load the file. Returns (content, hash_of_content). (None, None) if not found or expired.

        Parameters:
        -------------
        domain : str
            The domain name under which this was stored.
        name : str
            The name of the content itself.
        is_binary : bool
            Whether the content is binary or not.
        """
        cu = self.db.cursor()
        query = cu.execute(
            "SELECT sec_before_refresh FROM metadata WHERE name = ? AND domain = ?",
            (name, domain)
            )

        for sbr in query:
            if time.time() > sbr[0]:
                cu.execute(
                    "DELETE FROM metadata WHERE name = ? AND domain = ?",
                    (name, domain)
                )
                self.db.commit()
                return (None, None)

        filepath = os.path.join(self.root, domain, name)
        mode = "rb" if is_binary else "r"
        join = b"" if is_binary else ""
        try:
            with open(filepath, mode) as f:
                content = join.join(f.readlines())
                return (content, hash_string(content))
        except:
            return (None, None)

    def get_hash(self, domain : str, name : str) -> Union[None, str]:
        """
        Get the hash of some content that was stored previously.
        Parameters:
        -------------
        domain : str
            The domain name under which this was stored.
        name : str
            The name of the content itself.
        """
        cu = self.db.cursor()
        query = cu.execute(
            "SELECT sec_before_refresh, hash FROM metadata WHERE name = ? AND domain = ?",
            (name, domain)
            )
        for sbr, filehash in query:
            if time.time() > sbr:
                cu.execute(
                    "DELETE FROM metadata WHERE name = ? AND domain = ?",
                    (name, domain)
                )
                self.db.commit()
                return None
            return filehash
        return None
