from boilerpipe.extract import Extractor
import utils

tag = '[content_extractor]'


def extract_content(html):
    extractor = Extractor('ArticleExtractor', html=html)
    real_content = extractor.getText()

    return real_content


def process_content(real_content, lang):
    real_content = utils.strip_accents(real_content)
    real_content = utils.remove_stopwords(real_content, lang)
    real_content = utils.stem(real_content, lang)
    return real_content


# se usa el codigo en page_downloader y no aca
def process_dataset(redis):
    import guess_language
    pages = redis.keys('page:*:raw_content')

    for page in pages:
        page_id = page.split(':')[1]
        extracted = redis.get('page:%s:extracted' % page_id)

        if extracted is None:
            html = redis.get(page)
            if html is not None and html != '':
                try:
                    content = extract_content(html)
                    lang = guess_language.guessLanguageName(content)
                    lang = lang.lower()
                    try:
                        print tag, "extracting", page_id
                        content = process_content(content, lang)
                    except Exception, e:
                        print tag, e
                        content = process_content(content, 'english')

                    redis.set('page:%s:extracted' % page_id, 1)
                    redis.set('page:%s:content' % page_id, content)
                except Exception:
                    pass
