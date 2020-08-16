"""
graph2.py takes a specific link and builds a graph around it. Each node is the
name of a redditor that commented on a post containing that link. There exists 
an edge iff the two adjacent nodes (users) commented on the same submission
during the 6 months following the corresponding post's creation.

graph2.py saves the graph in file called graph2c.adjlist
"""
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

epoch_month = 2629743 #unix epoch value for 1 month

#interactors is a set of all people who commented on a post containing the link
interactors = set()
#times is a dict where each key is the name of an interactor, and each value is
#a tuple where start_time is the unix epoch value (UTC) of the interactor's
#corresponding post's creation time, and end_time is 6 months after start_time. 
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

#allInteractions is a dict where each key is the name of an interactor
#if using getTimedInteractions(), then each value is a set of ids of submissions
#they commented on during that 6 month window (start_time, end_time)
#if using getInteractions (see util.py) then we are only looking at the latest
#submissions they commented on
allInteractions = dict()

#count is to print out our progress while the code is running
count = 0

for interactor in interactors:
	allInteractions[interactor] = getTimedInteractions(interactor, times[interactor][0], times[interactor][1])
	G.add_node(interactor)
	count += 1
	print(count)
print(count)

allNodes = list(G.nodes())
print(allNodes)

#now we add the edges
#iterate over every pair of nodes and take set intersection of their interactions
for i in range(len(allNodes)):
	A = allInteractions[allNodes[i]]
	for j in range(i+1, len(allNodes)):
		B = allInteractions[allNodes[j]]
		commonInteractions = A.intersection(B)
		#weight = len(commonSubscribers)
		if len(commonInteractions) > 0:
			G.add_edge(allNodes[i], allNodes[j])


#saving graph as .adjlist file
nx.write_adjlist(G, "graph2c.adjlist")

print("---------------------- SAVED -----------------------")



#print(G.edges)


nx.draw_networkx(G)
