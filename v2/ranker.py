from redis import Redis
from twitter import get_num_retweets
from tldextract import extract
from collections import Counter
import pprint
import datetime
import time
import utils

r = Redis()


def get(id, attr):
    return r.get('tweet:' + id + ':' + attr)


def getd(id, attr):
    return r.get('document:' + id + ':' + attr)


def get_features(event_id, documents_tweet_ids):
    ids = documents_tweet_ids[event_id]
    docs = r.keys('document:*:' + event_id)

    documents = {}
    for doc in docs:
        key = doc.split(':')[1]
        documents[key] = {'url': getd(key, 'url')}

    documents_items = documents.items()

    i = 0
    domains = []
    for ids_list in ids:
        key = documents_items[i][0]
        extracted = extract(documents_items[i][1]['url'])
        if extracted.subdomain != 'www' and extracted.subdomain != '':
            domain = extracted.subdomain + '.' + extracted.domain
        else:
            domain = extracted.domain
        domain = domain + '.' + extracted.tld

        domains.append(domain)
        num_tweets = len(ids_list)

        documents[key].update({
            'domain': domain,
            'num_tweets': num_tweets
        })
        i += 1
    dom_freqs = Counter(domains)
    i = 0
    j = 0
    # para cada documento
    for id_list in ids:
        print "document", i, "of", len(ids)
        key = documents_items[i][0]

        documents[key].update({
            'user_is_verified': [],
            'user_lists': [],
            'user_statuses': [],
            'user_friends': [],
            'retweets': [],
            'tweets_lengths': [],
            'is_retweet': [],
            'user_created_at': [],
            'user_geo_enabled': [],
            'user_followers': [],

        })

        # para cada tweet
        for id in id_list:
            user_is_verified = int(get(id, 'user_verified') == 'True')
            user_lists = get(id, 'user_listed_count')
            user_statuses = get(id, 'user_statuses_count')
            user_friends = get(id, 'user_friends_count')

            if get(id, 'num_retweets') is None:
                retweets = get_num_retweets(get(id, 'id_str'))
                # bug, no se guardaron los retweets, se hace ahora
                r.set('tweet:' + id + ':num_retweets', retweets)
                time.sleep(5)  # twitter rate limit
            else:
                retweets = get(id, 'num_retweets')
            #tweets_lengths = len(documents_tweet_text[event_id][j].split())
            tweets_lengths = len(get(id, 'text').split())

            timetmp = datetime.datetime.strptime(get(id, 'user_created_at'), '%a %b %d %H:%M:%S +0000 %Y')
            user_created_at = time.mktime(timetmp.timetuple())

            user_geo_enabled = int(get(id, 'user_geo_enabled') == 'True')
            is_retweet = int(get(id, 'retweeted') == 'True')
            user_followers = get(id, 'user_followers_count')

            documents[key]['user_is_verified'].append(user_is_verified)
            documents[key]['user_lists'].append(user_lists)
            documents[key]['user_statuses'].append(user_statuses)
            documents[key]['user_friends'].append(user_friends)
            documents[key]['retweets'].append(retweets)
            documents[key]['tweets_lengths'].append(tweets_lengths)
            documents[key]['user_created_at'].append(user_created_at)
            documents[key]['user_geo_enabled'].append(user_geo_enabled)
            documents[key]['is_retweet'].append(is_retweet)
            documents[key]['user_followers'].append(user_followers)

            j += 1
        i += 1

    #pprint.pprint(documents)
    return dom_freqs, documents
    #return documents


def get_result(ev, documents_ids, clusters):
    import operator

    TWEETS = 0.152
    RTS = 0.091
    LEN = 0.091
    VERI = 0.21
    FOLLOW = 0.061
    LIST = 0.182
    STATS = 0.061
    FRND = 0.12
    GEO = 0.03

    dom_freqs, documents = get_features(ev, documents_ids)

    scores = {}
    for id, d in documents.iteritems():
        points = 0

        # !!!
        if 'num_tweets' not in d:
            scores.update({id: 0})
            continue

        tw = d['num_tweets']

        points += RTS * sum(map(int, d['retweets']))
        points += VERI * sum(d['user_is_verified'])
        points += FOLLOW * sum(map(int, d['user_followers']))
        points += LIST * sum(map(int, d['user_lists']))
        points += STATS * sum(map(int, d['user_statuses']))
        points += FRND * sum(map(int, d['user_friends']))
        points += GEO * sum(map(int, d['user_geo_enabled']))
        points += LEN * sum(d['tweets_lengths'])
        points /= tw

        points += TWEETS * tw
        scores.update({id: points})

    result = []
    for cluster in clusters:
        tmp = map(lambda x: (x, scores[x]), cluster)
        tmp = sorted(tmp, key=operator.itemgetter(1), reverse=True)[:2]
        result.append(map(lambda x: (r.get('document:%s:url' % x[0]), x[1]), tmp))

    result2 = sorted(reduce(lambda x, y: x + y, result, []), key=operator.itemgetter(1), reverse=True)
    return result, result2
