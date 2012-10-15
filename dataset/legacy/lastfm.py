import urllib, urllib2
from model.festival import Festival
import simplejson as json
import sys

"""
DEPRECATED!!!
"""

API_KEY = '92b7d449964a3e43a78529d51a30bde7'
URL = 'http://ws.audioscrobbler.com/2.0/?method=geo.getevents&location=%s&api_key=%s&format=json&festivalsonly=1'

F = "[lastfm]"

def get_events(location):
	#location_encoded = urllib.urlencode(location)
	url = URL % (location, API_KEY)

	net = urllib2.urlopen(url)		
	data = net.read()
	try:
		js = json.loads(data)
	except Exception as e:
		print F, e
		return []

	return js

def save_events(location):
	js = get_events(location)

	if len(js) == 0:		
		return None

	if js.has_key('error'):
		print F, js['message']
		return None

	tot = 0
	for event_data in js['events']['event']:
		print F, "festival: %s - %s " % (event_data['title'], event_data['startDate'])
		e = Festival(event_data)
		tot += 1
		e.save()
	print F, "crawled %d festivals" % tot
	return tot

def main():
	save_events('london')

if __name__ == '__main__':
	main()
