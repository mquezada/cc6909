import urllib, urllib2
import simplejson as json
from model.tweet import Tweet
import time
from threading import Thread

URL = "http://search.twitter.com/search.json?%s"
SLEEP_TIME = 24

def search(query, result_type, rpp, since_id, include_entities):
	params = {
		'q':query,
		'result_type':result_type,
		'rpp':rpp,
		'since_id':since_id,
		#'max_id':max_id,
		'include_entities':include_entities
	}
	enc = urllib.urlencode(params)
	net = urllib2.urlopen(URL % enc)
		
	data = net.read()
	try:
		js = json.loads(data)
	except Exception, e:
		return []

	return js

def search_term(query, page_id=None):
	results = []
	max_id = ''

	print "search term: '%s'" % (query)
	for i in range(1,16): # 15 times at most
		js = search(query, 'mixed', '100', max_id, True)

		if len(js) == 0 or len(js['results']) == 0:
			continue

		max_id = js['max_id_str']
		results.append(js)
		time.sleep(SLEEP_TIME)

	tot = 0
	for result in results:
		for tweet_data in result['results']:
			tweet_data['page_id'] = page_id

			tweet = Tweet(tweet_data)			
			tot += 1
			tweet.save()

	return tot

def main():
	search_term('metallica', 'asdf')

if __name__ == '__main__':
	main()