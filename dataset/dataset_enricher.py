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

    news_tweets = []
    for key in keys:
        locale = redis.get('news:%s:locale' % key.split(':')[1])

        if locale == 'en_us':
            lang = 'english'
        else:
            lang = 'spanish'

        id = key.split(':')[1]
        terms = get_search_terms_news(redis, id, lang)

        for term in terms:
            tweets = twitter.search_term(term)

            for tweet in tweets:
                tweet.event_id = id

            news_tweets.extend(tweets)

    print tag, "got", len(news_tweets), 'tweets for news'
    return news_tweets


def generate_pages_from(tweets, redis):
    """downloads content from urls in tweets' text and generates
        pages from each one"""
    import page_downloader

    def save_content(content, params):
        import lxml.html
        import model.page
        lcontent = lxml.html.fromstring(content)
        url = params[0]
        tweet_id = params[1]

        data = {}
        data['url'] = url
        data['title'] = lcontent.find('.//title').text
        data['date'] = ''
        data['type'] = 'from_tweet'

        page = model.page.Page(data)
        page.parent_id = tweet_id
        page.raw_content = content

        print tag, "got page from tweet: '%s' - %s" % (page.title, page.url)
        r_key = 'page:%s:%s' % (page.id, tweet_id)
        redis.set(r_key, 0)

        for key, value in page.__dict__.iteritems():
            r_key = 'page:%s:%s' % (page.id, key)
            r_value = value

            redis.set(r_key, r_value)

    sites = []
    method = save_content
    for tweet in tweets:
        for url in tweet.expanded_urls:
            params = (url, tweet.id)
            entry = (url, method, params)
            sites.append(entry)

    page_downloader.get_pages(sites)


def save_tweets(redis, tweets):
    count = 0

    for tweet in tweets:
        r_key = 'tweet:%s:%s' % (tweet.id, tweet.event_id)
        redis.set(r_key, 0)

        for key, value in tweet.__dict__.iteritems():
            r_key = 'tweet:%s:%s' % (tweet.id, key)
            r_value = value

            if redis.set(r_key, r_value):
                count += 1

    print tag, 'saved', count, 'objects'
