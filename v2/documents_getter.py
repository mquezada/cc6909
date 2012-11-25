from redis import Redis
from hashlib import md5
from urllib2 import quote
import threading
import utils
import Queue


TWITTER = 'https://api.twitter.com/1/statuses/show.json?id=%s'
tag = '[generate_documents]'
queue = Queue.Queue()
redis = Redis()


class ThreadDoc(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        with redis.pipeline() as pipe:
            while True:

                event_id, tweet_id, urls = self.queue.get()
                self.queue.task_done()

                for url in urls:
                    field = url['expanded_url']
                    if field is not None and field != '':
                        possibly_short_url = url['expanded_url']
                    else:
                        possibly_short_url = url['url']

                    try:
                        doc = utils.unshorten_url(possibly_short_url)
                        #print tag, 'got url', doc
                        id = md5(quote(doc)).hexdigest()
                        pipe.set('document:' + id + ':url', doc)
                        pipe.set('document:' + id + ':' + event_id, 0)
                        pipe.set('document:' + id + ':event_id', event_id)
                        pipe.rpush('document:' + id + ':tweets', tweet_id)
                        pipe.incr('tweet:' + tweet_id + ':documented')
                        print tag, 'saved:', reduce(lambda x, y: x > 0 and y > 0, pipe.execute(), True), '[' + event_id, doc + ']'
                    except Exception, e:
                        print tag, e
                        print tag, 'url=', possibly_short_url


def send_to_threads(entries):
    for entry in entries:
        queue.put(entry)

    for _ in range(100):
        thr = ThreadDoc(queue)
        thr.setDaemon(True)
        thr.start()

    queue.join()


def generate_documents():
    keys = redis.keys('event:*:title')
    pipe = redis.pipeline()
    entries = []
    no = 0

    for e_key in keys:
        print tag, 'event: "%s"' % redis.get(e_key)
        event_id = e_key.split(':')[1]
        tweets_keys = redis.keys('tweet:*:' + event_id)

        for t_key in tweets_keys:
            tweet_id = t_key.split(':')[1]
            cont = redis.get('tweet:' + tweet_id + ':documented')

            if cont is not None:
                continue

            urls = eval(redis.get('tweet:' + tweet_id + ':urls'))

            if len(urls) == 0:
                t_id = redis.get('tweet:' + tweet_id + ':id_str')
                doc = TWITTER % t_id
                id = md5(quote(doc)).hexdigest()
                pipe.set('document:' + id + ':url', doc)
                pipe.set('document:' + id + ':' + event_id, 0)
                pipe.set('document:' + id + ':event_id', event_id)
                pipe.rpush('document:' + id + ':tweets', tweet_id)
                no += 1
                pipe.incr('tweet:' + tweet_id + ':documented')
                pipe.execute()
            else:
                entry = (event_id, tweet_id, urls)
                entries.append(entry)

    print tag, 'processed', no, 'tweets'
    print tag, 'sent to threads', len(entries), 'entries (w/ possibly more than 1 url each)'
    send_to_threads(entries)


def main():
    generate_documents()


if __name__ == '__main__':
    main()
