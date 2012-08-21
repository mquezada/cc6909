'''
Created on 24/06/2012

@author: mquezada
'''

from twython import Twython
from redis import Redis
import simplejson as json
import time
from threading import Thread
from tweet import Tweet
import traceback
import sys

class TwitterCrawler(object):
    
    def __init__(self):
        self.twitter = Twython()
        self.redis = Redis()
    
    def search(self, term, newsid):
        print "search('%s','%s') called." % (term, newsid)
        self.redis.incr('news:%s:crawled_tweets' % newsid)
        
        # 1 day
        for _ in range(1,2):
            for page in xrange(1,16):
                try:
                    results = self.twitter.search(q=term, page=("%d" % page))
                    
                    for tweet_data in results['results']:
                        tweet_data['news_id'] = newsid
                        tweet = Tweet(tweet_data)                        
                        tweet.save()
                        
                except:
                    print "Exception: search('%s','%s')" % (term, newsid)
                    print "-"*60
                    traceback.print_exc(file=sys.stdout)
                    continue
                    
            time.sleep(120)
            
    def crawl_news(self):
        keys = self.redis.keys('news:*:title')
        
        key = keys[0]
        key_id = key.split(":")[1]
        if self.redis.get('news:%s:crawled_tweets' % key) is None:   
            self.search(self.redis.get(key), key_id)

        #for key in keys:
        #    url = self.redis.get(key)            
        #    key_id = key.split(":")[1]
        #    
        #    if self.redis.get('news:%s:crawled_tweets') is None:                
        #        t = Thread(target=self.search, args=(url, key_id))
        #        t.start()