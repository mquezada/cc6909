from google_news import GoogleNews
from twitter import search_term
from redis import Redis

def crawl_current_day():
	gn = GoogleNews()
	r = Redis()

	gn.get_topnews()

	all_news = r.keys('news:*:title')

	i = 1
	total = 0
	print "total news: %d" % len(all_news)
	for key_news_title in all_news:
		newsid = key_news_title.split(':')[1] 

		if r.get('news:%s:crawled_day' % newsid) is None:			
			i += 1
			news_title = r.get(key_news_title)
			r.incr('news:%s:crawled_day' % newsid)

			print "searching tweets for news: %s" % news_title 
			total += search_term(news_title, newsid) # search by title
	print "total news searched: %d" % i
	print "total tweets crawled: %d" % total

def crawl_week_later():
	gn = GoogleNews()
	r = Redis()
	
	all_news = r.keys('news:*:title')

	i = 1
	total = 0
	print "total news: %d" % len(all_news)	
	for key_news_title in all_news:
		newsid = key_news_title.split(':')[1] 

		if r.get('news:%s:crawled_week' % newsid) is None:
			i += 1			
			news_title = r.get(key_news_title)
			r.incr('news:%s:crawled_week' % newsid)

			print "searching tweets for news: %s" % news_title 
			total += search_term(news_title, newsid) # search by title
	print "total news searched: %d" % i
	print "total tweets crawled: %d" % total

def main():
	crawl_current_day()

if __name__ == '__main__':
	main()