"""Reporter class collects information during the run and summarizes
the run at the end, storing the result in REPORTS.txt in the project
directory."""

from typing import Collection, Union
from webchecks.utils.url import extract_fully_qualified_domain_name
from webchecks.utils.singleton import singleton
from .KeywordFinder import KeywordFinder


@singleton
class Report:
    """Reports the results to the user."""
    def __init__(self, project_name : str, root : str,
            initial_seed_urls : Union[str, Collection[str]]):
        self.recv = []
        self.keywords = None
        self.project_name = project_name
        self.root = root
        self.initial_seed_urls = initial_seed_urls
        self.kwfinder = KeywordFinder()


    def setup(self, keywords : Union[str, Collection[str]]):
        """Enter the Keywords. This feature is not yet mature and thus has no effect yet.

        Parameters:
        -------------
        keywords : str or Collection of str
            Not yet used.
        """
        self.keywords = keywords
        #self.kwfinder.set_keywords(keywords)

    def report(self, url : str):
        """Report another URL that was visited.
        
        Parameters:
        -------------
        url : str
            The url ot be reported.
        """
        self.recv.append(url)

    # def report_received(self, url : str, resp_header : dict, content : bytes,
    #         filelocation : str, fext : str):
    #     #Report data that was received. Can be used to then do small analysis on.
    #     #Not yet mature, has no effect. (Needs Keyword feature.)
    #     # Still some fixing to be done here.
    #     #if fext in ('html', '.html'):
    #     #    self.kwfinder.html_hit(url, resp_header, content, filelocation)
    #     return

    def _get_dom_report(self) -> str:
        """Return string of all URLs visited."""
        s = {}
        for url in self.recv:
            fqdn = extract_fully_qualified_domain_name(url)
            try:
                s[fqdn] += 1
            except KeyError:
                s[fqdn] = 1
        ret = ""
        for (key, value) in s.items():
            s1 = key
            s2 = str(value)
            if len(s1) < 65 - len(s2):
                s1 = s1.ljust(65 - len(s2))
            ret = "".join((ret, s1, " ", s2, "\n"))
        return ret

    def print(self) -> str: # pragma: no cover
        """Return a string with the report."""
        domains = "\t" + self._get_dom_report()
        domains = domains.replace("\n", "\n\t")
        keywords = "None"
        links = ""
        for url in self.recv:
            links = "".join((links, "\t", url, "\n"))

        init = str(self.initial_seed_urls[0]).rjust(55)
        for i in range(1, len(self.initial_seed_urls)):
            init = "".join((init, "\n", str(self.initial_seed_urls[i]).rjust(70)))

        if self.keywords is not None:
            keywords = str(self.keywords)[1:-1]

        kwmsg = ""
        if self.keywords is not None:
            kwhits = "\t"
            for ids in self.kwfinder.get_hits():
                kwhits = "".join((kwhits, ids, "\n\t"))
            # pylint: disable-next=line-too-long
            kwmsg = f"""_______________________________________________________________________________

Number of Keyword Hits: {str(self.kwfinder.num_hits()).rjust(46)}

Newly Identified Hits:
{kwhits}
"""

        return f"""
SCRAPING REPORT: Project '{self.project_name}'
===============================================================================

Initial Seeds: {init}

Keywords: {keywords.rjust(60)}
_______________________________________________________________________________           

Targeted Websites:
    
    Domain Name                                               Number of URLs
    ------------------------------------------------------------------------
{domains}

Number of fetched links: {str(len(self.recv)).rjust(45)}
{kwmsg}_______________________________________________________________________________

Visited Links:
{links}

===============================================================================
"""
