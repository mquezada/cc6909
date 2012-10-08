#!/usr/bin/env python
import Queue
import threading
import urllib2
import time
from util import remove_stopwords
from boilerpipe.extract import Extractor
from redis import Redis
import sys
import webarticle2text

queue = Queue.Queue()
r = Redis()

F = "[webpage_retriever]"

class ThreadUrl(threading.Thread):
    """Threaded Url Grab"""
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            #grabs host from queue
            redis_id , page, obj_type, lang = self.queue.get()

            #language
            if lang == 'es_cl':
                lang = 'spanish'
            else:
                lang = 'english'

            #grabs urls of hosts and prints first 1024 bytes of page
            try:
                url = urllib2.urlopen(page)
                content = url.read()    
            except Exception, e:
                self.queue.task_done()
                print F, str(e)
                continue                            

            # gets redis instance
            r = Redis()

            print F, "saving page %s" % page

            #saves content into redis instance
            r.set('%s:%s:raw_content' % (obj_type, redis_id), content.decode('utf-8', errors='ignore'))

            #extracts main content from page
            #real_content = webarticle2text.extractFromHTML(content)
            if content != '':
                extractor = Extractor(extractor='ArticleExtractor', html=content)#.decode('utf-8', errors='ignore'))
                real_content = extractor.getText()
                #real_content.decode('utf-8', errors='ignore')
                real_content = remove_stopwords(real_content, lang)
                
                r.set('%s:%s:content' % (obj_type, redis_id), real_content)

            #signals to queue job is done
            self.queue.task_done()

def get_pages(sites_list):
    """
sites_list is a list of tuples
[(id, url, type),..]
    """

    #spawn a pool of threads, and pass them queue instance
    for i in range(60):
        t = ThreadUrl(queue)
        t.setDaemon(True)
        t.start()

    #populate queue with data
    for entry in sites_list:
        queue.put(entry)

    #wait on the queue until everything has been processed
    queue.join()

def download_pages():
    """
checks current redis instance and downloads pages if necessary
    """
    r = Redis()
    keys = r.keys("page:*:raw_content")

    sites = []
    for elem in keys:
        if r.get(elem) == '':
            key = elem.split(":")[1]
            url = urllib2.unquote(r.get("page:%s:url" % key))
            locale = r.get(r.get("page:%s:locale" % key))
            tpe = 'page'

            entry = (key, url, tpe, locale)
            sites.append(entry)

    get_pages(sites)

def download_tweet_pages():
    """
    downloads pages contained in tweets
    """