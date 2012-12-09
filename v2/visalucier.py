from redis import Redis

r = Redis()

"""
### vista por doc
r_docs = r.keys('document:*:tweets')

docs = []
for k in r_docs:
    id = k.split(':')[1]
    tweets = r.lrange(k, 0, -1)
    for t in tweets:
        tweet = r.get('tweet:' + t + ':text')
        print tweet
    print '\n\n'
"""

### vista por evento
r_events = r.keys('event:*:title')

for k in r_events:
    id = k.split(':')[1]
    docs = r.keys('document:*:' + id)
    for doc in docs:
        d_id = doc.split(':')[1]
        d_tweets_key = 'document:' + d_id + ':tweets'
        tweets = r.lrange(d_tweets_key, 0, -1)
        for t in tweets:
            tweet = r.get('tweet:' + t + ':text')
            print tweet
            print r.get('tweet:' + t + ':urls')
    print '\n\n'


### ver docs de un evento

id = '47961910adba1a7cc98dc83b7bb2e773'
docs = r.keys('document:*:' + id)
for doc in docs:
    d_id = doc.split(':')[1]
    d_tweets_key = 'document:' + d_id + ':tweets'
    tweets = r.lrange(d_tweets_key, 0, -1)
    for t in tweets:
        tweet = r.get('tweet:' + t + ':text')
        print tweet
        print r.get('tweet:' + t + ':urls')
print '\n\n'

### urls por cantidad de tweets q la mencionan
urls2 = []
for k in r.keys('document:*:url'):
    urls2.append((r.get(k), len(r.lrange('document:' + k.split(':')[1] + ':tweets', 0, -1))))

print sorted(urls2, key=lambda x: x[1])


## ver eventos
i = 0
for k in r.keys('event:*:title'):
    id = k.split(':')[1]
    sd = r.get('event:' + id + ':startDate')
    ed = r.get('event:' + id + ':endDate')
    st = '['
    if sd is not None:
        st = st + sd
    if ed is not None:
        st = st + ' - ' + ed + ']'
    else:
        st = st + ']'
    print i, '[%s]' % id, st, '-', r.get(k), len(r.keys('document:*:'+id))
    i += 1


## pruebas de tiempo
from time import time

t0 = time()
p = r.pipeline()
for k in r.keys('document:*:url'):
    p.get(k)

l = p.execute()
print str(time() - t0)

t0 = time()
l = []
for k in r.keys('document:*:url'):
    l.append(r.get(k))

print str(time() - t0)



## basura
"""
def preprocess_dataset():
    global events
    global documents_tweets, documents_events
    global tweets

    p = r.pipeline()

    evs = r.keys('event:*:title')
    ids = []
    for e in evs:
        ids.append(e.split(':')[1])
        p.get(e)
    events = zip(ids, p.execute())

    docs = r.keys('document:*:tweets')
    ids = []
    for d in docs:
        ids.append(d.split(':')[1])
        p.lrange(d, 0, -1)
    documents_tweets = zip(ids, p.execute())

    docs_e = r.keys('document:*:event_id')
    ids = []
    for e in docs_e:
        ids.append(e.split(':')[1])
        p.get(e)
    documents_events = zip(ids, p.execute())

    twts = r.keys('tweet:*:text')
    ids = []

    for t in twts:
        ids.append(t.split(':')[1])
        p.get(t)
    tweets = zip(ids, p.execute())


def generate_documents():
    documents = {}
    for id, title in events:
        print 'event:', title
        # ids de los documentos del event id
        docs_ids = [doc for doc, event_id in documents_events if event_id == id]

        documents[id] = []
        for doc_id in docs_ids:
            # ids de los tweets del document doc_id
            tweet_ids = [ids_list for d_id, ids_list in documents_tweets if d_id == doc_id][0]
            tweet_texts = []
            for tweet_id in tweet_ids:
                tweet_texts.extend([text for t_id, text in tweets if t_id == tweet_id])
            documents[id].extend(tweet_texts)
        print documents[id]
        break

from time import time
t0 = time()
generate_documents()
print str(time() - t0)
"""