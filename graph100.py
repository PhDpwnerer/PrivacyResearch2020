import praw
import requests
from ratelimit import limits, RateLimitException, sleep_and_retry
from backoff import on_exception, expo
from psaw import PushshiftAPI
import csv
import networkx as nx
from util import *


topSubreddits = reddit.subreddits.popular(limit=100)

for subreddit in topSubreddits:
	"""
	print(subreddit["subs"])
	print(subreddit["real_name"])
	count+= 1
	print("count")
	print(count)
	"""
	if int(subreddit["subs"]) >= 100:
		subscribers = getSubscribers(subreddit["real_name"])
		print("subscriber count:")
		print(len(subscribers))
		allSubscribers[subreddit["real_name"]] = subscribers
		G.add_node(subreddit["real_name"])
		count += 1
		print(count)
print(count)

allNodes = list(G.nodes())
for i in range(len(allNodes)):
	A = allSubscribers[allNodes[i]]
	for j in range(i+1, len(allNodes)):
		B = allSubscribers[allNodes[j]]
		commonSubscribers = A.intersection(B)
		weight = len(commonSubscribers)
		G.add_edge(allNodes[i], allNodes[j], weight=weight)
