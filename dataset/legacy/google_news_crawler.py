'''
Created on 24/06/2012

@author: mquezada
'''

import feedparser
from urlparse import urlparse
import redis
import re
from news import News

class GoogleNewsCrawler(object):
    BASE_URI = 'https://news.google.com/news?output=rss'
    LANGUAGES = ('en', 'es')

    def __init__(self):
        self.url = GoogleNewsCrawler.BASE_URI
        self.redis = redis.Redis()

    def whoami(self):
        return self.__class__.__name__

    def build_url(self, params):
        """    Returns the full url for the current query, e.g.
            BASE_URI = 'http://www.google.com/?'

            @param dict, e.g. params = {'a':'b'}
            @returns string, e.g. 'http://www.google.com/?a=b'
        """
        result = self.url
        for key,value in params.items():
            result = "%s&%s=%s" % (result, key, value)
        return result

    def crawl_topnews(self, lang='en'):
        """    Returns a list of News objects representing the top news from GoogleNews
            @param lang='en' the language of the news (optional)
            @returns list of News objects with the top news
        """
        params = {
            'cf' : 'all',
            'ned' : 'us',
            'hl' : lang            
        }
        url = self.build_url(params)
        feed = feedparser.parse(url)
        
        for e in feed['entries']:
            
            url = urlparse(e['link'])
            clean_url = dict( [part.split('=') for part in url.query.split('&')] ) ['url']
            
            e['lang'] = lang
            e['link'] = clean_url
            
            news = News(e)
            news.save()
            #self.redis.set('news:%s:description' % id, GoogleNews.remove_html_tags(e.summary))

    @staticmethod
    def remove_html_tags(data):
        """ Removes html tags from data and replaces them with whitespaces """
        p = re.compile(r'<.*?>')
        return p.sub(' ', data)