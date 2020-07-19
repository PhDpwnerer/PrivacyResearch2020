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


# Pushshift claims to have a rate limit of 60 calls/min.
# However, the rate limit is stricter based on personal testing.
# Even if you only make 60 calls in a minute, if you make those calls too fast,
# Pushshift will preemptively block you before the minute has elapsed, since it
# thinks you will pass it soon.
@on_exception(expo, RateLimitException, max_tries=8)
@limits(calls=4, period=4)
def ratelimitedGet(url="", params={}):
	#REQUIRES: url (string, typically endpoint of an API), and params
	#ENSURES: returns result of API call
	if params:
		return requests.get(url=url, params=params)
	else:
		return requests.get(url=url)

def getCommentIDs(submissionID):
	#REQUIRES: ID of submission
	#ENSURES: list of IDs for all comments of that given submission
	URL = "https://api.pushshift.io/reddit/submission/comment_ids/"+submissionID
	r = ratelimitedGet(URL)
	try:
		info = r.json()
	except Exception as e:
		print(e)
		print("commentIDs")
		print(r.text)
		return []
	result = info["data"] #returns list of IDs
	#print(result)
	return result

def getInteractors(submissionID): 
	#REQUIRES: ID of submission
	#ENSURES: returns set of usernames of all redditors who 
	#         commented on the submission
	interactors = set()
	#print(submissionID)
	commentIDs = getCommentIDs(submissionID)
	print(len(commentIDs))
	# pushshift returns at most 500 results per call,
	# so we must divide the list of comment ids
	tracker = 0
	while tracker < len(commentIDs):	
		URL = commentEndPoint
		PARAMS = {"ids":commentIDs[tracker:tracker+500], "fields":"author"}
		r = ratelimitedGet(url = URL, params = PARAMS)
		try:
			info = r.json()
		except Exception as e:
			print(e)
			print("inter")
			print(r.text)
			return interactors
		comments = info["data"]
		for comment in comments:
			if (comment["author"] != "[deleted]"):
				#print(comment["author"])
				#interactors.add(comment.author.name)
				interactors.add(comment["author"])
		tracker += 100
	return interactors


def getSubscriptions(redditorName): 
	#REQUIRES: username of a redditor
	#ENSURES: returns set of all subreddits on which the redditor ever commented
	subscriptions = set()
	URL = commentEndPoint
	PARAMS = {"author":redditorName, "fields":["body","subreddit"]}
	r = ratelimitedGet(url=URL, params=PARAMS)
	try:
		info = r.json()
	except Exception as e:
		print(e)
		print("subscriptions")
		print(r.text)
		return subscriptions
	comments = info["data"]
	#to clear out the file from previous use:
	f = open(redditorName+".txt", 'w').close()
	f = open(redditorName+".txt", "a+")
	for comment in comments:
		f.write(comment["body"]+"\n")
		subscriptions.add(comment["subreddit"])
	f.close()
	print("completed subscriptions")
	return subscriptions

def getSubscribers(subredditName):
	#REQUIRES: name of a subreddit
	#ENSURES: returns set of all users who ever commented on this subreddit
	#BUG/PROBLEM: limited to 500 users, needs to be fixed
	subscribers = set()
	URL = commentEndPoint
	PARAMS = {"subreddit":subredditName, "size": 500}
	r = ratelimitedGet(url=URL, params=PARAMS)
	try:
		info = r.json()
	except Exception as e:
		print(e)
		print("subscribers")
		print(r.text)
		return subscribers
	comments = info["data"]
	for comment in comments:
		if (comment["author"] != "[deleted]"):
			subscribers.add(comment["author"])
	print("completed %s subreddit getSubscribers" % subredditName)
	return subscribers

def getAllSubscribers(start_time, end_time, subs_threshold):
	#REQUIRES: epochs for start_time and end_time, int for threshold
	#ENSURES: returns dict where keys are subreddit names,
	#		  and values are set of usernames of all redditors who ever
	#		  commented on that subreddit
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
			print("allSubscribers")
			print(r.text)
			return subscribers
		comments = info["data"]
		for comment in comments:
			if (comment["author"] != "[deleted]"):
				allSubscribers[comment["subreddit"]] = allSubscribers.get(comment["subreddit"], set()).add(comment["author"])
		start = int(comments[-1]["created_utc"])
	return allSubscribers

def getLinkSubmissions(link, size=25,display=False):
	#REQUIRES: link (string of website link), size: int<= 500, display: bool
	#ENSURES: returns list of submissions containing the link
	#		  the submissions are dictionaries with fields such as "id", etc.
	#		  check pushshift API for more details
	size is an int that is <= 500
	URL = submissionEndPoint
	PARAMS = {"q":link, "size":size}
	r = ratelimitedGet(url=URL, params=PARAMS)
	try:
		info = r.json()
	except Exception as e:
		print(e)
		print("linkSubmissions")
		print(r.text)
		return []
	linkSubmissions = info["data"]
	if display:
		for submission in linkSubmissions:
			if (submission["author"] != "[deleted]"):
				print(submission["author"])
			print(submission["title"])
			print(submission["id"])
	return linkSubmissions

def getInteractions(redditorName): 
	#REQUIRES: username of a redditor
	#ENSURES: returns set of IDs of submissions they commented on, up to 500
	interactions = set()
	URL = commentEndPoint
	PARAMS = {"author":redditorName, "size":500}
	r = ratelimitedGet(url=URL, params=PARAMS)
	try:
		info = r.json()
	except Exception as e:
		print(e)
		print("getInteractions")
		print(r.text)
		return interactions
	comments = info["data"]
	for comment in comments:
		link_id = comment["link_id"]
		submissionID = link_id[3:]
		interactions.add(submissionID)
	return interactions