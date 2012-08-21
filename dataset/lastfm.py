import urllib, urllib2

"""
Geo.getEvents
"""

API_KEY = '92b7d449964a3e43a78529d51a30bde7'
URL = 'http://ws.audioscrobbler.com/2.0/?method=geo.getevents&location=%s&api_key=%s&format=json'

def get_events(location):
	pass