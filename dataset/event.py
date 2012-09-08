
"""
Formato basado en
http://www.lastfm.es/api/show/geo.getEvents
"""
from hashlib import md5
from redis import Redis 

class Event(object):

	def __init__(self, data):
		self.id = data['id']
		self.title = data['title']
		self.artists = data['artists']
		self.venue = data['venue']
		self.startDate = data['startDate']		
		self.description = data['description']
		self.image = data['image']
		self.lastfmTag = data['tag']
		self.url = data['url']
		self.website = data['website']

		if data.has_key('tags'):
			self.tags = data['tags']

		if data.has_key('endDate'):
			self.endDate = data['endDate']
		
		self.id = md5(data['id']).hexdigest()
		
	def save(self):
		'''
		saves this object in current redis instance as
		- key: news:<id>:<key>
		- value: <value>
		'''
		r = Redis()
		for k,v in self.__dict__.items():
			key = 'event:%s:%s' % (self.id, k)
			value = v
			r.set(key, value)