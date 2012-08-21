'''
Created on 24/06/2012

@author: mquezada
'''

from hashlib import md5
from redis import Redis
import sys, traceback

class News(object):
    '''
    Wrapper object for a google news entry
    '''


    def __init__(self, data):
        '''
        Creates a news object from data param
        @param data: dictionary of news data        
        '''
        
        try:
            self.id = md5(data['link']).hexdigest()
            
            self.link = data['link']
            self.links = data['links']
            self.lang = data['lang']
            self.title = data['title']
            self.published = data['published']
            self.published_parsed = data['published_parsed']
            self.summary = data['summary']
            self.summary_detail = data['summary_detail']
            self.tags = data['tags']
            self.guidislink = data['guidislink']
        
        except:
            print "Exception in user code:"
            print '-'*60
            traceback.print_exc(file=sys.stdout)
            print '-'*60
        
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