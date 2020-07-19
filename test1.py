import praw
import requests
from ratelimit import limits, RateLimitException, sleep_and_retry
from backoff import on_exception, expo
from psaw import PushshiftAPI

commentEndPoint = "https://api.pushshift.io/reddit/search/comment/"
submissionEndPoint = "https://api.pushshift.io/reddit/search/submission/"


@on_exception(expo, RateLimitException, max_tries=8)
@limits(calls=4, period=4)
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

reddit = praw.Reddit(client_id="wlemUwlmzOwsDw",
					client_secret="r2_viKFvYZ_gkvMecP-8zh8TKDA",
					user_agent="trial20200606",
					username="CMUResearch1999",
					password="purple123")

api = PushshiftAPI(reddit)
link = "xkcd.com/936"
title = "Password Strength"

xkcdBot = reddit.redditor("xkcd_transcriber")

submissionIDs = []

for comment in xkcdBot.comments.new(limit=None):
	if title in comment.body:
		submissionIDs.append(comment.submission.id)
		print(comment.submission.title)
		print(comment.submission.url)
		print(comment.subreddit.title)
		print(comment.submission.id)
		print("---------------------")


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

print("--------------------------")
print("BUG FIXING")
print("BUGs FIXED")
print("--------------------------")

subredditCount = dict()
for ID in submissionIDs:
	print("getting interactors for:")
	print(ID)
	interactors = getInteractors(ID)
	for name in interactors:
		if name != "xkcd_transcriber":
			redditor = name
			print("getting subscriptions for:")
			print(name)
			subscriptions = getSubscriptions(redditor)	
			for name in subscriptions:
				subredditCount[name] = subredditCount.get(name, 0)+1
		#print(subredditCount)

sortedSubredditCount = sorted(subredditCount.items(), key=lambda x: x[1],reverse=True) 
print(sortedSubredditCount)
"""
for subreddit in subredditCount:
	f.write("------------------------------------ \n")
	f.write(reddit.subreddit(subreddit).description+"\n")
	f.write("------------------------------------ \n")
"""

f2 = open('Subreddit Scores.txt', 'w').close() #to clear out the file from previous use
f2 = open("Subreddit Scores.txt", "a+")
f2.write(str(sortedSubredditCount))
f2.close()


"""

def getInteractors(submission): #returns set of usernames
	interactors = set()
	submission.comments.replace_more(limit=0)
	for comment in submission.comments.list():
		if not (comment.author is None):
			print(comment.author.name)
			#interactors.add(comment.author.name)
			interactors.add(comment.author)
	return interactors

def getSubscriptions(redditor): #returns set of subreddit names
	subscriptions = set()
	for comment in redditor.comments.new(limit=1):
		subscriptions.add(comment.subreddit.title)
	return subscriptions

reddit = praw.Reddit(client_id="wlemUwlmzOwsDw",
					client_secret="r2_viKFvYZ_gkvMecP-8zh8TKDA",
					user_agent="my user agent",
					username="CMUResearch1999",
					password="purple123")


link = "xkcd.com/936"
title = "Password Strength"
counter = 0

xkcdBot = reddit.redditor("xkcd_transcriber")

submissions = []

for comment in xkcdBot.comments.new(limit=None):
	if title in comment.body:
		submissions.append(comment.submission)
		print(comment.submission.title)
		print(comment.submission.url)
		print(comment.subreddit.title)
		print("---------------------")

subredditCount = dict()
for submission in submissions:
	print("getting interactors for:")
	print(submission.title)
	interactors = getInteractors(submission)
	for name in interactors:
		if name != "xkcd_transcriber":
			#redditor = reddit.redditor(name)
			redditor = name
			print("getting subscriptions for:")
			print(name)
			subscriptions = getSubscriptions(redditor)	
			for name in subscriptions:
				subredditCount[name] = subredditCount.get(name, 0)+1
		print(subredditCount)

print(subredditCount)

"""