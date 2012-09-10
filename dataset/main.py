from news_crawler import crawl_current_day
from webpage_retriever import check_dataset

def main():
	crawl_current_day()
	check_dataset()

if __name__ == '__main__':
	main()