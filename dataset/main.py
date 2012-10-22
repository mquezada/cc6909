F = "[main]"


# paso 1
def get_events():
    from crawler import Crawler
    crawler = Crawler()

    print "[main] getting news"
    crawler.get_top_news()

    print "[main] getting festivals"
    crawler.get_festivals()


# paso 2
def download_pages_from_events():
    from page_downloader import download_pages
    download_pages()


# paso 3
def get_tweets():
    from dataset_enricher import enrich_festivals, enrich_news, generate_pages_from, save_tweets
    from redis import Redis

    redis = Redis()

    # news tweets
    tweets = enrich_news(redis)

    # festival tweets
    tweets.extend(enrich_festivals(redis))

    # create pages from tweets
    # this downloads and saves pages from tweets text url
    generate_pages_from(tweets, redis)

    # save tweets
    save_tweets(redis, tweets)


def main():
    print F, "getting news and festivals"
    get_events()

    print F, "downloading pages from news"
    download_pages_from_events()

    print F, "getting tweets from news and festivals, and pages from tweets, saving them"
    get_tweets()


if __name__ == '__main__':
    main()
