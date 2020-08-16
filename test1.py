"""
named test1.py since it was the first file I made 
for this project, should probably change it.
This file takes a link and generates a file for each user who ever commented
on a post containing that link (we define that as interactor). 
Each file contains all the comments the user made during the 6 month period 
following the creation of the corresponding post containg that link.
This file also saves a dictionary (.json) where key=subreddit name, and
val=number of interactors who commented on corresponding subreddit
"""

import praw
import requests
from ratelimit import limits, RateLimitException, sleep_and_retry
from backoff import on_exception, expo
from psaw import PushshiftAPI
import json
from util import *

link = "https://pages.nist.gov/800-63-3/sp800-63b.html"
submissions = getLinkSubmissions(link, 100, display=True)

submissionIDs = list(map(lambda x: (x["id"], x["created_utc"]), submissions))

epoch_month = 2629743 #unix epoch value for one month

subredditCount = dict()
#count is to print progress while code runs
count = 0
for ID, start_time in submissionIDs:
	end_time = start_time + 6*epoch_month
	print("getting interactors for:")
	print(ID)
	#getInteractors returns set of names of all who commented on said post
	#see util.py for more info
	interactors = getInteractors(ID)
	print("number of interactors:")
	print(len(interactors))
	for name in interactors:
		redditor = name
		#print("getting subscriptions for:")
		#print(name)
		count += 1
		print(count)
		#getTimedSubscriptions returns set of subreddits the user commented on
		#over the corresponding time interval
		#getTimedSubscriptions also writes the comments to file
		subscriptions = getTimedSubscriptions(redditor, start_time, end_time)	
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
with open('Subreddit Scores.json', 'w') as fp:
    json.dump(subredditCount, fp)

f2 = open('Subreddit Scores.txt', 'w').close() #to clear out the file from previous use
f2 = open("Subreddit Scores.txt", "a+")
f2.write(str(sortedSubredditCount))
f2.close()


