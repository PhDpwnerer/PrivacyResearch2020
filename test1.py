import praw
import requests
from ratelimit import limits, RateLimitException, sleep_and_retry
from backoff import on_exception, expo
from psaw import PushshiftAPI
from util import *

commentEndPoint = "https://api.pushshift.io/reddit/search/comment/"
submissionEndPoint = "https://api.pushshift.io/reddit/search/submission/"

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