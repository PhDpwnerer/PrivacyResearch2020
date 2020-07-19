import praw
import requests
from ratelimit import limits, RateLimitException, sleep_and_retry
from backoff import on_exception, expo
from psaw import PushshiftAPI
import csv
import networkx as nx
import matplotlib.pyplot as plt

G = nx.read_adjlist("graph2.adjlist")

nx.draw(G)
plt.savefig("graph2.png")
plt.show()