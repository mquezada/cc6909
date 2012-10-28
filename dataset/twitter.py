import urllib
import simplejson as json
from model.tweet import Tweet
import time
import oauth2 as oauth
import settings
import urlparse

F = "[twitter]"
SLEEP_TIME = 5


def get_access_token():
    """
    'Three-legged' oauth taken from https://github.com/simplegeo/python-oauth2
    """
    request_token_url = 'http://twitter.com/oauth/request_token'
    access_token_url = 'http://twitter.com/oauth/access_token'
    authorize_url = 'http://twitter.com/oauth/authorize'

    consumer = oauth.Consumer(key=settings.CONSUMER_KEY, secret=settings.CONSUMER_SECRET)
    client = oauth.Client(consumer)

    # Step 1: Get a request token. This is a temporary token that is used for
    # having the user authorize an access token and to sign the request to obtain
    # said access token.

    resp, content = client.request(request_token_url, "GET")
    if resp['status'] != '200':
        raise Exception("%s Invalid response %s." % (F, resp['status']))

    request_token = dict(urlparse.parse_qsl(content))

    print "Request Token:"
    print "    - oauth_token        = %s" % request_token['oauth_token']
    print "    - oauth_token_secret = %s" % request_token['oauth_token_secret']
    print

    # Step 2: Redirect to the provider. Since this is a CLI script we do not
    # redirect. In a web application you would redirect the user to the URL
    # below.
    print "Go to the following link in your browser:"
    print "%s?oauth_token=%s" % (authorize_url, request_token['oauth_token'])
    print

    # After the user has granted access to you, the consumer, the provider will
    # redirect you to whatever URL you have told them to redirect to. You can
    # usually define this in the oauth_callback argument as well.
    accepted = 'n'
    while accepted.lower() == 'n':
        accepted = raw_input('Have you authorized me? (y/n) ')
    oauth_verifier = raw_input('What is the PIN? ')

    # Step 3: Once the consumer has redirected the user back to the oauth_callback
    # URL you can request the access token the user has approved. You use the
    # request token to sign this request. After this is done you throw away the
    # request token and use the access token returned. You should store this
    # access token somewhere safe, like a database, for future use.
    token = oauth.Token(request_token['oauth_token'],
        request_token['oauth_token_secret'])
    token.set_verifier(oauth_verifier)
    client = oauth.Client(consumer, token)

    resp, content = client.request(access_token_url, "POST")
    access_token = dict(urlparse.parse_qsl(content))

    print "Access Token:"
    print "    - oauth_token        = %s" % access_token['oauth_token']
    print "    - oauth_token_secret = %s" % access_token['oauth_token_secret']
    print
    print "You may now access protected resources using the access tokens above."
    print

    settings.OAUTH_TOKEN = access_token['oauth_token']
    settings.OAUTH_TOKEN_SECRET = access_token['oauth_token_secret']


def search_11(query, result_type, rpp, since_id, include_entities, user_params=None):
    """
    search method for api 1.1, it seems that the rate limit is wider now
    """

    url = "https://api.twitter.com/1.1/search/tweets.json"

    if user_params == None:
        params = {
            'q': query,
            'result_type': result_type,
            'count': rpp,
            'include_entities': include_entities,
            'since_id': since_id
        }
        url = "%s?%s" % (url, urllib.urlencode(params))
    else:
        url = "%s%s" % (url, user_params)

    consumer = oauth.Consumer(key=settings.CONSUMER_KEY, secret=settings.CONSUMER_SECRET)
    token = oauth.Token(key=settings.OAUTH_TOKEN, secret=settings.OAUTH_TOKEN_SECRET)
    client = oauth.Client(consumer, token)

    resp, content = client.request(
        url,
        method="GET",
        body=None,
        headers=None,
        force_auth_header=False
    )

    try:
        if resp['status'] == '200':
            return json.loads(content)
        else:
            print F, str(resp), content
            try_again = raw_input('%s Recreate access tokens? [y/n] ' % F)

            if try_again == 'y':
                get_access_token()
                print F, settings.OAUTH_TOKEN, settings.OAUTH_TOKEN_SECRET

            return search_11(query, result_type, rpp, since_id, include_entities, user_params)
    except Exception, e:
        print F, 'Exception:', e
        return {}


def search_term(query):
    tweets = []
    max_id = ''
    params = None

    print F, "search term: '%s'" % (query)
    num_tweets = str(settings.NUM_TWEETS_PER_PAGE)
    num_pages = settings.NUM_PAGES_PER_SEARCH + 1

    # 15 times at most
    for i in range(1, num_pages):
        js = search_11(query, result_type='mixed', rpp=num_tweets, since_id=max_id, include_entities=True, user_params=params)

        time.sleep(SLEEP_TIME)

        if len(js) == 0 or len(js['statuses']) == 0:
            continue

        for tweet_data in js['statuses']:
            tweet = Tweet(tweet_data)
            tweets.append(tweet)

        if 'next_results' in js['search_metadata']:
            params = js['search_metadata']['next_results']
        else:
            break

    return tweets


def main():
    print search_term('metallica')

if __name__ == '__main__':
    main()
