import typing


from .BaseProfile import BaseProfile
from webchecks.utils.Error import ValueError
from webchecks.utils.url import extract_domain
from webchecks.utils.messaging import logging
from webchecks.config import LOG_WARNING



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