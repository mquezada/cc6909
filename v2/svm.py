from nltk.stem import SnowballStemmer
from redis import Redis
import utils
import HTMLParser
from sklearn.cluster import KMeans, MiniBatchKMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from time import time


r = Redis()
parser = HTMLParser.HTMLParser()
r_events = map(lambda x: x.split(':')[1], r.keys('event:*:title'))
documents = {}
documents_ids = {}
stemmers = {
    'spanish': SnowballStemmer('spanish'),
    'english': SnowballStemmer('english')
}


def id(k):
    return k.split(':')[1]


def generate_documents_for(event_id):
    lang = r.get('event:' + event_id + ':lang')
    if lang is None:
        lang = 'spanish'
    docs = r.keys('document:*:' + event_id)
    documents[event_id] = []
    documents_ids[event_id] = []

    keys = []
    for eid in docs:
        keys.append(id(eid))

    docs = set(keys)
    for doc_id in docs:
        #doc_id = id(doc_key)
        tweet_ids = r.lrange('document:' + doc_id + ':tweets', 0, -1)
        documents_ids[event_id].append(tweet_ids)

        document = []
        for tweet_id in tweet_ids:
            # esto se puede mejorar...
            tweet = utils.remove_entities(tweet_id)
            tweet = parser.unescape(' '.join(tweet.split()))
            if len(tweet) == 0 or len(tweet.split()) == 0:
                continue
            tweet = utils.strip_accents(tweet)
            tweet = utils.remove_stopwords(tweet, lang)
            tweet = ' '.join([stemmers[lang].stem(token) for token in tweet.split()])
            document.append(tweet)
        documents[event_id].append(' '.join(document))


# 10-20 segs por evento
def generate_documents():
    events = r.keys('event:*:title')
    for event_key in events:
        event_id = id(event_key)
        lang = r.get('event:' + event_id + ':lang')
        docs = r.keys('document:*:' + event_id)
        documents[event_id] = []
        for doc_key in docs:
            doc_id = id(doc_key)
            tweet_ids = r.lrange('document:' + doc_id + ':tweets', 0, -1)
            document = []
            for tweet_id in tweet_ids:
                # esto se puede mejorar...
                tweet = utils.remove_entities(tweet_id)
                tweet = parser.unescape(' '.join(tweet.split()))
                if len(tweet) == 0 or len(tweet.split()) == 0:
                    continue
                tweet = utils.strip_accents(tweet)
                tweet = utils.remove_stopwords(tweet, lang)
                tweet = ' '.join([stemmers[lang].stem(token) for token in tweet.split()])
                document.append(tweet)
            documents[event_id].append(' '.join(document))


def cluster_event(event_id):
    t0 = time()
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(documents[event_id])

    print "done in %fs" % (time() - t0)
    print "n_samples: %d, n_features: %d" % X.shape
    print

    km = MiniBatchKMeans(n_clusters=5, init='k-means++', n_init=1,
                             init_size=1000,
                             batch_size=1000, verbose=1)

    """km = KMeans(n_clusters=true_k, init='random', max_iter=100, n_init=1,
                verbose=1)"""

    print "Clustering sparse data with %s" % km
    t0 = time()
    km.fit(X)
    print "done in %0.3fs" % (time() - t0)
    print
    return km


## test
t = time()
#ev = '82cefb914318e7a9e6664550080f259a'
#ev = '47961910adba1a7cc98dc83b7bb2e773'
#ev = '62d63b809018510981a48d263a646ef5'
ev = 'b60e4389f7910448e4972f622afb9260'
generate_documents_for(ev)

C = cluster_event(ev)

## clusters
p = zip(documents_ids[ev], C.labels_)

clusters = []
for i in range(C.n_clusters):
    ids = map(lambda x: x[0], filter(lambda x: x[1] == i, p))
    texts = []
    for id in ids:
        text = map(lambda x: r.get('tweet:' + x + ':text'), id)
        texts.append(text)
    clusters.append(texts)

print str(time() - t)

