from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.datasets import load_files
from sklearn.decomposition import NMF, LatentDirichletAllocation
from gensim.parsing.preprocessing import strip_punctuation
from sklearn.metrics.pairwise import cosine_similarity
import gensim
from gensim.parsing.preprocessing import strip_punctuation
import re

import numpy as np


def display_topics(model, feature_names, no_top_words):
	for topic_idx, topic in enumerate(model.components_):
		print ("Topic %d:" % (topic_idx))
		print (" ".join([feature_names[i]
						for i in topic.argsort()[:-no_top_words - 1:-1]]))

dataset = load_files("./", encoding="utf-8", decode_error="strict")
docs = dataset.data
documents = list(map(lambda x: strip_punctuation(re.sub(r'http\S+', '', x)).lower().strip(), docs))
print(len(documents))
print(type(documents))
print(type(documents[0]))

no_features = 1000

# NMF is able to use tf-idf
tfidf_vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, max_features=no_features, stop_words='english')
tfidf = tfidf_vectorizer.fit_transform(documents)
tfidf_feature_names = tfidf_vectorizer.get_feature_names()
#print(tfidf_feature_names)
#print("-------------------------------")
#print("-------------------------------")
#print("-------------------------------")

# LDA can only use raw term counts for LDA because it is a probabilistic graphical model
tf_vectorizer = CountVectorizer(max_df=0.95, min_df=2, max_features=no_features, stop_words='english')
tf = tf_vectorizer.fit_transform(documents)
tf_feature_names = tf_vectorizer.get_feature_names()
#print(tf_feature_names)

no_topics = 4

# Run NMF
nmf = NMF(n_components=no_topics, random_state=1, alpha=.1, l1_ratio=.5, init='nndsvd').fit(tfidf)

# Run LDA
lda = LatentDirichletAllocation(n_components=no_topics, max_iter=5, learning_method='online', learning_offset=50.,random_state=0).fit(tf)

no_top_words = 20
print("-------------------------------")
print("Topics using NMF:")
print("-------------------------------")
display_topics(nmf, tfidf_feature_names, no_top_words)
print("-------------------------------")
print("Topics using LDA:")
print("-------------------------------")
display_topics(lda, tf_feature_names, no_top_words)

### For cosine similarity and stuff


docs_tokenized = [s.split(' ') for s in documents]
print(type(docs_tokenized))
print(type(docs_tokenized[0]))
print(type(docs_tokenized[0][0]))
word2vec_model = gensim.models.Word2Vec(docs_tokenized, min_count = 1)
word2vec_model.train(docs_tokenized, total_examples=len(docs_tokenized), epochs=10)

def avgTopicCosineSimilarity(w2v_model, feature_names, topic, no_top_words):
	vectors = np.array([w2v_model.wv[feature_names[i]]
						for i in topic.argsort()[:-no_top_words - 1:-1]])
	temp = cosine_similarity(vectors)
	return temp.mean()

def avgCosineSimilarity(w2v_model, topic_model, feature_names, no_top_words):
	temp = np.array([avgTopicCosineSimilarity(w2v_model, feature_names, topic, no_top_words) for topic in 
										topic_model.components_])
	return temp.mean()

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

