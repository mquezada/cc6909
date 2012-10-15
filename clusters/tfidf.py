import math

def freq(word, doc):
	return doc.count(word)

def word_count(doc):
	return len(doc)

def tf(word, doc):
	return (freq(word, doc) / float(word_count(doc)))

def num_docs_containing(word, doc_list):
	count = 0

	for doc in doc_list:
		if freq(word, doc) > 0:
			count += 1
	return count # + 1 avoids division by 0, but by definition count is at least 1

def idf(word, doc_list):
	return math.log(len(doc_list) / float(num_docs_containing(word, doc_list)))

def tf_idf(word, doc, doc_list):
	return tf(word, doc) * idf(word, doc_list)

def main():
	doc_list = ['hola esto es un documento', 'mi documento la lleva', 'jason funk disipa patitos']
	words = ['hola', 'documento', 'lleva', 'jason', 'funk', 'disipa', 'patitos']

	for doc in doc_list:
		for word in words:
			print tf_idf(word, doc, doc_list)


if __name__ == '__main__':
	main()