import praw
import requests
from ratelimit import limits, RateLimitException, sleep_and_retry
from backoff import on_exception, expo
from psaw import PushshiftAPI
import csv
import networkx as nx
import datetime
import random
import re
from string import punctuation
import nltk
from nltk.corpus import brown

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
	#print("length of commentIDs")
	#print(len(commentIDs))
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


def getSubscriptions(redditorName,size=25): 
	#REQUIRES: username of a redditor, int <= 100
	#ENSURES: returns set of subreddits the redditor most recently commented on, up to size
	#		  also, it writes the user's entire comment history in its own separate
	# 		  .txt file named after the username
	subscriptions = set()
	URL = commentEndPoint
	PARAMS = {"author":redditorName, "fields":["body","subreddit"], "size":size}
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

def getTimedSubscriptions(redditorName, start_time, end_time):
	#REQUIRES: username of a redditor, unix epochs (int) for start_time and end_time
	#ENSURES: returns set of all subreddits the redditor commented on
	#		  during that time interval, up to 5000
	#		  also, it writes the user's entire comment history in its own 
	#		  separate .txt file named after the username
	subscriptions = set()
	URL = commentEndPoint
	before = end_time
	batch = 1
	while batch <= 50:
		PARAMS = {"author":redditorName, "size":100, "before":before, "after":start_time,
				  "sort":"desc", "sort_type":"created_utc"}
		r = ratelimitedGet(url=URL, params=PARAMS)
		try:
			info = r.json()
		except Exception as e:
			print(e)
			print("getInteractions")
			print(r.text)
			return subscriptions
		comments = info["data"]
		if not comments: break
		#to clear out the file from previous use:
		f = open(redditorName+".txt", 'w').close()
		f = open(redditorName+".txt", "a+")
		before = comments[-1]["created_utc"]
		for comment in comments:
			f.write(comment["body"]+"\n")
			subscriptions.add(comment["subreddit"])
		f.close()
		#print("length of comments:")
		#print(len(comments))
		print("batch number %d" % batch)
		batch += 1
		if len(comments) < 100: break
	#print("completed timed subscriptions")
	return subscriptions

#getSubscribers is now kind of obsolete, since I built graph #1
#using downloaded Pushshift comment files
def getSubscribers(subredditName):
	#REQUIRES: name of a subreddit
	#ENSURES: returns set of all users who ever commented on this subreddit
	#BUG/PROBLEM: limited to 500 users
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

#getAllSubscribers is now kind of obsolete, since I built graph #1
#using downloaded Pushshift comment files
def getAllSubscribers(start_time, end_time, subs_threshold):
	#REQUIRES: epochs for start_time and end_time, int for threshold
	#ENSURES: returns dict where keys are subreddit names,
	#		  and values are set of usernames of all redditors who ever
	#		  commented on that subreddit
	allSubscribers = dict()
	start = start_time
	URL = commentEndPoint
	while start < end_time:
		PARAMS = {"after":start, "before":end_time, "size":100,
				  "sort":"desc", "sort_type":"created_utc"}
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
	#REQUIRES: link (string of website link), size: int<= 100, display: bool
	#ENSURES: returns list of submissions containing the link
	#		  the submissions are dictionaries with fields such as "id", etc.
	#		  check pushshift API for more details
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
			epoch = submission["created_utc"]
			print(datetime.datetime.fromtimestamp(epoch).strftime('%c'))
	return linkSubmissions

def getInteractions(redditorName, numBatches=1): 
	#REQUIRES: username of a redditor, int for numBatches
	#ENSURES: returns set of IDs of submissions they commented on, up to 100*numBatches
	interactions = set()
	URL = commentEndPoint
	before = None
	batch = 1
	while batch <= numBatches:
		PARAMS = {"author":redditorName, "size":100, "before":before, 
				  "sort":"desc", "sort_type":"created_utc"}
		r = ratelimitedGet(url=URL, params=PARAMS)
		try:
			info = r.json()
		except Exception as e:
			print(e)
			print("getInteractions")
			print(r.text)
			return interactions
		comments = info["data"]
		if not comments: break
		before = comments[-1]["created_utc"]
		for comment in comments:
			link_id = comment["link_id"]
			submissionID = link_id[3:]
			interactions.add(submissionID)
		#print("length of comments:")
		#print(len(comments))
		print("batch number %d" % batch)
		batch += 1
		if len(comments) < 100: break
	return interactions

