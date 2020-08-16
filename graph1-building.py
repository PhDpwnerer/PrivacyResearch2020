"""
Performs part 2 of graph1.py
See that file for more information. 
Requires the pickle files created by graph1.py.
Takes around 25 min. on my computer with 16GB of ram.
There are around 140 million edges IIRC.
"""

import praw
import requests
from ratelimit import limits, RateLimitException, sleep_and_retry
from backoff import on_exception, expo
from psaw import PushshiftAPI
import csv
import networkx as nx
import zstandard as zstd
import json
import pickle
import time

from util import *

#Code mostly from https://www.reddit.com/r/pushshift/comments/ajmcc0/information_and_code_examples_on_how_to_use_the/
# See u/Watchful1's comment

G = nx.Graph()


print("Loading allSubscribers...")

with open('allSubscribers.pickle', 'rb') as fp:
	allSubscribers = pickle.load(fp)

print("Loading allSubreddits...")

with open('allSubreddits.pickle', 'rb') as fp:
	allSubreddits = pickle.load(fp)

print("-------------------------------------------------------------------------------")
print("-------------------------------------------------------------------------------")
print("-------------------------------------------------------------------------------")


print(allSubreddits)
print(type(allSubreddits))
print(len(allSubreddits))


print("Building graph")
print("-------------------------------------------------------------------------------")
print("-------------------------------------------------------------------------------")
print("-------------------------------------------------------------------------------")

print("adding nodes")
for subreddit in allSubreddits:
	if len(allSubscribers[subreddit]) >= 100:
		G.add_node(subreddit, active=False)

print(len(G.nodes))

print("adding edges")
allNodes = list(G.nodes())

start_time = time.time()
#count is to print our progress while the code is running
count = 0
for i in range(len(allNodes)):
	A = allSubscribers[allNodes[i]]
	for j in range(i+1, len(allNodes)):
		B = allSubscribers[allNodes[j]]
		commonSubscribers = A.intersection(B)
		weight = len(commonSubscribers)
		G.add_edge(allNodes[i], allNodes[j], weight=weight)
		count += 1
		if count % 1000000 == 0:			
			current_time = time.time()
			#prints how much time was needed to compute the latest million edges
			print(current_time-start_time)
			start_time = current_time
			#prints how many million edges we have computed
			print(count/1000000)

print("Done building graph")

nx.write_adjlist(G, "graph1.adjlist")

print("---------------------- SAVED -----------------------")