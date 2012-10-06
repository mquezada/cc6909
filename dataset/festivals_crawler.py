from lastfm import save_events
from twitter import search_term
from redis import Redis 
from HTMLParser import HTMLParser
from util.remove_stopwords import remove_stopwords
from util.strip_accents import strip_accents
import sys

F = "[festivals]"

def crawl_tweets_for_event(event_id):
	r = Redis()
	p = HTMLParser()

	total_tweets = 0

	event_title = r.get("festival:%s:title" % event_id).decode('utf-8')
	event_title = strip_accents(event_title)
	event_title = p.unescape(event_title)
	event_title = remove_stopwords(event_title)

	artists = r.get("festival:%s:artists" % event_id)

	for k,v in eval(artists).items():
		if type(v) == list:
			for artist in v:
				print F, "searching tweets for %s %s" % (k, artist)
				total_tweets += search_term(artist)
		elif type(v) == str:
			print F, "searching tweets for %s %s" % (k, v)
			total_tweets += search_term(v)

	r.incr("festival:%s:crawled_times" % event_id)

	print F, "searching tweets for festival title: %s" % event_title 
	total_tweets += search_term(event_title, event_id) # newsid
	print F, "total tweets: %d" % total_tweets