def getTimedInteractions(redditorName, start_time, end_time):
	#REQUIRES: username of a redditor, epochs for start and end times
	#ENSURES: returns set of IDs of submissions they commented on during the
	#		  specified time interval, up to 5000.
	interactions = set()
	URL = commentEndPoint
	before = end_time
	batch = 1
	while batch <= 50:
		PARAMS = {"author":redditorName, "size":100, "before":before, "after":start_time,
				  "sort":"desc", "sort_type":"created_utc"}
		r = ratelimitedGet(url=URL, params=PARAMS)
		try:
			info = r.json()
		except Exception as e:
			print(e)
			print("getInteractions")
			print(r.text)
			return interactions
		comments = info["data"]
		if not comments: break
		before = comments[-1]["created_utc"]
		for comment in comments:
			link_id = comment["link_id"]
			submissionID = link_id[3:]
			interactions.add(submissionID)
		#print("length of comments:")
		#print(len(comments))
		print("batch number %d" % batch)
		batch += 1
		if len(comments) < 100: break
	return interactions


#following function is made by Sasank
RANGE = 1 << 24
def make_id(max_rand=RANGE):
	"""Make a random base36 ID"""
	alphabet = "0123456789abcdefghijklmnopqrstuvwxyz"
	#random.seed(None)
	# get random value
	rand = random.randrange(1, max_rand)
	# store base36 value
	output = ""
	while rand != 0:
		rand, i = divmod(rand, len(alphabet))
		output = alphabet[i] + output
	# get first 6 values
	output = output[0:6]
	return output

def findAllURLs(text):
	urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
	return urls

words = set(w.lower() for w in brown.words())
def clean_string(str_raw):
	stops = {'the', 'a', 'an', 'and', 'but', 'if', 'or', 'because', 'as', 'what', 'which', 'this', 'that', 'these',
			 'those', 'then', 'just', 'so', 'than', 'such', 'both', 'through', 'about', 'for', 'is', 'of', 'while',
			 'during', 'to'}

	# Remove punctuation from text
	str_raw = ''.join([c for c in str_raw if c not in punctuation])

	# Remove stop words
	str_raw = " ".join([w for w in str_raw.split() if w.lower() not in stops])

	# Replace apostrophes with standard lexicons
	str_raw = str_raw.replace("isn't", "is not")
	str_raw = str_raw.replace("aren't", "are not")
	str_raw = str_raw.replace("ain't", "am not")
	str_raw = str_raw.replace("won't", "will not")
	str_raw = str_raw.replace("didn't", "did not")
	str_raw = str_raw.replace("shan't", "shall not")
	str_raw = str_raw.replace("haven't", "have not")
	str_raw = str_raw.replace("hadn't", "had not")
	str_raw = str_raw.replace("hasn't", "has not")
	str_raw = str_raw.replace("don't", "do not")
	str_raw = str_raw.replace("wasn't", "was not")
	str_raw = str_raw.replace("weren't", "were not")
	str_raw = str_raw.replace("doesn't", "does not")
	str_raw = str_raw.replace("'s", " is")
	str_raw = str_raw.replace("'re", " are")
	str_raw = str_raw.replace("'m", " am")
	str_raw = str_raw.replace("'d", " would")
	str_raw = str_raw.replace("'ll", " will")

	# remove emails and urls
	str_raw = re.sub(r'^https?:\/\/.*[\r\n]*', ' ', str_raw, flags=re.MULTILINE)
	str_raw = re.sub(r'[\w\.-]+@[\w\.-]+', ' ', str_raw, flags=re.MULTILINE)

	# Remove all symbols (clean to normal english)
	str_raw = re.sub(r'[^A-Za-z0-9\s]', r' ', str_raw)
	str_raw = re.sub(r'\n', r' ', str_raw)
	str_raw = re.sub(r'[0-9]', r' ', str_raw)

	#remove non-english words
	print("removing non-english words")
	" ".join(w for w in nltk.wordpunct_tokenize(str_raw) \
			 if w.lower() in words) #or not w.isalpha()

	return str_raw