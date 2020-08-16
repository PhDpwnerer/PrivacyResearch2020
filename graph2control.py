"""
graph2control.py serves as a control group for graph2.
graph2control builds the same graph as graph2, but using a different link.
See graph2.py's comments to better understand how code works.
links are pulled from either poplinks or links (your choice).
"""

import praw
import requests
from ratelimit import limits, RateLimitException, sleep_and_retry
from backoff import on_exception, expo
from psaw import PushshiftAPI
import csv
import networkx as nx
from util import *

import pprint
import json

#poplinks.json is created by generatePopLinks.py
#links.json is created by generateLinks.py
with open('poplinks.json', 'r') as fp:
    links = json.load(fp)

pprint.pprint(links)

#List of links for previously built control graphs
# control1: http://www.ncbi.nlm.nih.gov/pubmed/17378847
# control2: http://xkcd.com/137/
# control3: https://www.ally.com/do-it-right/investing/top-10-option-trading-mistakes/

link = "https://www.ally.com/do-it-right/investing/top-10-option-trading-mistakes/"


linkSubmissions = getLinkSubmissions(link, 100, display=True)
print(len(linkSubmissions)) #to make sure it is less than 100

epoch_month = 2629743 #unix epoch value for one month

interactors = set()
times = dict()
for submission in linkSubmissions:
	start_time = submission["created_utc"] #unix epoch
	end_time = start_time+6*epoch_month
	subInteractors = getInteractors(submission["id"])
	for user in subInteractors:
		times[user] = (start_time,end_time)
	#print(subInteractors)
	interactors = interactors.union(subInteractors)
	#print("==== interactors ====")
	#print(interactors)

print(interactors)
print(len(interactors))


G = nx.Graph()
allInteractions = dict()

count = 0

for interactor in interactors:
	allInteractions[interactor] = getTimedInteractions(interactor, times[interactor][0], times[interactor][1])
	G.add_node(interactor)
	count += 1
	print(count)
print(count)

allNodes = list(G.nodes())
print(allNodes)
for i in range(len(allNodes)):
	A = allInteractions[allNodes[i]]
	for j in range(i+1, len(allNodes)):
		B = allInteractions[allNodes[j]]
		commonInteractions = A.intersection(B)
		#weight = len(commonSubscribers)
		if len(commonInteractions) > 0:
			G.add_edge(allNodes[i], allNodes[j])

nx.write_adjlist(G, "control3.adjlist")

print("---------------------- SAVED -----------------------")



#print(G.edges)
