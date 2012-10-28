import re
from nltk.corpus import stopwords
import unicodedata
from HTMLParser import HTMLParser


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


def stem(s, lang='english'):
    from nltk.stem import SnowballStemmer
    stemmer = SnowballStemmer(lang)
    return " ".join(map(stemmer.stem, s.split()))


def andl(x, y):
    return x and y
