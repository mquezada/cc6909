import settings
import simplejson as json
from urllib import urlencode
from urllib2 import urlopen
from urllib2 import quote, unquote
from model.page import Page
from model.event import Event
from model.festival import Festival
from redis import Redis
import urlparse


class Crawler(object):
    """docstring for Crawler"""

    def __init__(self,):
        super(Crawler, self).__init__()

    def __save_events(self, events, pages):
        import utils
        redis = Redis()
        pipe = redis.pipeline()

        count = 0
        for event in events:
            for key, value in event.__dict__.iteritems():
                r_key = '%s:%s:%s' % (event.type, event.id, key)
                r_value = value

                if pipe.set(r_key, r_value):
                    count += 1

        for page in pages:
            # para saber en la llave el evento padre sin tener que acceder
            r_key = 'page:%s:news_%s' % (page.id, page.parent_id)
            pipe.set(r_key, 0)

            for key, value in page.__dict__.iteritems():
                r_key = 'page:%s:%s' % (page.id, key)
                r_value = value

                if pipe.set(r_key, r_value):
                    count += 1

        print '[crawler/redis]', "executing redis pipeline"
        print '[crawler/redis]', reduce(utils.andl, pipe.execute(), True)
        print '[crawler/redis]', 'saved', count, 'objects'

    def get_top_news(self):
        tag = "[crawler/get_top_news]"

        base_url = settings.GN_BASE_URL
        editions = settings.GN_EDITIONS
        topics = settings.GN_TOPICS
        num_news = settings.GN_NUM_NEWS

        params = {
            'v': '1.0',
            'ned': '',
            'topic': '',
            'rsz': num_news
        }

        events = []
        pages = []

        for edition in editions:
            for topic in topics:
                params['ned'] = edition
                params['topic'] = topic

                url = base_url + '?' + urlencode(params)
                print tag, 'getting url', url
                response = urlopen(url)
                data = response.read()

                if data != '':
                    news = json.loads(data)
                else:
                    return None

                if news['responseStatus'] != 200:
                    return None

                for result in news['responseData']['results']:
                    data = {}
                    data['title'] = result['titleNoFormatting']
                    data['date'] = result['publishedDate']
                    data['url'] = result['url']
                    data['type'] = 'news'

                    # quitar la query para tener una unica url
                    par = urlparse.urlparse(unquote(data['url']))
                    data['url'] = quote(par.scheme + '://' + par.netloc + par.path)

                    event = {}
                    event['title'] = data['title']
                    event['locale'] = edition
                    event['description'] = result['content']
                    event['date'] = data['date']
                    event['url'] = data['url']

                    event = Event(event)
                    page = Page(data)
                    page.parent_id = event.id

                    events.append(event)
                    pages.append(page)

                    print tag, "event:", data['title']

                    if not 'relatedStories' in result:
                        continue

                    for related in result['relatedStories']:
                        data = {}
                        data['title'] = related['titleNoFormatting']
                        data['date'] = related['publishedDate']
                        data['url'] = related['url']
                        data['type'] = 'news'

                        # quitar la query para tener una unica url
                        par = urlparse.urlparse(unquote(data['url']))
                        data['url'] = quote(par.scheme + '://' + par.netloc + par.path)

                        page = Page(data)
                        page.parent_id = event.id
                        pages.append(page)

                        print tag, "page:", data['title']

        self.__save_events(events, pages)

    def get_festivals(self):
        base_url = settings.LASTFM_BASE_URL
        api_key = settings.LASTFM_API_KEY

        tag = '[crawler/lastfm]'

        festivals = []
        params = {
            'method': 'geo.getevents',
            'location': '',
            'api_key': api_key,
            'format': 'json',
            'festivalsonly': 1
        }

        for location, lang in settings.LASTFM_LOCATIONS.iteritems():
            params['location'] = location
            url = base_url + '?' + urlencode(params)
            response = urlopen(url)
            data = response.read()
            try:
                js = json.loads(data)
            except Exception, e:
                print tag, e
                return None
            if 'error' in js:
                print tag, js['message']
            for data in js['events']['event']:
                title = data['title']
                date = data['startDate']
                data['lang'] = lang

                print tag, 'festival: %s - %s' % (title, date)

                festival = Festival(data)
                festivals.append(festival)

        self.__save_events(festivals, [])


def main():
    crawler = Crawler()
    crawler.get_top_news()
    crawler.get_festivals()


if __name__ == '__main__':
    main()
