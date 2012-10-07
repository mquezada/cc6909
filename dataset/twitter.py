import urllib, urllib2
import simplejson as json
from model.tweet import Tweet
import time
from threading import Thread
import oauth2 as oauth
import sys

F = "[twitter]"
SLEEP_TIME = 5

def search(query, result_type, rpp, since_id, include_entities):
	URL = "http://search.twitter.com/search.json?%s"

	params = {
		'q':query,
		'result_type':result_type,
		'rpp':rpp,
		'since_id':since_id,
		#'max_id':max_id,
		'include_entities':include_entities
	}
	try:
		enc = urllib.urlencode(params)
		net = urllib2.urlopen(URL % enc)
		data = net.read()
	except Exception, e:
		print F, e
		return []	

	try:
		js = json.loads(data)
	except Exception, e:
		return []

	return js

def search_11(query, result_type, rpp, since_id, include_entities, user_params = None):
	"""
	search method for api 1.1, it seems that the rate limit is wider now
	"""	

	url = "https://api.twitter.com/1.1/search/tweets.json"

	CONSUMER_KEY = "RH7hKZS8NtUgtNTFB4GHMQ"
	CONSUMER_SECRET = "Dp4uKEmqGM5z8NzcbZ6BjPXQDUGNrwqknGCPOYlXQg"	
	key = "21123704-NRej4tA3tKxfonEUPIb07SxcQYZ7i2Cu6GEBVf1U"
	secret = "b6lEz5Mmq5EymsvyqleeqXBVInCjDVvEZqn2ANw"

	if user_params == None:
		params = {
			'q' : query,
			'result_type' : result_type,
			'count' : rpp,
			'include_entities' : include_entities,
			'since_id' : since_id
		}
		url = "%s?%s" % (url, urllib.urlencode(params))
	else:
		url = "%s%s" % (url, user_params)

	consumer = oauth.Consumer(key=CONSUMER_KEY, secret=CONSUMER_SECRET)
	token = oauth.Token(key=key, secret=secret)
	client = oauth.Client(consumer, token)

	resp, content = client.request(
		url,
		method="GET",
		body=None,
		headers=None,
		force_auth_header=True
	)
	
	try:
		if resp['status'] == '200':
			return json.loads(content)
		else:
			return {}
	except Exception, e:
		print F, 'Exception:', e
		return {}


def search_term(query, page_id=None):
	results = []
	max_id = ''
	params = None

	print F, "search term: '%s'" % (query)

	for i in range(1,15): # 15 times at most
		js = search_11(query, result_type='mixed', rpp='100', since_id=max_id, include_entities=True, user_params=params)

		if len(js) == 0 or len(js['statuses']) == 0:						
			continue
		
		params = js['search_metadata']['next_results']
		results.extend(js['statuses'])
		time.sleep(SLEEP_TIME)
	
	tot = 0	
	for tweet_data in results:
		tweet_data['page_id'] = page_id	

		tweet = Tweet(tweet_data)					
		tot += tweet.save()
	
	return tot

def main():
	search_term('metallica', 'asdf')

if __name__ == '__main__':
	main()