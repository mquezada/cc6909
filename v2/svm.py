from nltk.stem import SnowballStemmer
from redis import Redis
import nltk
import utils
import numpy
import HTMLParser

parser = HTMLParser.HTMLParser()


def remove_entities(tweet_id):
    r = Redis()
    key = 'tweet:' + tweet_id
    text = r.get(key + ':text').decode('utf-8')
    mentions = eval(r.get(key + ':user_mentions'))
    hashtags = eval(r.get(key + ':hashtags'))
    urls = eval(r.get(key + ':urls'))

    for entity in mentions + hashtags + urls:
        i = entity['indices']
        text = text.replace(text[i[0]:i[1] + 1], ' ' * (i[1] - i[0] + 1))

    return text


r = Redis()
r_events = r.keys('event:*:title')

test = []
for k in r_events:
    print r.get(k)
    id = k.split(':')[1]
    docs = r.keys('document:*:' + id)
    for doc in docs:
        d_id = doc.split(':')[1]
        d_tweets_key = 'document:' + d_id + ':tweets'
        tweets = r.lrange(d_tweets_key, 0, -1)
        for t in tweets:
            tweet = remove_entities(t)
            test.append(tweet)
    break


stemmer = SnowballStemmer('spanish')
texts = []
for tweet in test:
    text = utils.clean2(parser.unescape(tweet))
    col = nltk.Text(nltk.word_tokenize(text))
    texts.append(col)

corpus = nltk.TextCollection(texts)
unique_terms = list(set(corpus))


def TFIDF(document):
    word_tfidf = []
    for word in unique_terms:
        word_tfidf.append(corpus.tf_idf(word, document))
    return word_tfidf


### And here we actually call the function and create our array of vectors.
vectors = [numpy.array(TFIDF(f)) for f in texts]
print vectors[0]
print "Vectors created."
print "First 10 words are", unique_terms[:10]
print "First 10 stats for first document are", vectors[0][0:10]
