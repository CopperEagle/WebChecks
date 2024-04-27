# WebChecks

[![Python](https://img.shields.io/badge/Python-3.10-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
![Version](https://img.shields.io/badge/Webchecks_version-0.1-darkgreen)
[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![Linting: Pylint](https://img.shields.io/badge/linting-pylint-green)](https://github.com/pylint-dev/pylint)

![Linting Score](https://img.shields.io/badge/Linting_score-9.52/10.0-green)
![Test Coverage](https://img.shields.io/badge/Test_coverage-87%25-green)

## The project - goals

WebCheck is a BSD-licensed web search and research tool for searching on a given set of domains given some starting web addresses. It has three goals:

- Easy steerability to ensure ethical scraping practices and effectively achieving set goals. This is in part achieved by offering an extensible per (sub)domain profile system allowing to precisely define digital behaviour, access pattern / access frequency amongst other things. *It mandatorely respects robots.txt.* (No, there is no option to disable that.)

- Scaling over time: A given Project can merge the results of diffrent scraping runs in a structured manner and allows  easy adaption of the rules in between.

- Ample options to ensure safety: Not only does it provide the user to opt out Javascript, it also allows to set a policy **from which sources Javascript is allowed to run**. The user can specify which domains can be visited, which ones not.

The tool was written about one and a half year ago as a side project.

## Intended uses

**This tool is NOT intended to scrape many websites to create large datasets** (e.g. for AI/LLMs). This is simply not the purpose of this tool: It is not intended and does not scale over several machines or large datagrabs.

It's main use is to help research and decisionmaking by collecting some information given some clearly defined interest topics or websites, etc.

Examples may be to regularely check a set of news sites and filter for reports on local disease outbreaks, which may help projects like proMEDmail. Such (*enter your topic*) awareness projects usually have a small staff which also needs to do human networking etc. Given we live in the world where change accelerates (including content generation), keeping track of all of it may become more challenging and important.

## Features and Todos

Features:
- Allows scraping many diffrent domains in one go.
- Optional Javascript. If enabled, it will require Seleniumwire (allows intercepting requests). Can optionally specify per domain whether to allow running Javascript from that domain. See Limitations.
- Adding per-(sub)domain profiles that allows to specify some of the fallowing: Access frequency, allowed links (besides robots.txt), managing the result (fetched content). It may also modify the header sent to the server. Websites without user defined profile will have a reasonable default Profile.

Limitations:
- Currently the inline javascript on the html page itself will be executed, *even if this domain is disallowed to execute JS*. This is because disallowing it requires editing HTML pages midflight and may break it. 

Todos:
- Currently the Scraper will remember which websites it has already visited and will not revisit them again. Sometimes, however, it may be interesting to allow revisits to this page after some time has passed.
- Currently the Javascript feature only allows using the Firefox browser. This should be an easy fix. Currently there is just little time to do it.
- More tests
- Keywords feature not yet usable.


## Installing it

Requires Python 3.10+. Optionally, you may create a virtual environment using

```bash
python3 -m venv path/to/new/venv
cd path/to/new/venv
source bin/activate
```

Then do

```bash
pip3 install webchecks
```

or download the code, navigate into that directory and run

```bash
pip3 install -r requirements.txt
pip3 install .
```

Note: If you require Javascript then make sure you have Firefox because this is what is being used currently by this project.

## How to use it

Basic use is fairly straight forward. *ALMOST ALL* calls the user performs is using the Project class.
For more examples and how to programmatically access the results, enable compression, using profiles, etc. check out [the tutorial](TUTORIAL.md).

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
This will set the initial roots of your search at mywebsite.com/coolsite.html and it will follow any links on that website provided that they are allowed by the security policy you define. The above security policy is fairly simple: You specify just what websites you allow the tool to visit and you disallow Javascript.

Once finished, there will be a REPORT.txt file in the project directory.
It will summarize the scraping process. The file is also printed on the terminal.


## Questions and Contibuting

For any questions or issues, just open an issue.


## Notes

It is in your responsibility to make sure you comply with the website's TOS when using this tool. There is no warranty whatsoever. The code is covered by the BSD-3-Clause license, and the license is included in this repository.

