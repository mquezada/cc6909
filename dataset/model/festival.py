from hashlib import md5


class Festival(object):
    def __init__(self, data):
        self.type = 'festival'
        self.title = data['title']
        self.artists = data['artists']
        self.venue = data['venue']
        self.startDate = data['startDate']
        self.description = data['description']
        self.image = data['image']
        self.lastfmTag = data['tag']
        self.url = data['url']
        self.website = data['website']
        self.lang = data['lang']

        if 'tags' in data:
            self.tags = data['tags']

        if 'endDate' in data:
            self.endDate = data['endDate']

        self.id = md5(data['id']).hexdigest()
