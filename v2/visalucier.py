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


### urls por cantidad de tweets q la mencionan
urls2 = []
for k in r.keys('document:*:url'):
    urls2.append((r.get(k), len(r.lrange('document:' + k.split(':')[1] + ':tweets', 0, -1))))

print sorted(urls2, key=lambda x: x[1])
