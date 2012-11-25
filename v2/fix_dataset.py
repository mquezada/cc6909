# fix_dataset.py


from redis import Redis

r = Redis()

"""
for k in r.keys('document*:tweets'):
    if k[8] != ':':
        content = r.lrange(k, 0, -1)
        newkey = 'document:' + k[8:len(k)]
        r.delete(k)
        for t in content:
            r.rpush(newkey, t)



for k in r.keys('document:*:tweet'):
    content = r.lrange(k, 0, -1)
    newkey = 'document:' + k[8:len(k)] + 's'
    r.delete(k)
    for t in content:
        r.rpush(newkey, t)

"""


"""
for k in r.keys('event:*:title'):
    id = k.split(':')[1]
    print 'event:' + id + ':id', id
    r.set('event:' + id + ':id', id)



for k in r.keys('document:*:*'):

    id = k.split(':')[1]
    last = k.split(':')[2]

    if last != 'url' and last != 'tweets':
        r.set('document:' + id + ':event_id', last)


# eliminar duplicados de los terminos
for k in r.keys('event:*:type'):
    if r.get(k) == 'fest':
        key = 'event:' + k.split(':')[1] + ':terms'
        terms = list(set(r.lrange(key, 0, -1)))
        r.delete(key)
        for term in terms:
            r.rpush(key, term)
"""

for k in r.keys('event:*:type'):
    if r.get(k) == 'fest':
        key = 'event:' + k.split(':')[1] + ':terms'
        terms = r.lrange(key, 0, -1)
        if len(terms) != len(set(terms)):
            print terms
