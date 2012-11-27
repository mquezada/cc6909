import events_crawler
import events_enricher
import documents_getter
from time import time


def main():
    tt0 = time()
    # step 1
    t0 = time()
    events_crawler.get_news()
    print "time:", str((time() - t0))

    t0 = time()
    events_crawler.get_festivals()
    print "time:", str((time() - t0))

    t0 = time()
    # step 2
    events_enricher.enrich_events()
    print "time:", str((time() - t0))

    t0 = time()
    # step 3
    documents_getter.generate_documents()
    print "time:", str((time() - t0))

    print "total: ", str((time() - tt0))
if __name__ == '__main__':
    main()
