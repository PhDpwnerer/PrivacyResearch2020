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
		G.add_node(subreddit)

print("adding edges")
allNodes = list(G.nodes())
for i in range(len(allNodes)):
	A = allSubscribers[allNodes[i]]
	for j in range(i+1, len(allNodes)):
		B = allSubscribers[allNodes[j]]
		commonSubscribers = A.intersection(B)
		weight = len(commonSubscribers)
		G.add_edge(allNodes[i], allNodes[j], weight=weight, active=False)

print("Done building graph")

nx.write_adjlist(G, "graph1.adjlist")

print("---------------------- SAVED -----------------------")