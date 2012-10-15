from hashlib import md5


class Event(object):
    def __init__(self, data):
        self.title = data['title']
        self.locale = data['locale']
        self.description = data['description']
        self.date = data['date']
        self.type = 'news'
        self.id = md5('event' + data['url']).hexdigest()
