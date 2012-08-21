import datetime

def log(message):
	fd = open('logs.txt', 'a')
	to_log = "%s\n%s\n%s\n\n" % (datetime.datetime.now(), "="*30, message)
	fd.write(to_log)
	fd.close()