import urllib2
from redis import Redis 

# urllib.unquote('http%3A%2F%2Fwww.voanews.com%2Fcontent%2Fsyria_denies_defection_of_vice_president%2F1490635.html')
# -> 'http://www.voanews.com/content/syria_denies_defection_of_vice_president/1490635.html'


"""
downloads and saves the page content in 
'url' in current redis instance

the key is the form of 'news:<id>' or
'event:<id>' for news or music event, respectively

"""
def get_page(url):
	return urllib2.urlopen(url).read()

def main():
	print get_page("http://t.co/JLdh1CRP")

if __name__ == '__main__':
	main()

