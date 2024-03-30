"""Provides a store for all profiles."""

from webchecks.utils.url import extract_domain
from webchecks.utils.messaging import logging
from webchecks.config import LOG_WARNING
from .BaseProfile import BaseProfile



profiledb = {}

def add_profile(profile):
    """Add profile."""
    profiledb[profile.get_domain()] = profile

def fetch_profile(domain : str):
    """Fetch a profile from the DB."""
    try:
        return profiledb[domain]
    except KeyError:
        # first, try base domain. without subdomain
        try:
            return profiledb[extract_domain(domain)]
        except KeyError:
            logging(f"Domain {domain} has no profile. Using a default profile.", LOG_WARNING)
            profiledb[domain] = BaseProfile(domain)
            return profiledb[domain]
