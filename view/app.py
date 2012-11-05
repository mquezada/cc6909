from flask import Flask, render_template
from redis import Redis


app = Flask(__name__)
r = Redis()


@app.route('/')
def index():
    news = []
    for k in r.keys('news:*:id'):
        id = r.get(k)
        item = {}
        item['href'] = '/news/' + id
        item['title'] = r.get('news:%s:title' % id).decode('utf-8')
        news.append(item)
    fests = []
    for k in r.keys('festival:*:id'):
        id = r.get(k)
        item = {}
        item['href'] = '/fest/' + id
        item['title'] = r.get('festival:%s:title' % id).decode('utf-8')
        item['startDate'] = r.get('festival:%s:startDate' % id).decode('utf-8')
        fests.append(item)

    return render_template('index.html', news=news, fests=fests)


@app.route('/fest/<id>')
def fest(id=None):
    p = r.pipeline()
    s = 'festival:%s:' % id

    p.get(s + 'title')
    p.get(s + 'lang')
    p.get(s + 'description')
    p.get(s + 'type')
    p.get(s + 'venue')
    p.get(s + 'url')
    p.get(s + 'startDate')
    p.get(s + 'website')
    p.get(s + 'image')
    p.get(s + 'artists')

    l = p.execute()

    item = {}
    item['title'] = l[0].decode('utf-8')
    item['lang'] = l[1]
    item['description'] = l[2].decode('utf-8')
    item['type'] = l[3].decode('utf-8')
    item['venue'] = l[4]
    item['url'] = l[5]
    item['startDate'] = l[6]
    item['website'] = l[7]
    item['image'] = l[8]
    item['artists'] = l[9]

    tweets = get_tweets(id)

    return render_template('fest.html', item=item, tweets=tweets, tcount=len(tweets))


@app.route('/news/<id>')
def news(id=None):
    p = r.pipeline()
    s = 'news:%s:' % id

    p.get(s + 'title')
    p.get(s + 'locale')
    p.get(s + 'description')
    p.get(s + 'date')

    l = p.execute()

    item = {}
    item['title'] = l[0].decode('utf-8')
    item['locale'] = l[1]
    item['description'] = l[2].decode('utf-8')
    item['date'] = l[3]

    pages = get_pages(id)
    tweets = get_tweets(id)

    return render_template('news.html', item=item, pages=pages, tweets=tweets, tcount=len(tweets), pcount=len(pages))


@app.route('/page/<id>')
def page(id=None):
    import urllib
    p = r.pipeline()
    s = 'page:%s:' % id

    p.get(s + 'title')
    p.get(s + 'url')
    p.get(s + 'type')

    l = p.execute()

    item = {}
    item['title'] = l[0].decode('utf-8')
    item['url'] = urllib.unquote(l[1])
    item['type'] = l[2]

    return render_template('page.html', item=item)


@app.route('/tweet/<id>')
def tweet(id=None):
    p = r.pipeline()
    keys = r.keys('tweet:%s:*' % id)

    attrs = []
    for k in keys:
        attrs.append(k.split(':')[2])
        p.get(k)

    print attrs
    l = p.execute()
    i = 0
    item = {}

    for attr in attrs:
        item[attr] = l[i].decode('utf-8')
        i += 1

    return render_template('tweet.html', item=item, attrs=attrs)


def get_tweets(id):
    ids = r.keys('tweet:*:%s' % id)
    p = r.pipeline()
    tweets = []
    for tw in ids:
        s = 'tweet:%s:' % tw.split(':')[1]

        p.get(s + 'user_name')
        p.get(s + 'text')
        p.get(s + 'id')
        p.get(s + 'expanded_urls')
        p.get(s + 'user_screen_name')

        l = p.execute()

        tweet = {}
        tweet['user_name_href'] = 'http://twitter.com/' + l[4].decode('utf-8')
        tweet['user_name'] = l[0].decode('utf-8')
        tweet['text'] = l[1].decode('utf-8')
        tweet['href_out'] = 'https://api.twitter.com/1/statuses/show.json?id=%s&include_entities=1' % l[2]
        tweet['href'] = '/tweet/' + l[2]
        tweet['urls'] = l[3]

        tweets.append(tweet)
    return tweets


def get_pages(id):
    ids = r.keys('page:*:news_%s' % id)
    pages = []
    for pag in ids:
        id = pag.split(':')[1]
        page = {}
        page['title'] = r.get('page:%s:title' % id).decode('utf-8')
        page['href'] = '/page/' + id
        pages.append(page)
    return pages


if __name__ == '__main__':
    app.run(debug=True)
