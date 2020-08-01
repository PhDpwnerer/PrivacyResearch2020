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
allSubscribers = dict()
allSubreddits = set()
count = 0

start_time = time.time()


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