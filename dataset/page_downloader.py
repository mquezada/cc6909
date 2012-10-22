import Queue
import threading
import urllib2
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
            #redis_id, page, obj_type, lang = self.queue.get()
            url, method, params = self.queue.get()

            #grabs urls of hosts from the interwebz
            try:
                page = urllib2.urlopen(url)
                content = page.read()
            except Exception, ex:
                self.queue.task_done()
                print F, str(ex)
                continue

            method(content, params)

            #signals to queue job is done
            self.queue.task_done()


def get_pages(sites_list):
    """sites_list is a list of tuples [(page, *method),..]"""

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
    """checks current redis instance and downloads pages if necessary"""
    redis = Redis()

    def save_page(content, params):
        page_id = params[0]
        url = params[1]
        print F, "page_id:", page_id, ". Saving url", url
        rkey = '%s:%s:raw_content' % ('page', page_id)
        redis.set(rkey, content.decode('utf-8', errors='ignore'))

    pages = redis.keys("page:*:raw_content")
    sites = []
    method = save_page
    for elem in pages:
        if redis.get(elem) == '':
            page_id = elem.split(":")[1]
            url = urllib2.unquote(redis.get("page:%s:url" % page_id))
            params = (page_id, url)

            entry = (url, method, params)
            sites.append(entry)

    get_pages(sites)

#extracts main content from page
#real_content = webarticle2text.extractFromHTML(content)
#if content != '':
#content = strip_accents.strip_accents(content.decode('utf-8', errors='ignore'))
#extractor = Extractor(extractor='ArticleExtractor', html=content)#.decode('utf-8', errors='ignore'))
#real_content = extractor.getText()
#r.set('%s:%s:content' % (obj_type, redis_id), real_content)
#from boilerpipe.extract import Extractor
