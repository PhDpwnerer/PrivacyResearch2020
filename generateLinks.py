"""
generates 1 million random posts.
extracts URLs from them
saves them in a json file where key=url, and val=frequency
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
from util import *

a = [make_id() for i in range(1000000)]

links = {}

for i in range(2000):
	print("batch # %d" %(i+1))
	URL = submissionEndPoint
	PARAMS = {"ids": a[500*i: 500*(i+1)]}
	r = ratelimitedGet(url = URL, params = PARAMS)
	try:
		info = r.json()
	except Exception as e:
		print(e)
		print("generating random submissions")
		print(r.text)
	submissions = info["data"]
	for submission in submissions:
		for url in findAllURLs(submission["selftext"]):
			links[url] = links.get(url, 0)+1

print(links)

with open('links.json', 'w') as fp:
    json.dump(links, fp)

print("------------ SAVED ------------")