from redis import Redis 

class Page(object):

	def __init__(self, data):
		
		self.url = data['url']
		self.title = data['title']
		self.locale = data['locale']
		self.content = data['content']
		self.date = data['date']
		self.type = data['type']		
		self.id = data['id']				
		self.parent_id = self.id

		self.raw_content = ''
		
	def save(self):
		'''
		saves this object in current redis instance as
		- key: news:<id>:<key>
		- value: <value>
		'''
		r = Redis()
		for k,v in self.__dict__.items():
			key = 'page:%s:%s' % (self.id, k)
			value = v
			r.set(key, value)