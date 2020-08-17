"""
Analyse graph1. Requires graph1 to be saved in a file called graph1.adjlist.
We use Louvain method of community detection to identify communities within
our graph. We then identify which subreddits our link was posted on.
Finally, we inspect which communities these subreddits belong to.
"""

import praw
import requests
from ratelimit import limits, RateLimitException, sleep_and_retry
from backoff import on_exception, expo
from psaw import PushshiftAPI
import csv
import networkx as nx
import matplotlib.pyplot as plt
import math
import community as community_louvain
from util import *


print("loading graph")

G = nx.read_adjlist("graph1b.adjlist")

print("finished loading graph")

print("gathering link nodes")

link = "https://pages.nist.gov/800-63-3/sp800-63b.html"

linkSubmissions = getLinkSubmissions(link, 500, display=True)

linkSubreddits = list(map(lambda x: x["subreddit"], linkSubmissions))

print("finished gathering link nodes")

print("partitioning graph using Louvain method")

partition = community_louvain.best_partition(G)

print("Finished partitioning")

print("All the communities:")
print(partition.values())

print("Communities of link nodes:")
#Communities are numbered from 0 to n-1 where n is the number of communites
for subreddit in linkSubreddits:
	print(partition[subreddit])

"""
#activating link nodes
for subreddit in linkSubreddits:
	G.nodes[subreddit]["active"] = True

"""