import events_crawler
import events_enricher
import documents_getter


def main():
    # step 1
    events_crawler.get_news()
    events_crawler.get_festivals()

    # step 2
    events_enricher.enrich_events()

    # step 3
    documents_getter.generate_documents()


if __name__ == '__main__':
    main()
