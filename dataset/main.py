

from google_news_crawler import GoogleNewsCrawler
from twitter_crawler import TwitterCrawler

def main():
    g = GoogleNewsCrawler()
    g.crawl_topnews('en')
    g.crawl_topnews('es')

    t = TwitterCrawler()
    t.crawl_news()


if __name__ == '__main__':
    main()