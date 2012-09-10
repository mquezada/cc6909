from redis import Redis 

class Event(object):

	def __init__(self, data):		
		self.title = data['title']
		self.locale = data['locale']
		self.description = data['description']
		self.date = data['date']		
		self.id = data['id']	

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