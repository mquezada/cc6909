from hashlib import md5


class Page(object):
    def __init__(self, data):
        self.url = data['url']
        self.title = data['title']
        self.raw_content = ''
        self.content = ''
        self.date = data['date']
        self.type = data['type']
        self.id = md5(data['url']).hexdigest()
        self.parent_id = self.id
