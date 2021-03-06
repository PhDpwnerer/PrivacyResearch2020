"""
This file requires test1.py to be run first. Make sure to place files generated
by test1.py in a folder called Comments
It performs Word2Vec embedding of the corpus generated by test1.py.
We then perform topic modeling using NMF and LDA. We do it 19 times, varying
the number of topics from 2 to 20. We see which number of topics yields the 
highest avg cosine similarity of the words within each topic.
The results are printed.
"""

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.datasets import load_files
from sklearn.decomposition import NMF, LatentDirichletAllocation
from gensim.parsing.preprocessing import strip_punctuation
from sklearn.metrics.pairwise import cosine_similarity
import gensim
from gensim.parsing.preprocessing import strip_punctuation
import re
from util import *

import numpy as np

#Helper functions:

def avgTopicCosineSimilarity(w2v_model, feature_names, topic, no_top_words):
	vectors = np.array([w2v_model.wv[feature_names[i]]
						for i in topic.argsort()[:-no_top_words - 1:-1]])
	temp = cosine_similarity(vectors)
	return temp.mean()

def avgCosineSimilarity(w2v_model, topic_model, feature_names, no_top_words):
	temp = np.array([avgTopicCosineSimilarity(w2v_model, feature_names, topic, no_top_words) for topic in 
										topic_model.components_])
	return temp.mean()

def display_topics(model, feature_names, no_top_words):
	for topic_idx, topic in enumerate(model.components_):
		print ("Topic %d:" % (topic_idx))
		print (" ".join([feature_names[i]
						for i in topic.argsort()[:-no_top_words - 1:-1]]))

#Part 1: Loading the files and standardizing the documents

dataset = load_files(container_path="./", categories="Comments", encoding="utf-8", decode_error="strict")
docs = dataset.data
#We clean and standardize the documents. See util.py for how clean_string works
documents = list(map(lambda x: clean_string(x).lower().strip(), docs))
print(len(documents))




#Part 2: Perform Word2Vec embedding on the corpus


docs_tokenized = [s.split(' ') for s in documents]
print(type(docs_tokenized))
print(type(docs_tokenized[0]))
print(type(docs_tokenized[0][0]))
word2vec_model = gensim.models.Word2Vec(docs_tokenized, min_count = 1)
word2vec_model.train(docs_tokenized, total_examples=len(docs_tokenized), epochs=10)

#Part 3: Perform topic modeling with no_topics ranging from 2 to 20.
# Calculate Cosine Similarities for each no_topics.

no_features = 1000

# NMF is able to use tf-idf
tfidf_vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, max_features=no_features, stop_words='english')
tfidf = tfidf_vectorizer.fit_transform(documents)
tfidf_feature_names = tfidf_vectorizer.get_feature_names()

# LDA can only use raw term counts for LDA because it is a probabilistic graphical model
tf_vectorizer = CountVectorizer(max_df=0.95, min_df=2, max_features=no_features, stop_words='english')
tf = tf_vectorizer.fit_transform(documents)
tf_feature_names = tf_vectorizer.get_feature_names()

similaritiesNMF = []
similaritiesLDA = []
for num_topics in range(2,21):
	print("num_topics: %d" %num_topics)
	nmf = NMF(n_components=num_topics, random_state=1, alpha=.1, l1_ratio=.5, init='nndsvd').fit(tfidf)
	similarityNMF = avgCosineSimilarity(word2vec_model, nmf, tfidf_feature_names, 20)
	lda = LatentDirichletAllocation(n_components=num_topics, max_iter=5, learning_method='online', learning_offset=50.,random_state=0).fit(tf)
	similarityLDA = avgCosineSimilarity(word2vec_model, lda, tf_feature_names, 20)
	similaritiesNMF.append(similarityNMF)
	similaritiesLDA.append(similarityLDA)

print(similaritiesNMF)
print(similaritiesLDA)

#Part 4: Identify no_topics that yield best avg cosine similarity for 
# each method (NMF and LDA). Return the results

bestNumTopicsNMF = np.argmax(np.array(similaritiesNMF))+2 #since num_topics starts at 2

bestTopicModelNMF = NMF(n_components=bestNumTopicsNMF, random_state=1, alpha=.1, l1_ratio=.5, init='nndsvd').fit(tfidf)

print("-------------------------------")
print("Topics using bestTopicModelNMF:")
print("-------------------------------")
display_topics(bestTopicModelNMF, tfidf_feature_names, 20)

bestNumTopicsLDA = np.argmax(np.array(similaritiesLDA))+2 #since num_topics starts at 2
bestTopicModelLDA = LatentDirichletAllocation(n_components=bestNumTopicsLDA, max_iter=5, learning_method='online', learning_offset=50.,random_state=0).fit(tf)
print("-------------------------------")
print("Topics using bestTopicModelLDA:")
print("-------------------------------")
display_topics(bestTopicModelLDA, tf_feature_names, 20)

