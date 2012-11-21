from redis import Redis
from twitter import search_term
from hashlib import md5
import datetime


def save_tweets(tweets, event_id):
    redis = Redis()
    pipe = redis.pipeline()

    for tweet in tweets:
        tweet_id = tweet['id_str']
        key = 'tweet:' + md5(tweet_id).hexdigest() + ':'

        # metadata
        pipe.set(key + 'event_id', event_id)
        pipe.set(key + event_id, 0)

        # tweet data
        pipe.set(key + 'text', tweet['text'])
        pipe.set(key + 'in_reply_to_status_id_str', tweet['in_reply_to_status_id_str'])
        pipe.set(key + 'id_str', tweet['id_str'])
        pipe.set(key + 'source', tweet['source'])
        pipe.set(key + 'retweeted', tweet['retweeted'])
        pipe.set(key + 'coordinates', tweet['coordinates'])
        pipe.set(key + 'in_reply_to_screen_name', tweet['in_reply_to_screen_name'])
        pipe.set(key + 'in_reply_to_user_id_str', tweet['in_reply_to_user_id_str'])
        pipe.set(key + 'geo', tweet['geo'])
        #pipe.set(key + 'possibly_sensitive', tweet['possibly_sensitive'])
        pipe.set(key + 'created_at', tweet['created_at'])
        pipe.set(key + 'place', tweet['place'])
        pipe.set(key + 'metadata', tweet['metadata'])

        # entities (urls, hashtags, etc)
        pipe.set(key + 'hashtags', tweet['entities']['hashtags'])
        pipe.set(key + 'urls', tweet['entities']['urls'])
        pipe.set(key + 'user_mentions', tweet['entities']['user_mentions'])

        # user data
        pipe.set(key + 'user_id_str', tweet['user']['id_str'])
        pipe.set(key + 'user_verified', tweet['user']['verified'])
        pipe.set(key + 'user_profile_image_url_https', tweet['user']['profile_image_url_https'])
        pipe.set(key + 'user_followers_count', tweet['user']['followers_count'])
        pipe.set(key + 'user_listed_count', tweet['user']['listed_count'])
        pipe.set(key + 'user_statuses_count', tweet['user']['statuses_count'])
        pipe.set(key + 'user_description', tweet['user']['description'])
        pipe.set(key + 'user_friends_count', tweet['user']['friends_count'])
        pipe.set(key + 'user_location', tweet['user']['location'])
        pipe.set(key + 'user_geo_enabled', tweet['user']['geo_enabled'])
        pipe.set(key + 'user_screen_name', tweet['user']['screen_name'])
        pipe.set(key + 'user_lang', tweet['user']['lang'])
        pipe.set(key + 'user_favourites_count', tweet['user']['favourites_count'])
        pipe.set(key + 'user_name', tweet['user']['name'])
        pipe.set(key + 'user_created_at', tweet['user']['created_at'])
        pipe.set(key + 'user_time_zone', tweet['user']['time_zone'])

        pipe.execute()
    print 'saved', len(tweets), 'tweets'


def enrich_event(redis_key):
    tag = '[events_enricher]'
    redis = Redis()
    queries = redis.lrange(redis_key, 0, -1)
    tweets = []

    for query in queries:
        #print tag, 'searching "%s"' % query.decode('utf-8', errors='ignore')
        tweets.extend(search_term(query.decode('utf-8', errors='ignore')))

    print tag, 'got', len(tweets), 'tweets'
    event_id = redis_key.split(':')[1]
    save_tweets(tweets, event_id)


def enrich_events():
    """
    solo buscar en la ventana de 1 dia antes a 1 semana despues
    """
    tag = '[events_enricher]'
    redis = Redis()
    keys = redis.keys('event:*:title')

    for key in keys:
        id = key.split(':')[1]
        terms_key = 'event:' + id + ':terms'
        e_type = redis.get('event:' + id + ':type')
        e_schd = redis.get('event:' + id + ':searched')

        if e_type == 'news':
            if e_schd is None or e_schd < 2:
                print tag, 'enriching event:', redis.get('event:' + id + ':title')
                enrich_event(terms_key)
                redis.incr('event:' + id + ':searched')
        elif e_type == 'fest':
            is_festival = redis.get('event:' + id + ':is_festival')
            sevenDays = datetime.timedelta(hours=7 * 24)
            oneDay = datetime.timedelta(hours=24)
            today = datetime.datetime.today()

            startDate = redis.get('event:' + id + ':startDate')
            startDate = datetime.datetime.strptime(startDate, '%a, %d %b %Y %H:%M:%S')

            endDate = redis.get('event:' + id + ':endDate')

            if is_festival:
                if endDate is None:
                    if startDate - oneDay <= today and today <= startDate + sevenDays:
                        print tag, 'enriching event:', redis.get('event:' + id + ':title')
                        enrich_event(terms_key)
                else:
                    endDate = datetime.datetime.strptime(endDate, '%a, %d %b %Y %H:%M:%S')
                    endDate = endDate + datetime.timedelta(hours=24)

                    if startDate - oneDay <= today and today <= endDate + sevenDays:
                        print tag, 'enriching event:', redis.get('event:' + id + ':title')
                        enrich_event(terms_key)
            else:
                if startDate - oneDay <= today and today <= startDate + sevenDays:
                    print tag, 'enriching event:', redis.get('event:' + id + ':title')
                    enrich_event(terms_key)


def main():
    key = 'event:9d688ca2ff7e4539f94b4fb993527450:terms'
    enrich_event(key)

if __name__ == '__main__':
    main()
