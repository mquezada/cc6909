
"""
Formato basado en
https://ajax.googleapis.com/ajax/services/search/news?v=1.0&topic=w&ned=es_cl
"""
from hashlib import md5
from redis import Redis 

class News(object):

	def __init__(self, data):

		#self.content = data['content']
		self.url = data['url']
		self.title = data['titleNoFormatting']
		self.location = data['location']
		self.publisher = data['publisher']
		self.publishedDate = data['publishedDate']
		self.language = data['language']
		self.id = md5(data['url']).hexdigest()

		self.topic = data['topic']
		self.edition = data['edition']

		self.parent_id = self.id

	def save(self):
		'''
		saves this object in current redis instance as
		- key: news:<id>:<key>
		- value: <value>
		'''
		r = Redis()
		for k,v in self.__dict__.items():
			key = 'news:%s:%s' % (self.id, k)
			value = v
			r.set(key, value)