#-*- coding: utf-8 -*-
import twitter
import utils

tag = '[enricher]'


def get_search_terms_news(redis, news_id, lang):
    # obtener todas las paginas hijas del event id=news_id
    keys = redis.keys('page:*:%s' % news_id)

    terms = []
    for key in keys:
        id = key.split(':')[1]
        title = redis.get('page:%s:title' % id)
        title = title.decode('utf-8', errors='ignore')
        title = utils.strip_accents(title)
        title = utils.remove_stopwords(title, lang=lang)
        terms.append(title)

    print tag, 'got', len(terms), 'search terms for news'
    return terms


def get_search_terms_festivals(redis, festival_id, lang):
    title = redis.get('festival:%s:title' % festival_id)
    title = title.decode('utf-8', errors='ignore')
    title = utils.strip_accents(title)
    title = utils.remove_stopwords(title, lang)

    terms = [title]

    artists = redis.get('festival:%s:artists' % festival_id)
    artists = eval(artists)

    for _, v in artists.iteritems():
        if type(v) == list:
            for artist in v:
                terms.append(artist)
        elif type(v) == str:
            terms.append(v)

    print tag, 'got', len(terms), 'search terms for festivals'
    return terms


def enrich_festivals(redis):
    import datetime

    keys = redis.keys('festival:*:startDate')
    to_search_keys = []

    # solo buscar en los festivales que estan pasando ahora
    for key in keys:
        startDate = redis.get(key)
        id = key.split(':')[1]

        startDate = datetime.datetime.strptime(startDate, '%a, %d %b %Y %H:%M:%S')
        if datetime.datetime.today() >= startDate:
            to_search_keys.append(key)

    if len(keys) == 0:
        return

    # obtener el idioma dado en los datos del festival
    id_first = keys[0].split(':')[1]
    lang = redis.get('festival:%s:lang' % id_first)

    festivals_tweets = []

    for key in to_search_keys:
        id = key.split(':')[1]
        terms = get_search_terms_festivals(redis, id, lang)

        for term in terms:
            tweets = twitter.search_term(term)

            for tweet in tweets:
                tweet.event_id = id

            festivals_tweets.extend(tweets)

    print tag, "got", len(festivals_tweets), 'tweets for festivals'
    return festivals_tweets


def enrich_news(redis):
    keys = redis.keys('news:*:id')

    if len(keys) == 0:
        return

    id_first = keys[0].split(':')[1]
    first = redis.get('news:%s:locale' % id_first)

    if first == 'en_us':
        lang = 'english'
    else:
        lang = 'spanish'

    news_tweets = []
    for key in keys:

        id = key.split(':')[1]
        terms = get_search_terms_news(redis, id, lang)

        for term in terms:
            tweets = twitter.search_term(term)

            for tweet in tweets:
                tweet.event_id = id

            news_tweets.extend(tweets)

    print tag, "got", len(news_tweets), 'tweets for news'
    return news_tweets


def save_tweets(redis, tweets):
    count = 0
    for tweet in tweets:
        for key, value in tweet.__dict__.iteritems():
            r_key = 'tweet:%s:%s' % (tweet.id, key)
            r_value = value

            if redis.set(r_key, r_value):
                count += 1
    # TODO marcar tweets que tengan URLs!
    print tag, 'saved', count, 'objects'
