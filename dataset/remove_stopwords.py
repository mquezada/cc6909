import re
from nltk.corpus import stopwords

def remove_stopwords(sentence):

	#We only want to work with lowercase for the comparisons
	sentence = sentence.lower()

	#remove punctuation and split into seperate words
	words = re.findall(r'\w+', sentence, flags = re.UNICODE | re.LOCALE) 

	#This is the more pythonic way
	important_words = filter(lambda x: x not in stopwords.words('spanish'), words)

	return important_words 