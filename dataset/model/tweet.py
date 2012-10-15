'''
Created on 24/06/2012

@author: mquezada
'''

import sys
import traceback


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
            self.event_id = ''

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

        except:
            print "Exception in user code:"
            print '-' * 60
            traceback.print_exc(file=sys.stdout)
            print '-' * 60
