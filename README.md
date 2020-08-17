# Overview:
## Important Modules and APIs that I used:
1. Pushshift (https://github.com/pushshift/api)
2. Networkx

## What each file does (Complete details found at the beginning of each file):
1. util.py: contains almost all the helper functions (with the exception of topic modeling stuff)
2. test1.py: creates corpus for topic modeling.
3. topic.py: does topic modeling on corpus created by test1.py. Requries test1.py to be run first and corpus to be placed in folder called "Comments"
4. graph1.py: creates graph #1 (see SURF proposal) that models Reddit on a subreddit level. Each node is a subreddit, and edge weights are equal to the number of common subscribers between sbureddits. Saves graph in graph1.adjlist.
5. graph1-building.py: if terminated graph1.py after part 1 but before part2 was completed (see file), use this file to complete part 2.
6. graph1analysis.py: Performs louvain method of community detection on graph 1 and identifies which communities contained posts of our security link.
7. graph2.py: creates graph #2 (see SURF proposal) where each node is a user that interacted with out link and edge connects users who commented on same submission at some point in time.
8. graph2control.py: serves as control group to compare graph2 to (graph generated via random link). Obsolete if we use erdos-renyi graph instead.
9. graph2analysis.py: calculates diameter of graph2 and compares it to diameters of 20 erdos-renyi graphs that have same edge density. Can also be used to analyse control graphs.
10. generateLinks.py: saves as .json file a dictionary of randomly generated links.
11. generatePopLinks.py: saves as .json file a dictionary of randomly generated popular links.

## Quick Project Recap:
### Intro
We tracked the spread of a link (https://pages.nist.gov/800-63-3/sp800-63b.html) on Reddit.

### Exploratory Data Analysis:
#### Method #1 (Subreddit Scores):
We gathered the all users who ever commented on a post containing our link (we called them **interactors**). We looked at these users comment history during the 6-month period following the creation of the **link post** (post containing link) that they interacted with. We used that info to create a dictionary where each key is a subreddit and each value is the number of **interactors** who commented on that subreddit.

See test1.py
#### Method #2 (Topic Analysis):
Once again, we looked at the comment history of each **interactor** during the 6-month period following the creation of the **link post** that they interacted with. We created a corpus out of this comment history where each file contains the comments of a specific user. We then performed topic analysis on the corpus, varying the number of topics (no_topics) from 2 to 20 and returned the results of the no_topics that yielded the highest cosine similarity between the words within each topic. Results can be found in "Topic Modeling Results.txt".

See test1.py for corpus creation, and topic.py for topic analysis.

### Graph Modeling and Analysis:
#### Graph #1:
We modeled Reddit on a subreddit level. Each node is a subreddit, and edge weights are equal to the number of common subscribers between subreddits. Since subscribers are not public info on Reddit API, we defined subscribers as redditors who commented on the subreddit. We only looked at the comments made in April 2019, since that month had the highest frequency of **link posts**.

For the sake of run-time efficiency, we downloaded all the comments from April 2019 and iterated through them locally.

We then performed Louvain method of community detection to see which communities contained the **link posts**. **UNFORTUNATELY, THE MODULE FOR THE LOUVAIN METHOD OF COMMUNITY DETECTION IS BUGGY AND I GET SEGFAULTS. ONLY HAPPENS WHEN THE GRAPH IS TOO BIG.**

See the following files: graph1.py, graph1-building.py, graph1analysis.py

#### Graph #2:
We created a graph where each node is an **interactor** and edges connect **interactors** who commented on the same submission before. We then calculated its diameter and compared it with the diameters of 20 random erdos-renyi graphs that had the same edge density and number of nodes. 
##### Results: 
All 20 random erdos-renyi graphs had a diameter of 2. Our graph2 was unconnected, but the sum of the diameters of graph2's connected components is 13. The graph has 768 nodes.

We also considered generating control graphs that were built using the same principle as graph #2, but with a random link. However, we didn't do any analysis on these graphs.

See the following files: graph2.py, graph2analysis.py
See the following files for the control graphs: graph2control.py, generateLinks.py, generatePopLinks.py
