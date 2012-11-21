import re
from nltk.corpus import stopwords
import unicodedata
import httplib
import urlparse


def remove_stopwords(sentence, lang='english'):

    #We only want to work with lowercase for the comparisons
    sentence = sentence.lower()

    #remove punctuation and split into seperate words
    words = re.findall(r'\w+', sentence, flags=re.UNICODE | re.LOCALE)

    #This is the more pythonic way
    important_words = filter(lambda x: x not in stopwords.words(lang), words)

    return " ".join(important_words)


def strip_accents(s):
    return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))


def clean(s, lang):
    s = strip_accents(s)
    s = remove_stopwords(s, lang)
    return s


def clean2(s):
    s = strip_accents(s)
    s = remove_stopwords(s, 'spanish')
    s = remove_stopwords(s, 'english')
    return s


def stem(s, lang='english'):
    from nltk.stem import SnowballStemmer
    stemmer = SnowballStemmer(lang)
    return " ".join(map(stemmer.stem, s.split()))


def andl(x, y):
    return x and y


def unshorten_url(url):
    parsed = urlparse.urlparse(url)
    h = httplib.HTTPConnection(parsed.netloc)
    resource = parsed.path
    if parsed.query != "":
        resource += "?" + parsed.query
    h.request('HEAD', resource)
    response = h.getresponse()
    if response.status / 100 == 3 and response.getheader('Location'):
        return unshorten_url(response.getheader('Location'))  # changed to process chains of short urls
    else:
        return url
