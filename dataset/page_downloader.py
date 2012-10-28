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
            # print threading.currentThread().name, "get"
            url, method, params = self.queue.get()
            # print threading.currentThread().name, "got"
            self.queue.task_done()
            # print threading.currentThread().name, "done"
            #grabs urls of hosts from the interwebz
            try:
                url = urllib2.unquote(url)
                # print threading.currentThread().name, "downloading"
                page = urllib2.urlopen(url)
                url_expanded = page.url
                content = page.read()
                method(content, url_expanded, params)
                # print threading.currentThread().name, "saved"
            except Exception, ex:
                # print threading.currentThread().name, "exception"
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
    """checks current redis instance and downloads pages if necessary"""
    redis = Redis()
    pipe = redis.pipeline()

    def save_page(content, url_expanded, params):
        page_id = params[0]
        url = params[1]
        pipe = params[2]

        print F, threading.currentThread().name, "- page_id:", page_id, ". Saving url", urllib2.unquote(url)
        rkey = '%s:%s:raw_content' % ('page', page_id)
        pipe.set(rkey, content.decode('utf-8', errors='ignore'))

        rkey = '%s:%s:expanded_url' % ('page', page_id)
        pipe.set(rkey, url_expanded)

    pages = redis.keys("page:*:raw_content")
    sites = []
    method = save_page
    for elem in pages:
        if redis.get(elem) == '':
            page_id = elem.split(":")[1]
            url = redis.get("page:%s:url" % page_id)
            params = (page_id, url, pipe)

            entry = (url, method, params)
            sites.append(entry)

    get_pages(sites)
    print F, "executing redis pipeline"
    print F, reduce(utils.andl, pipe.execute(), True)
