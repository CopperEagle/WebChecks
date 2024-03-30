# Basic Use
Basic use is fairly straight forward. *ALMOST ALL* calls the user performs is using the Project class.

```python
from webchecks import Project

# Give name and starting address. The latter may be a list of URLs.
proj = Project("project_name", "mywebsite.com/coolsite.html")

# Allowing to visit mywebsite.com and all wikipedia sites, regardless of language, 
# like en.wikipedia.org. Note that you can use regular expressions here.
proj.set_allowed_websites((r"(.*\.)?wikipedia\.org", "mywebsite.com")) 

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
```
This will set the initial roots of your search at mywebsite.com/coolsite.html and it will fallow any links on that website provided that they are allowed by the security policy you define. The above security policy is fairly simple: You specify just what websites you allow the tool to visit and you disallow Javascript.

Once finished, there will be a REPORT.txt file in the project directory.
It will summarize the scraping process. The file is also printed on the terminal.

## Multiple Starting points

Note that you can also specify multiple "initial root urls" from which you start gathering webpages.
```python
from webchecks import Project

# Give name and starting address. The latter may be a list of URLs.
proj = Project.Project("project_name", ("SiteA.com", "SiteB.com"))
```

## Timeout and Data compression

The fallowing settings set the timeout value in seconds and whether text (HTML) should be compressed before stored.
```python
proj.set_timeout(240)               # Timeout of request. In seconds. Default is 20.
proj.set_compress_text(True)        # Compress html. Default is True.
```

## Troubleshooting

If you enable Javascript, it will use Seleniumwire and the Firefox driver. Now in some cases you may want to explicitly specify the location of the driver or the Firefox profile to use (e.g. on Ubuntu when managing Firefox using snap). Use 
```python
proj.set_browser_driver_location('...geckodriver/linux64/v0.XX.0/geckodriver')
proj.set_browser_use_profile('...snap/firefox/common/.mozilla/firefox/dhdfjksdh.default')
```

# Security Policy
A user should specify several things:
- Is Javascript used? Use the *project.enable_javascript* method. 
- Set Websites that are allowed to be visited. Use the *project.set_allowed_websites* 
- If Javascript is allowed, the user can optionally specify from what sources Javascript can be run.

The case if JS is disabled is demonstrated in the first code example above. The fallowing is an example if Javascript is enabled:

```python
proj.set_allowed_websites((r"(.*\.)?wikipedia\.org", "mywebsite.com"))
proj.enable_javascript(True)

# If you allow Javascript, you can manage what sources you allow to run JS.
# Reset defaults:
proj.sec_reset_javascript_permissions_for_domains() # Now all sources are allowed to run.

# Blacklist any domain by default:
proj.sec_set_disallow_javascript_for_domain("*")

# Explicitly whitelist wikipedia.org. This automatically includes any subdomain like 'en.wikipedia.org'
proj.sec_set_allow_javascript_for_domain("wikipedia.org")
```

Note that all methods concerning the security policy except *enable_javascript* and *set_allowed_websites* start with "sec". Check the documentation for the Project class to find more options.

# Accessing the results

By default, it currently stores all pages in a correspnding directory.
The root of that directory is the project directory specified when
creating the Project object. You can check out the results there, especially 
if you do not compress the text data, i.e. ```proj.set_compress_text(False)```
Alternatively, you can access the results in the code directly, using the AccessNode interface:

```py
# assume proj object from above
## ... proj.run(1000)

# from webchecks.archive.AccessNode import AccessNode

# returns AccessNode
acc = proj.access_node()

# Domains that were visited during scraping or
# were given a profile by the user.
print(acc.registered_domains())		

# Set of visited URLs. Can use to get the content. See next line.
print(acc.get_urls_visited("mywebsite.com"))


# Provided that this wesbite was visited, it will return the results
# that were fetched. Automatically decompresses text if applicable.
print(acc.get_content("mywebsite.com/coolsite.html"))

# Will return WHERE in the project folder that website is stored.
print(acc.get_content_location("mywebsite.com/coolsite.html"))

```

# Profiles

Custom Profiles are created by extending the BaseProfile class. Then, the profile is installed using the Project object.
You can install one profile per domain. When extending, three methods are of interest. You can use the code below as a template.

```py
import typing
from webchecks.profiles.BaseProfile import BaseProfile

class CustomProfile(BaseProfile):
    def __init__(self):
        super(CustomProfile, self).__init__("mydomain.com")

        # Each domain has their own timer. The line below specifies the waiting behavior for this domain.
        # Thus, this is specifying the access behavior.
        # access pattern algorithms available:
        # ACCESS_EQUISPACED:  			Every domain gets exactly one request per average wait time
        # ACCESS_EXPONENTIAL_RND: 		The request pattern to any domain follows an exponential distribution with the given average wait time (but here it is randomized)
        # ACCESS_EXPONENTIAL_RND_MIN	Like above but additionally it respects the minimum wait time between requests to a domain 
        access_pattern = ACCESS_EXPONENTIAL_RND_MIN
        avg_wait_after_request = 25 # seconds per domain
        min_wait_after_request = 20 # seconds per domain

        self._set_access_algorithm(access_pattern, avg_wait_after_request, min_wait_after_request)
        self._modify_header("header-entry", "value") # used for the requests where JS is disabled.
        # ...

    def get_links(self, url : str, html_source : str):
        """For a given website and corresponding URL, choose what links to extract and
        to click next (inserting into the sending queue).

        Parameters
        ---------
        url : str
            URL of the html source at hand.
        html_source : str 
            The HTML source
        """
        links = []

        # ... use html_source (enter your code)

        return self._register_urls(links) # mandatory

    def consume_retreived_content(self, url : str, resp_header : dict, content : bytes):
        """After a webaccess happened, this function is called. The main purpose is to
        process the data and store it.

        Parameters
        ---------
        url : str
            URL that was accessed
        resp_header : dict
            The HTTP response header.
        content : bytes
            The actual data that was received.
        """
        self._deregister_url(url) # mandatory

        # ... process content (enter your code)

        metadata = f"Retrived {time.asctime()}\nURL {url} ..."
        filename = self.archive.save_content(url, resp_header, content, metadata)

proj.install_profile(CustomProfile())
```

# Default settings

You can see all default values in the docstrings of the Project class (type help(Project) in the terminal).
All default settings are defined inside webchecks.config. You can check them out. Some settings cannot be changed yet through the Project interface. Thus, it is generally recommended to leave these settings. *Do not change the config dictionary directly.*
```py
from webchecks.config import config
print(config)
```

