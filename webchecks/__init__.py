"""
WebCheck is a BSD-licensed web search and research tool for searching 
on a given set of domains and some starting web addresses. Basic use:

from webchecks import Project

# Give name and starting address. The latter may be a list of URLs.
proj = Project("project_name", "mywebsite.com/coolsite.html")

# Allowing only the mywebsite.com.
# Note that you can use regular expressions here.
proj.set_allowed_websites("mywebsite.com") 

# Enabling Javascript? Default value is False.
proj.enable_javascript(False)       

# Whether links in retrieved HTML sources should be visited.
# The default value is true. If False only visits the initially given addresses.
proj.enable_crawl(True)

# Default minimum wait in seconds between two requests to the same domain.
# Applies only to domains that have no dedicated profile. (See below.)
proj.set_min_wait(10)

# Default average wait time in seconds between two requests to the same domain.
# The access timing pattern is randomized.
proj.set_avg_wait(10)				

# Translates into seconds. (roughly, will finish last 
# access before shutting down)
proj.run(1000)
"""


from .Project import Project
from .profiles.BaseProfile import BaseProfile


__version__ = "0.1.1"
