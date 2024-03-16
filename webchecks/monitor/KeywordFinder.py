
import re
from bs4 import BeautifulSoup
from webchecks.utils.file_ops import binary_to_text

class KeywordFinder(object):
    """NOT YET FULLY IMPLEMENTED: For now."""

    def __init__(self):
        self.keywords = None
        self.hits = []

    def get_hits(self):
        for id in self.hits:
            yield id
    
    def num_hits(self):
        return len(self.hits)

    def set_keywords(self, keywords):
        self.keywords = []
        for key in keywords:
            self.keywords.append(re.compile(key))

    def html_hit(self, url, resp_header, html, identifier):
        
        # find common stuff
        if type(html) == bytes:
            html = binary_to_text(html)
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text()

        for key in self.keywords:
            if re.search(key, text):
                self.hits.append(identifier)
                return True
        return False

    


