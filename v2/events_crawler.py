import settings
from urllib import urlencode
from urllib2 import urlopen
import simplejson as json
from redis import Redis
from hashlib import md5
import HTMLParser
import utils


def get_news():
    tag = '[crawler/get_news]'
    redis = Redis()
    parser = HTMLParser.HTMLParser()

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

    for edition, lang in editions.iteritems():
        for topic in topics:
            params['ned'] = edition
            params['topic'] = topic

            url = base_url + '?' + urlencode(params)
            print tag, 'GET - url=' + url
            resp = urlopen(url)
            data = resp.read()

            if data != '':
                news = json.loads(data)
            else:
                continue

            if news['responseStatus'] != 200:
                print tag, 'ERROR - url=' + url, '- status_code=' + news['responseStatus']
                continue

            for result in news['responseData']['results']:
                n_url = result['url']
                n_title = result['titleNoFormatting']
                n_type = 'news'
                n_date = result['publishedDate']
                n_desc = result['content']
                n_id = md5('event:' + n_url).hexdigest()

                print tag, 'Event: "%s"' % n_title

                key = 'event:' + n_id + ':'
                redis.set(key + 'url', n_url)
                redis.set(key + 'title', n_title)
                redis.set(key + 'type', n_type)
                redis.set(key + 'date', n_date)
                redis.set(key + 'desc', n_desc)

                if not 'relatedStories' in result:
                    continue

                for related in result['relatedStories']:
                    title = utils.clean(parser.unescape(related['titleNoFormatting']), lang)
                    redis.rpush(key + 'terms', title)


def get_festivals():
    base_url = settings.LASTFM_BASE_URL
    api_key = settings.LASTFM_API_KEY
    redis = Redis()

    tag = '[crawler/lastfm]'

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
            continue

        if 'error' in js:
            print tag, js['message']
            continue

        for data in js['events']['event']:
            key = 'event:' + md5('event:' + data['id']).hexdigest() + ':'

            title = data['title']

            redis.set(key + 'type', 'fest')
            redis.set(key + 'title', data['title'])
            redis.set(key + 'artists', data['artists'])
            redis.set(key + 'venue', data['venue'])
            redis.set(key + 'startDate', data['startDate'])
            redis.set(key + 'description', data['description'])
            redis.set(key + 'image', data['image'])
            redis.set(key + 'url', data['url'])
            redis.set(key + 'website', data['website'])
            redis.set(key + 'lang', lang)

            if 'endDate' in data:
                redis.set(key + 'endDate', data['endDate'])
            if 'tags' in data:
                redis.set(key + 'tags', data['tags'])

            print tag, 'festival: %s - %s' % (title, data['startDate'])

            term = utils.clean(title, lang)
            redis.rpush(key + 'terms', term)

            artists = data['artists']
            for _, v in artists.iteritems():
                if type(v) == list:
                    for artist in v:
                        redis.rpush(key + 'terms', utils.clean(artist, lang))
                        redis.rpush(key + 'terms', utils.clean(title + ' ' + artist, lang))
                elif type(v) == str:
                    redis.rpush(key + 'terms', utils.clean(v, lang))
                    redis.rpush(key + 'terms', utils.clean(title + ' ' + v, lang))


def main():
    get_festivals()


if __name__ == '__main__':
    main()
