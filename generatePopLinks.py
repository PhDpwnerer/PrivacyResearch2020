"""
This file generates x amount of most popular submissions between
May 1st and April 1st, 2019.
It then extracts all URLs from these submissions.
It finally saves these URLs in a json file where key=url, and val=frequency.

Note: I say "x" amount, because pushshift limits each request's size to 100,
so I had to try a workaround to generate more, but it ended up generating somewhere
between 1000-2000. In the past, when you don't care about popularity of posts, you 
could get as many posts as you want by sorting your requests by time and keeping track
of the creation time of the last post of the last request. This is not possible here
since we have to sort by popularity instead.
"""

import praw
import requests
from ratelimit import limits, RateLimitException, sleep_and_retry
from backoff import on_exception, expo
from psaw import PushshiftAPI
import csv
import networkx as nx
import re
import json
import pprint
from util import *

links = {}

URL = submissionEndPoint
end_time = 1556668800 #unix epoch for May 1st, 2019
start_time = 1554076800	#unix epoch for April 1st, 2019
before = end_time
batch = 0
while batch <= 100:
	PARAMS = {"size":100, "before":before,"after":start_time,
			  "sort":"desc", "sort_type":"num_comments"}
	r = ratelimitedGet(url=URL, params=PARAMS)
	try:
		info = r.json()
	except Exception as e:
		print(e)
		print(r.text)
	submissions = info["data"]
	print("length of submissions:")
	print(len(submissions))
	#print(submissions)
	if not submissions: break
	before = submissions[-1]["created_utc"]
	for submission in submissions:
		for url in findAllURLs(submission["selftext"]):
			links[url] = links.get(url, 0)+1
	print("batch number %d" % batch)
	batch += 1
	if len(submissions) < 100: break

pprint.pprint(links)

with open('poplinks.json', 'w') as fp:
    json.dump(links, fp)

print("------------ SAVED ------------")