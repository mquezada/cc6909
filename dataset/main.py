from news_crawler import crawl_current_day, crawl_week_later
from webpage_retriever import *
from festivals_crawler import crawl_tweets_for_event
from lastfm import save_events
from twitter import get_access_token
import datetime
from redis import Redis
import sys

F = "[main]"

def main():
	r = Redis()
	#get_access_token()

	print F, "getting news from google news"

	#crawl_current_day()
	#crawl_week_later()	
	download_pages()

	print F, "getting news from google news; done"
	print F, "getting festivals from lastfm (santiago, london)"

	#save_events('santiago')
	#save_events('london')

	print F, "getting festivals from lastfm; done"
	print F, "current festivals in dataset"

	festivals = r.keys('festival:*:startDate')
	for key in festivals:
		startDate = r.get(key)
		fid = key.split(":")[1]

		startDate = datetime.datetime.strptime(startDate, "%a, %d %b %Y %H:%M:%S")		
		if datetime.datetime.today() >= startDate:			
			print F, '"%s...". ID: %s' % (r.get('festival:%s:title' % fid)[0:20], fid)

	try:
		while True:
			to_crawl = raw_input("%s Enter festival id: " % F)
			if to_crawl != '':
				crawl_tweets_for_event(to_crawl)
	except KeyboardInterrupt:
		print ""
		print F, "exit"
		sys.exit()

if __name__ == '__main__':
	main()