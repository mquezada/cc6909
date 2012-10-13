from redis import Redis 


r = Redis()

for k in r.keys('page:*:content')