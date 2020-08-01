import praw
import requests
from ratelimit import limits, RateLimitException, sleep_and_retry
from backoff import on_exception, expo
from psaw import PushshiftAPI
import csv
import networkx as nx
from util import *

link = "https://pages.nist.gov/800-63-3/sp800-63b.html"


linkSubmissions = getLinkSubmissions(link, 500, display=True)

epoch_month = 2629743*3 #unix epoch

interactors = set()
times = dict()
for submission in linkSubmissions:
	start_time = submission["created_utc"] #unix epoch
	end_time = start_time+3*epoch_month
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

nx.write_adjlist(G, "graph2c.adjlist")

print("---------------------- SAVED -----------------------")



#print(G.edges)


nx.draw_networkx(G)
