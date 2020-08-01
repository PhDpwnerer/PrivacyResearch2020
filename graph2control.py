import praw
import requests
from ratelimit import limits, RateLimitException, sleep_and_retry
from backoff import on_exception, expo
from psaw import PushshiftAPI
import csv
import networkx as nx
from util import *

ALL = reddit.subreddit("all")

randomSubmissions = [ALL.random() for i in range(500)]

# randomSubmissions = ALL.hot(limit=50)

"""
for submission in randomSubmissions:
	print(submission.title)
	print(submission.url)
	print(submission.subreddit.title)
	print(submission.id)
"""

randomSubmissionIDs = list(map(lambda x: x.id, randomSubmissions))
print(randomSubmissionIDs)

epoch_month = 2629743*3 #unix epoch

interactors = set()
times = dict()

r = ratelimitedGet(url = submissionEndPoint, params = {"ids":randomSubmissionIDs})
try:
	info = r.json()
except Exception as e:
	print(e)
	print("pushshiftRandomSubmissions")
	print(r.text)
pushshiftRandomSubmissions = info["data"] #returns list of IDs

print(len(pushshiftRandomSubmissions))

for submission in pushshiftRandomSubmissions:
	#print(submission["title"])
	#print(submission["subreddit"])
	print(submission["full_link"])
	print(submission["selftext"])
	print("--------------------------------------")

for submission in pushshiftRandomSubmissions:
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

nx.write_adjlist(G, "graph2comparison.adjlist")

print("---------------------- SAVED -----------------------")



#print(G.edges)


nx.draw_networkx(G)
