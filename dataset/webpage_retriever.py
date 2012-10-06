#!/usr/bin/env python
import Queue
import threading
import urllib2
import time
from util import remove_stopwords
from redis import Redis
import sys

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
            redis_id , page, obj_type = self.queue.get()

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
            r.set('%s:%s:content' % (obj_type, redis_id), content)

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

def check_dataset():
    """
checks current redis instance and downloads pages if necessary
    """
    r = Redis()
    keys = r.keys("page:*:content")

    sites = []
    for elem in keys:
        if r.get(elem) == '':
            key = elem.split(":")[1]
            url = urllib2.unquote(r.get("page:%s:url" % key))
            # tpe = r.get("page:%s:type" % key)
            # type is always 'page'
            tpe = 'page'

            entry = (key, url, tpe)
            sites.append(entry)

    get_pages(sites)
