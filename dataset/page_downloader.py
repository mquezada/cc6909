import Queue
import threading
import urllib2
import urlparse
from redis import Redis

queue = Queue.Queue()
F = "[page_downloader]"


class ThreadUrl(threading.Thread):
    """Threaded Url Grab"""
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            # grabs host from queue

            url, method, params = self.queue.get()
            url = url.lower()

            self.queue.task_done()

            # descartar urls con solo el domino, eg 'http://www.google.com/?q=1'
            p = urlparse.urlparse(url)
            if p.path == '/':
                continue

            #grabs urls of hosts from the interwebz
            try:
                url = urllib2.unquote(url)

                page = urllib2.urlopen(url)
                url_expanded = page.url
                content = page.read()
                method(content, url_expanded, params)

            except Exception, ex:

                print F, str(ex)
                continue


def get_pages(sites_list):
    """sites_list is a list of tuples [(page, *method, (params,..)),..]"""

    #spawn a pool of threads, and pass them queue instance
    for _ in range(60):
        thr = ThreadUrl(queue)
        thr.setDaemon(True)
        thr.start()

    #populate queue with data
    for entry in sites_list:
        queue.put(entry)

    #wait on the queue until everything has been processed
    queue.join()


def download_pages():
    import utils
    import guess_language
    from content_extractor import extract_content, process_content
    """checks current redis instance and downloads pages if necessary"""
    redis = Redis()
    pipe = redis.pipeline()

    def save_page(content, url_expanded, params):
        page_id = params[0]
        pipe = params[1]

        rkey = '%s:%s:raw_content' % ('page', page_id)
        pipe.set(rkey, content.decode('utf-8', errors='ignore'))

        rkey = '%s:%s:expanded_url' % ('page', page_id)
        pipe.set(rkey, url_expanded)

        if content is not None and content != '':
            try:
                content = extract_content(content)
                lang = guess_language.guessLanguageName(content)
                lang = lang.lower()
                try:
                    content = process_content(content, lang)
                except Exception:
                    content = process_content(content, 'english')

                pipe.set('page:%s:extracted' % page_id, 1)
                pipe.set('page:%s:content' % page_id, content)
            except Exception:
                pass

        print F, "saved page", url_expanded

    pages = redis.keys("page:*:raw_content")
    sites = []
    method = save_page
    for elem in pages:
        if redis.get(elem) == '':
            page_id = elem.split(":")[1]
            url = redis.get("page:%s:url" % page_id)
            params = (page_id, pipe)

            entry = (url, method, params)
            sites.append(entry)

    get_pages(sites)
    print F, "executing redis pipeline"
    print F, reduce(utils.andl, pipe.execute(), True)
