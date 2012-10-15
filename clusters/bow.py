#-*- coding: utf-8 -*-
from redis import Redis 
from nltk.tokenize import RegexpTokenizer
import re
from tfidf import *

docs = {}
docs_only_text = []

def get_doc_repr(redis, redis_id):	
	tokenizer = RegexpTokenizer("[\w’]+", flags=re.UNICODE)
	content = redis.get('page:%s:content' % redis_id)
	return (tokenizer.tokenize(content), content)

def __get_doc_list(lang='en_us'):
	r = Redis()
	for k in r.keys('page:*:locale'):
		locale = r.get(k)
		if locale == lang:
			id = k.split(':')[1]
			doc_repr = get_doc_repr(r, id)

			tokenized = doc_repr[0]
			doc_text = doc_repr[1]

			docs.update({id : tokenized})
			docs_only_text.append(doc_text)
		else:
			continue	

def __create_vocabulary(lang='en_us'):	
	if len(docs) == 0:
		__get_doc_list()

	vocabulary = set()
	for _, doc in docs.iteritems():
		vocabulary.update(doc)

	return list(vocabulary)

def create_corpus(lang='en_us'):	
	r = Redis()		
	corpus = []
	vocabulary = __create_vocabulary(lang)

	for doc in docs_only_text:
		doc_svm = {}
		for word in doc:
			try:
				idx = vocabulary.index(word);								
				value = tf_idf(word, doc, docs_only_text)
				doc_svm.update({idx : value})
			except Exception, e:
				continue
		if len(doc_svm) != 0:
			corpus.append(doc_svm)

	return corpus


def main():
	c = create_corpus('es_cl')
	print c

if __name__ == '__main__':
	main()