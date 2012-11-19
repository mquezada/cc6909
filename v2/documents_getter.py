from redis import Redis
from hashlib import md5
from urllib2 import quote
import utils


TWITTER = 'https://api.twitter.com/1/statuses/show.json?id=%s'


def generate_documents():
    tag = '[generate_documents]'
    redis = Redis()
    keys = redis.keys('event:*:title')

    for e_key in keys:
        print tag, 'event: "%s"' % redis.get(e_key)
        event_id = e_key.split(':')[1]
        tweets_keys = redis.keys('tweet:*:' + event_id)

        for t_key in tweets_keys:
            tweet_id = t_key.split(':')[1]
            urls = eval(redis.get('tweet:' + tweet_id + ':urls'))

            if len(urls) == 0:
                t_id = redis.get('tweet:' + tweet_id + ':id_str')
                doc = TWITTER % t_id
                print tag, 'got url', doc
                id = md5(quote(doc)).hexdigest()
                redis.set('document:' + id + ':url', doc)
                redis.set('document:' + id + ':' + event_id, 0)
                redis.rpush('document' + id + ':tweets', tweet_id)

            for url in urls:
                field = url['expanded_url']
                if field is not None and field != '':
                    possibly_short_url = url['expanded_url']
                else:
                    possibly_short_url = url['url']

                try:
                    doc = utils.unshorten_url(possibly_short_url)
                    print tag, 'got url', doc
                    id = md5(quote(doc)).hexdigest()
                    redis.set('document:' + id + ':url', doc)
                    redis.set('document:' + id + ':' + event_id, 0)
                    redis.rpush('document:' + id + ':tweets', tweet_id)
                except Exception, e:
                    print tag, e
                    print tag, 'url=', possibly_short_url


def main():
    generate_documents()


if __name__ == '__main__':
    main()
