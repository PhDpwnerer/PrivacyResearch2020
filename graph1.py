"""
graph1.py models the entirety of Reddit on a subreddit level. Each node is the
name of a subreddit. Each edge has a weight equal to the number of common
subscribers between the two adjacent nodes (subreddits). We define subscribers
as anyone who has commented on a submission from the corresponding subreddit.
Currently, we are only looking at the comments from April 2019.
Download more pushshift comment files from here:
https://files.pushshift.io/reddit/comments/

graph1.py saves the graph in file called graph1.adjlist
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

"""
High-level description of algorithm:

#Part 1: Gathering info
We iterate through every comment in our pushshift file(s).
For each comment, we look at the "author" and "subreddit" attributes. We add
the author of each comment to the corresponding subreddit's set of subscribers.
We use a dictionary (allSubscribers) to keep track of each subreddit's subscribers.
#Part 2: Building the graph
We only consider subreddits with over 100 interactors (to filter out dead subreddits).
Each node is set to active=False. We will use this attribute for graph analysis
later.
The rest is self-explanatory.

#IMPORTANT NOTE: If you don't want to do Part 1 & 2 in a single run or if you
want to use the info from part 1 to build a different graph later, you can
terminate your code once part 1 is complete. allSubscribers and allSubreddits
will both be saved as pickle files that can be loaded in graph1-building.py to 
complete graph building or any other script of your creation.
"""

G = nx.Graph()
#allSubscribers is a dictionary where each key is the name of a subreddit, 
#and the value is the set of names of the corresponding subscribers
allSubscribers = dict()

#simply a set that contains the names of all subreddits
allSubreddits = set()
count = 0

start_time = time.time()

#Code mostly from https://www.reddit.com/r/pushshift/comments/ajmcc0/information_and_code_examples_on_how_to_use_the/
# See u/Watchful1's comment
with open("RC_2019-04.zst", 'rb') as fh:
	dctx = zstd.ZstdDecompressor()
	with dctx.stream_reader(fh) as reader:
		previous_line = ""
		while True:
			chunk = reader.read(2**24) #used to be 65536
			if not chunk:
				break
			string_data = chunk.decode('utf-8')
			lines = string_data.split("\n")
			for i, line in enumerate(lines[:-1]):
				if i == 0:
					line = previous_line + line
				object = json.loads(line)
				#print(object) AWWW YISSS IT WORKS!!!
				#Do stuff with the json object (dictionary) here
				subreddit = object["subreddit"]
				author = object["author"]
				if subreddit in allSubscribers:
					allSubscribers[subreddit].add(author)
				else:
					allSubscribers[subreddit] = set()
					allSubscribers[subreddit].add(author)
				#print(allSubscribers)
				allSubreddits.add(subreddit)
				count += 1
				if count % 100000 == 0:
					print("--- %s seconds ---" % (time.time() - start_time))
					start_time = time.time()
					print(count)
			previous_line = lines[-1]



print("-------------------------------------------------------------------------------")
print("-------------------------------------------------------------------------------")
print("-------------------------------------------------------------------------------")
print("Done building allSubscribers and allSubreddits")

with open('allSubscribers.pickle', 'wb') as fp:
	pickle.dump(allSubscribers, fp, protocol=pickle.HIGHEST_PROTOCOL)

with open('allSubreddits.pickle', 'wb') as fp:
	pickle.dump(allSubreddits, fp, protocol=pickle.HIGHEST_PROTOCOL)

print("all allSubscribers and allSubreddits SAVED")

print("-------------------------------------------------------------------------------")
print("-------------------------------------------------------------------------------")
print("-------------------------------------------------------------------------------")


print("Building graph")
print("-------------------------------------------------------------------------------")
print("-------------------------------------------------------------------------------")
print("-------------------------------------------------------------------------------")

print("adding nodes")
for subreddit in allSubreddits:
	if len(allSubscribers[subreddit]) >= 100:
		G.add_node(subreddit,active=False)

print("adding edges")
allNodes = list(G.nodes())
for i in range(len(allNodes)):
	A = allSubscribers[allNodes[i]]
	for j in range(i+1, len(allNodes)):
		B = allSubscribers[allNodes[j]]
		commonSubscribers = A.intersection(B)
		weight = len(commonSubscribers)
		G.add_edge(allNodes[i], allNodes[j], weight=weight)

print("Done building graph")

#Save graph in .adjlist file
nx.write_adjlist(G, "graph1.adjlist")

print("---------------------- SAVED -----------------------")