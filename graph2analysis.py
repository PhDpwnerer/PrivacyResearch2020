import praw
import requests
from ratelimit import limits, RateLimitException, sleep_and_retry
from backoff import on_exception, expo
from psaw import PushshiftAPI
import csv
import networkx as nx
import matplotlib.pyplot as plt
import math

G = nx.read_adjlist("graph2b.adjlist")

nx.draw_networkx(G, with_labels=False, node_size=10, node_color="green", alpha=0.5, )
plt.savefig("graph2b.png")
plt.show()
print(G.edges)
print(len(G.nodes))

# make p equal to the ratio of edges in G over max. number of possible edges in G
p = len(G.edges)/((len(G.nodes)*(len(G.nodes)-1))/2)
print("p = "+str(p))

er = nx.erdos_renyi_graph(len(G.nodes), p, seed=2020)

nx.draw(er)
plt.savefig("Erdos_Renyi_Graph.png")
plt.show()

print(nx.diameter(G), nx.diameter(er))