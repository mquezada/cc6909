from google_news import GoogleNews
from util.remove_stopwords import remove_stopwords
from twitter import search_term
from redis import Redis

def crawl_current_day():
	gn = GoogleNews()
	r = Redis()

	gn.get_topnews()

	all_news = r.keys('page:*:title')

	i = 1
	total = 0
	print "total pages: %d" % len(all_news)
	for key_news_title in all_news:
		newsid = key_news_title.split(':')[1] 

		# only interested in news here
		if r.get('page:%s:type' % newsid) != 'news':
			continue

		# and pages not already crawled in its first day
		if r.get('page:%s:crawled_day' % newsid) is None:			
			i += 1

			# lang for stopwords remove
			if r.get('page:%s:locale' % newsid) == 'es_cl':
				lang = 'spanish'
			else: 
				lang = 'english'

			news_title_stopwords = r.get(key_news_title)
			news_title = remove_stopwords(r.get(key_news_title), lang=lang)
			print "searching tweets for news (w/ sw): \"%s\"" % news_title_stopwords			
			print "searching tweets for news (w/o sw): \"%s\"" % news_title

			# mark its news' first day as searched
			r.incr('page:%s:crawled_day' % newsid)

			# search by title in twitter
			total += search_term(news_title, newsid) 

	print "total news searched: %d" % i
	print "total tweets crawled: %d" % total







def crawl_week_later():
	gn = GoogleNews()
	r = Redis()
	
	all_news = r.keys('page:*:title')

	i = 1
	total = 0
	print "total news: %d" % len(all_news)	
	for key_news_title in all_news:
		newsid = key_news_title.split(':')[1] 

		if r.get('page:%s:crawled_week' % newsid) is None:
			i += 1

			if r.get('page:%s:locale' % newsid) == 'es_cl':
				lang = 'spanish'
			else: 
				lang = 'english'

			news_title_stopwords = r.get(key_news_title)
			news_title = remove_stopwords(r.get(key_news_title), lang=lang)
			print "searching tweets for news (w/ sw): \"%s\"" % news_title_stopwords			
			print "searching tweets for news (w/o sw): \"%s\"" % news_title

			print "searching tweets for news: %s" % news_title 
			total += search_term(news_title, newsid) # search by title
	print "total news searched: %d" % i
	print "total tweets crawled: %d" % total

def main():
	crawl_current_day()

if __name__ == '__main__':
	main()