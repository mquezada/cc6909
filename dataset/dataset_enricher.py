#-*- coding: utf-8 -*-
import HTMLParser
import twitter
import utils

tag = '[enricher]'
h = HTMLParser.HTMLParser()


def get_search_terms_news(redis, news_id, lang):
    # obtener todas las paginas hijas del event id=news_id
    # que no hayan sido procesadas antes*
    keys = redis.keys('page:*:news_%s' % news_id)

    terms = []
    for key in keys:
        id = key.split(':')[1]

        got = redis.get('page:%s:searched' % id)

        # para poder buscar 2 veces tweets de una pagina de un evento
        if got is None or got < 2:
            title = redis.get('page:%s:title' % id)
            title = title.decode('utf-8', errors='ignore')
            title = h.unescape(title)
            title = utils.strip_accents(title)
            title = utils.remove_stopwords(title, lang=lang)
            terms.append(title)

            redis.incr('page:%s:searched' % id)

    print tag, 'got', len(terms), 'search terms for news'
    return terms


# test: dataset_enricher.get_search_terms_festivals(r, '394e017af204c6b3e78474277b87cf0c')
def get_search_terms_festivals(redis, festival_id):
    title = redis.get('festival:%s:title' % festival_id)
    title = title.decode('utf-8', errors='ignore')
    title = title.lower()

    terms = [title]

    artists = redis.get('festival:%s:artists' % festival_id)
    artists = eval(artists)

    for _, v in artists.iteritems():
        if type(v) == list:
            for artist in v:
                terms.append(title + ' ' + artist)
                terms.append(artist + ' festival')
        elif type(v) == str:
            terms.append(title + ' ' + v)
            terms.append(v + ' festival')

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

    festivals_tweets = []
    pages = []
    for key in to_search_keys:
        id = key.split(':')[1]
        terms = get_search_terms_festivals(redis, id)

        for term in terms:
            tweets, pages = twitter.search_term(term)

            for tweet in tweets:
                tweet.event_id = id

            festivals_tweets.extend(tweets)
            pages.extend(pages)

    print tag, "got", len(festivals_tweets), 'tweets for festivals'
    return (festivals_tweets, pages)


def enrich_news(redis):
    keys = redis.keys('news:*:id')

    if len(keys) == 0:
        return

    news_tweets = []
    pages = []
    for key in keys:
        locale = redis.get('news:%s:locale' % key.split(':')[1])

        if locale == 'en_us':
            lang = 'english'
        else:
            lang = 'spanish'

        id = key.split(':')[1]
        terms = get_search_terms_news(redis, id, lang)

        for term in terms:
            tweets, pages = twitter.search_term(term)

            for tweet in tweets:
                tweet.event_id = id

            news_tweets.extend(tweets)
            pages.extend(pages)

    print tag, "got", len(news_tweets), 'tweets for news'
    return (news_tweets, pages)


def save_tweets(redis, tweets):
    count = 1
    pipe = redis.pipeline()

    for tweet in tweets:
        r_key = 'tweet:%s:%s' % (tweet.id, tweet.event_id)
        pipe.set(r_key, 0)

        for key, value in tweet.__dict__.iteritems():
            r_key = 'tweet:%s:%s' % (tweet.id, key)
            r_value = value

            if pipe.set(r_key, r_value):
                count += 1

    print tag, "executing redis pipeline"
    print tag, reduce(utils.andl, pipe.execute(), True)
    print tag, 'saved', count, 'objects'


def save_pages(redis, pages):
    count = 1
    pipe = redis.pipeline()

    for page in pages:
        r_key = 'page:%s:tweet_%s' % (page.id, page.parent_id)
        pipe.set(r_key, 0)

        for key, value in page.__dict__.iteritems():
            r_key = 'page:%s:%s' % (page.id, key)
            r_value = value

            if pipe.set(r_key, r_value):
                count += 1

    print tag, "executing redis pipeline"
    print tag, reduce(utils.andl, pipe.execute(), True)
    print tag, 'saved', count, 'objects'
