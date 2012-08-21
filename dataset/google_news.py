import simplejson as json
import urllib2
from logger import log
from news import News

class GoogleNews(object):
	
	#https://ajax.googleapis.com/ajax/services/search/news?v=1.0&topic=s

	@staticmethod
	def get_topnews(results=8):
		URL = 'https://ajax.googleapis.com/ajax/services/search/news?v=1.0&ned=%s&topic=%s&rsz=%d'
		editions = {'es_cl':'Chile', 'en_us':'EEUU'}
		topics = {'w':'Internacional', 'h':'Titulares'}
		i = 0
		for edition, ed_name in editions.items():			
			for topic, top_name in topics.items():
				url = URL % (edition, topic, results)
				response = urllib2.urlopen(url)
				data = response.read()

				news = json.loads(data)
				if news['responseStatus'] == 200:
					for result in news['responseData']['results']:
						print repr("Crawled news: %s" % result['titleNoFormatting'])
						result['edition'] = ed_name
						result['topic'] = top_name

						n = News(result)
						n.save()

						news_id = n.id

						for related in result['relatedStories']:
							print repr("\tRelated news: %s" % related['titleNoFormatting'])
							related['edition'] = ed_name
							related['topic'] = top_name

							n = News(related)
							n.parent_id = news_id
							n.save()
							i += 1
				else:
					log(news['responseDetails'])					
		print "total news collected: %d" % i

def main():
	GoogleNews.get_topnews()

if __name__ == '__main__':
	main()