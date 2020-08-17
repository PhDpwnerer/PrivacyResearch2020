"""
graph2analysis.py does the graph analysis for graph2 (built by graph2.py).
We compare the diameter of graph2 with the diameter of 20 random graphs.
The random graphs are erdos-renyi graphs where p=edge density of graph2
If a graph is not connected, we calculate the diameter by summing the
diameters of each connected component.

This file can also be used to analyze the control graphs. Just make sure
that you adjust which graph is being loaded.
"""

import praw
import requests
from ratelimit import limits, RateLimitException, sleep_and_retry
from backoff import on_exception, expo
from psaw import PushshiftAPI
import csv
import networkx as nx
import matplotlib.pyplot as plt
import math

G = nx.read_adjlist("graph2c.adjlist")

nx.draw_networkx(G, with_labels=False, node_size=10, node_color="green", alpha=0.5)
plt.savefig("graph2c.png")
plt.show()

#print(G.edges)
print(len(G.nodes))

# make p equal to the ratio of edges in G over max. number of possible edges in G
# in other words, edge density
p = len(G.edges)/((len(G.nodes)*(len(G.nodes)-1))/2)
print("p = "+str(p))

print("Diameters of Erdos-Renyi Graphs")
for seed in range(20):
	er = nx.erdos_renyi_graph(len(G.nodes), p, seed = seed)
	if nx.is_connected(er):
		print(nx.diameter(er))
	else:
		print("Erdos-Renyi Graph is not connected. Sum of diameter of connected components:")
		connected_components = list(nx.connected_components(er))
		connected_components_subgraphs = list(map(lambda x: er.subgraph(x), connected_components))
		print(sum(list(map(lambda x: nx.diameter(x), connected_components_subgraphs))))

print("--------------------")
print("Diameter of Link Graph")

if nx.is_connected(G):
	print(nx.diameter(G))
else:
	print("Graph is not connected. Sum of diameter of connected components:")
	connected_components = list(nx.connected_components(G))
	connected_components_subgraphs = list(map(lambda x: G.subgraph(x), connected_components))
	print(sum(list(map(lambda x: nx.diameter(x), connected_components_subgraphs))))