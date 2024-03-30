"""Provides the AccessNode class which is the interface to the user to
access programmatically the results that were previously stored at the
specified project location."""

from typing import List, Set
from webchecks.archive.GlobalCache import GlobalCache
from webchecks.profiles.profileDB import profiledb, fetch_profile
from webchecks.utils.url import extract_fully_qualified_domain_name, strong_strip_query_from_url


class AccessNode:
    """
    Interface that allows you to access the results of the run programmatically.
    """
    def __init__(self):
        self.cache = GlobalCache()

    def registered_domains(self) -> List[str]:
        """Get domains that you can query. (That were visited.)"""
        return list(profiledb.keys())

    def get_urls_visited(self, url : str) -> Set[str]:
        """For a given domain, get the URLs visited."""
        profile = fetch_profile(extract_fully_qualified_domain_name(url))
        return profile.get_urls_visited()

    def get_content(self, url : str) -> str:
        """Get the content fetched from a specific URL.

        TODO: return as bytes option."""
        name = self.cache.get_link_location(strong_strip_query_from_url(url))
        if name is None:
            raise ValueError(f"Url {url} was not found in the cache. Was it really retreived?")
        name = name[0]
        profile = fetch_profile(extract_fully_qualified_domain_name(url))
        return profile.get_archive().retreive_content(name)

    def get_content_location(self, url : str) -> str:
        """Get the local file location where the content behind the given URL is stored."""
        name = self.cache.get_link_location(strong_strip_query_from_url(url))
        if name is None:
            raise ValueError(f"Url {url} was not found in the cache. Was it really retreived?")
        name = name[0]
        profile = fetch_profile(extract_fully_qualified_domain_name(url))
        return profile.get_archive().retreive_content(name, path_only=True)
