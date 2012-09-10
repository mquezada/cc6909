import urllib, urllib2
from model.event import Event
from util.logger import log
import simplejson as json

"""
Geo.getEvents
"""

API_KEY = '92b7d449964a3e43a78529d51a30bde7'
URL = 'http://ws.audioscrobbler.com/2.0/?method=geo.getevents&location=%s&api_key=%s&format=json&festivalsonly=1'

def get_events(location):
	#location_encoded = urllib.urlencode(location)
	url = URL % (location, API_KEY)

	net = urllib2.urlopen(url)		
	data = net.read()
	try:
		js = json.loads(data)
	except Exception as e:
		log(e)
		return []

	return js

def save_events(location):
	js = get_events(location)

	if len(js) == 0:		
		return None

	if js.has_key('error'):
		log(js['message'])
		return None

	tot = 0
	for event_data in js['events']['event']:
		print "Event title: %s" % event_data['title']
		e = Event(event_data)
		tot += 1
		e.save()
	print "Crawled %d events" % tot
	return tot

def main():
	save_events('london')

if __name__ == '__main__':
	main()
