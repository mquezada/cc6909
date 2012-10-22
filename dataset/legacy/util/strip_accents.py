import unicodedata

def strip_accents(s):
   return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))

def main():
	s = raw_input("String: ")
	print strip_accents(s.decode('utf-8'))

if __name__ == '__main__':
	main()