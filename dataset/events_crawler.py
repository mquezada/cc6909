from lastfm import save_events
from twitter import search_term
from redis import Redis 
from util.remove_stopwords import remove_stopwords

def crawl_tweets_for_event(event_id):
	r = Redis()

	total_tweets = 0
	event_title = remove_stopwords(r.get("event:%s:title" % event_id))

	r.incr("event:%s:crawled_times" % event_id)

	print "searching tweets for event: %s" % event_title 
	total_tweets += search_term(event_title) # newsid
	print "total tweets: %d" % total_tweets

