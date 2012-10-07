'''
Created on 24/06/2012

@author: mquezada
'''

import simplejson as json
from simplejson import JSONDecodeError
from redis import Redis
import sys, traceback
import ttp

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
            
            # internal
            self.page_id = data['page_id']

            # context
            self.created_at = data['created_at']
            self.id = data['id_str']

            # tweet
            self.text = data['text']
            self.is_retweet = data['retweeted']
            self.retweets = data['retweet_count']
            self.geo = data['geo']
            self.place = data['place']
            self.in_reply_to_user_id = data['in_reply_to_user_id_str']
            self.in_reply_to_status_id = data['in_reply_to_status_id_str']
            self.in_reply_to_screen_name = data['in_reply_to_screen_name']

            # entities
            self.hashtags = data['entities']['hashtags']
            self.urls = data['entities']['urls']

            # user
            self.user_id = data['user']['id_str']
            self.user_is_verified = data['user']['verified']
            self.user_image_url_https = data['user']['profile_image_url_https']
            self.user_followers_count = data['user']['followers_count']
            self.user_listed_count = data['user']['listed_count']
            self.user_statuses_count = data['user']['statuses_count']
            self.user_description = data['user']['description']
            self.user_location = data['user']['location']
            self.user_screen_name = data['user']['screen_name']
            self.user_name = data['user']['name']
            self.user_url = data['user']['url']
            self.user_created_at = data['user']['created_at']
            self.user_timezone = data['user']['time_zone']

            """
            self.from_user = data['from_user']
            self.from_user_id = data['from_user_id']
            self.from_user_id_str = data['from_user_id_str']
            self.from_user_name = data['from_user_name']
            
            
            self.id_str = data['id_str']
            self.iso_language_code = data['iso_language_code']
            self.metadata =  data['metadata']
            self.profile_image_url = data['profile_image_url']
            self.profile_image_url_https = data['profile_image_url_https']
            self.source = data['source']
            
            self.to_user = data['to_user']
            self.to_user_id = data['to_user_id']
            self.to_user_id_str = data['to_user_id_str']
            self.to_user_name = data['to_user_name']
            
            if data.has_key('in_reply_to_status_id'):
                self.in_reply_to_status_id = data['in_reply_to_status_id']
                self.in_reply_to_status_id_str =  data['in_reply_to_status_id_str']

            #data for urls in tweet
            p = ttp.Parser()
            tweet_obj = p.parse(self.text.decode('utf-8', errors='ignore'))
            self.urls = tweet_obj.urls
            self.urls_raw_content = []
            self.urls_content = []
            """
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
        if r.get('tweet:%s:id' % self.id) == None:
            for k,v in self.__dict__.items():
                r_key = 'tweet:%s:%s' % (self.id, k)
                r_value = v
                r.set(r_key, r_value)
            return 1
            
        return 0