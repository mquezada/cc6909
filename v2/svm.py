from nltk.stem import SnowballStemmer
from redis import Redis
import nltk
import utils
import numpy
import HTMLParser
from nltk.cluster import KMeansClusterer, cosine_distance
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from time import time


r = Redis()
r_events = r.keys('event:*:title')
parser = HTMLParser.HTMLParser()


test = []
documents = []
k = r_events[126]
print "event:", r.get(k)
id = k.split(':')[1]
docs = r.keys('document:*:' + id)
lang = r.get('event:' + id + ':lang')
ds = 0
ts = 0
for doc in docs:
    document = []
    ds = ds + 1
    d_id = doc.split(':')[1]
    d_tweets_key = 'document:' + d_id + ':tweets'
    tweets = r.lrange(d_tweets_key, 0, -1)
    for t in tweets:
        tweet = utils.remove_entities(t)
        document.append(parser.unescape(' '.join(tweet.split())))
        ts = ts + 1
    documents.append(' '.join(document))

"""
stemmers = {
    'english': SnowballStemmer('english'),
    'spanish': SnowballStemmer('spanish'),
}
"""

print "docs: ", ds
print "tweets: ", ts

norml = []
for tweet in documents:
    #stemmer = stemmers[lang]
    if type(tweet) == str:
        tweet = tweet.decode('utf-8')
    text = utils.strip_accents(tweet)
    text = utils.remove_stopwords(text, lang)

    norml.append(text)

t0 = time()
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(norml)

print "done in %fs" % (time() - t0)
print "n_samples: %d, n_features: %d" % X.shape
print

from sklearn import metrics

from sklearn.cluster import KMeans, MiniBatchKMeans


km = MiniBatchKMeans(n_clusters=5, init='k-means++', n_init=1,
                         init_size=1000,
                         batch_size=1000, verbose=1)

"""    km = KMeans(n_clusters=true_k, init='random', max_iter=100, n_init=1,
            verbose=1)"""

print "Clustering sparse data with %s" % km
t0 = time()
km.fit(X)
print "done in %0.3fs" % (time() - t0)
print

#print "Homogeneity: %0.3f" % metrics.homogeneity_score(labels, km.labels_)
#print "Completeness: %0.3f" % metrics.completeness_score(labels, km.labels_)
#print "V-measure: %0.3f" % metrics.v_measure_score(labels, km.labels_)
#print "Adjusted Rand-Index: %.3f" % \
#    metrics.adjusted_rand_score(labels, km.labels_)
#print "Silhouette Coefficient: %0.3f" % metrics.silhouette_score(
#    X, labels, sample_size=1000)

print