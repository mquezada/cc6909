'''
Created on 24/06/2012

@author: mquezada
'''

import simplejson as json
from simplejson import JSONDecodeError
from redis import Redis
import sys, traceback

class Tweet(object):
    '''
    Wrapper for a tweet
    '''


    def __init__(self, data):
        '''
        creates a representation of a tweet from its json object
        @param data: dictionary of tweet data retrieved by GET SEARCH
        '''
        
        try: 
            #data = json.loads(json_string)
        
            self.news_id = data['news_id']
            self.created_at = data['created_at']
            self.from_user = data['from_user']
            self.from_user_id = data['from_user_id']
            self.from_user_id_str = data['from_user_id_str']
            self.from_user_name = data['from_user_name']
            self.geo = data['geo']
            self.id = data['id']
            self.id_str = data['id_str']
            self.iso_language_code = data['iso_language_code']
            self.metadata =  data['metadata']
            self.profile_image_url = data['profile_image_url']
            self.profile_image_url_https = data['profile_image_url_https']
            self.source = data['source']
            self.text = data['text']
            self.to_user = data['to_user']
            self.to_user_id = data['to_user_id']
            self.to_user_id_str = data['to_user_id_str']
            self.to_user_name = data['to_user_name']
            
            if data.has_key('in_reply_to_status_id'):
                self.in_reply_to_status_id = data['in_reply_to_status_id']
                self.in_reply_to_status_id_str =  data['in_reply_to_status_id_str']
            
        except:
            print "Exception in user code:"
            print '-'*60
            traceback.print_exc(file=sys.stdout)
            print '-'*60
        
        
    def save(self):
        '''
        saves this objects in current redis instance as a hash
        - key: 'tweet:<id>:<key>'
        - value: '<value>'        
        '''
        
        r = Redis()
        
        for k,v in self.__dict__.items():
            r_key = 'tweet:%s:%s' % (self.id, k)