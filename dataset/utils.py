import re
from nltk.corpus import stopwords
import unicodedata


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
