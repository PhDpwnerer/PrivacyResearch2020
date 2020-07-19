import praw
import requests
from ratelimit import limits, RateLimitException, sleep_and_retry
from backoff import on_exception, expo
from psaw import PushshiftAPI
import csv
import networkx as nx

reddit = praw.Reddit(client_id="wlemUwlmzOwsDw",
					client_secret="r2_viKFvYZ_gkvMecP-8zh8TKDA",
					user_agent="trial20200606",
					username="CMUResearch1999",
					password="purple123")

commentEndPoint = "https://api.pushshift.io/reddit/search/comment/"
submissionEndPoint = "https://api.pushshift.io/reddit/search/submission/"

@on_exception(expo, RateLimitException, max_tries=8)
@limits(calls=60, period=60)
def ratelimitedGet(url="", params={}):
	if params:
		return requests.get(url=url, params=params)
	else:
		return requests.get(url=url)

def getCommentIDs(submissionID):
	#REQUIRES: ID of submission
	#ENSURES: list of IDs for all comments of that given submission
	URL = "https://api.pushshift.io/reddit/submission/comment_ids/"+submissionID
	r = ratelimitedGet(URL)
	info = r.json()
	result = info["data"] #returns list of IDs
	#print(result)
	return result

def getInteractors(submissionID): #returns set of usernames
	interactors = set()
	print(submissionID)
	commentIDs = getCommentIDs(submissionID)
	#print(commentIDs)
	URL = commentEndPoint
	PARAMS = {"ids":commentIDs, "fields":"author"}
	r = ratelimitedGet(url = URL, params = PARAMS)
	info = r.json()
	comments = info["data"]
	for comment in comments:
		if (comment["author"] != "[deleted]"):
			#print(comment["author"])
			#interactors.add(comment.author.name)
			interactors.add(comment["author"])
	return interactors


def getSubscriptions(redditorName): #returns set of subreddit names
	subscriptions = set()
	URL = commentEndPoint
	PARAMS = {"author":redditorName, "fields":["body","subreddit"]}
	r = ratelimitedGet(url=URL, params=PARAMS)
	try:
		info = r.json()
	except Exception as e:
		print(e)
		print(r.text)
		return subscriptions
	comments = info["data"]
	f = open(redditorName+".txt", 'w').close() #to clear out the file from previous use
	f = open(redditorName+".txt", "a+")
	for comment in comments:
		f.write(comment["body"]+"\n")
		subscriptions.add(comment["subreddit"])
	f.close()
	print("completed subscriptions")
	return subscriptions

def getSubscribers(subredditName):
	subscribers = set()
	URL = commentEndPoint
	PARAMS = {"subreddit":subredditName, "size": 500}
	r = ratelimitedGet(url=URL, params=PARAMS)
	try:
		info = r.json()
	except Exception as e:
		print(e)
		print(r.text)
		return subscribers
	comments = info["data"]
	for comment in comments:
		if (comment["author"] != "[deleted]"):
			subscribers.add(comment["author"])
	print("completed %s subreddit subscribers" % subredditName)
	return subscribers

def getAllSubscribers(start_time, end_time, subs_threshold):
	allSubscribers = dict()
	start = start_time
	URL = commentEndPoint
	while start < end_time:
		PARAMS = {"after":start, "before":end_time, "size":500}
		r = ratelimitedGet(url=URL, params=PARAMS)
		try:
			info = r.json()
		except Exception as e:
			print(e)
			print(r.text)
			return subscribers
		comments = info["data"]
		for comment in comments:
			if (comment["author"] != "[deleted]"):
				allSubscribers[comment["subreddit"]] = allSubscribers.get(comment["subreddit"], set()).add(comment["author"])
		start = int(comments[-1]["created_utc"])
	return allSubscribers



csvfile = open('2020-07-03.csv', encoding="iso-8859-1",newline='')
allSubreddits = csv.DictReader(csvfile)

G = nx.Graph()
allSubscribers = dict()
count = 0

for subreddit in allSubreddits:
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




