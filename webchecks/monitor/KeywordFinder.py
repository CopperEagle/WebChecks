"""Implements the searching functionality with the KeywordFinder class. 
Not yet implemented."""

import re
from bs4 import BeautifulSoup
from webchecks.utils.file_ops import binary_to_text

class KeywordFinder: # pragma: no cover
    """NOT YET FULLY IMPLEMENTED: For now."""

    def __init__(self):
        self.keywords = None
        self.hits = []

    def get_hits(self):
        """Returns webpages that have a keyword."""
        yield from self.hits

    def num_hits(self):
        """Returns number webpages that have one of the specified keywords."""
        return len(self.hits)

    def set_keywords(self, keywords):
        """Set the keywords."""
        self.keywords = [re.compile(key) for key in keywords]

    def html_hit(self, url, resp_header, html, identifier):
        """Find keywords."""
        if not url or not resp_header: ## eh?..
            return False
        # find common stuff
        if isinstance(html, bytes):
            html = binary_to_text(html)
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text()

        for key in self.keywords:
            if re.search(key, text):
                self.hits.append(identifier)
                return True
        return False
