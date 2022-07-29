import logging
import collections
import csv
import requests
import bs4
import lxml
from lxml.doctestcompare import strip
import time
import json
import os.path

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('FullCont')

news_dict = {}

ParserResult = collections.namedtuple(
    'ParseResult',
    (
        'url',
        'title_name',
        'article_name',
    ),
)


class Client:
    keywords = ['laravel+js', 'питон', 'python', 'frontend', 'фронтэнд', 'верстка', 'телеграм', 'telegram', 'bot', 'бот']

    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36',
            'Accept-Language': 'ru',
        }
        self.result = []
        self.dictionary_list = []


    def load_page(self, keyword, page: int = None,):
        url = f'https://kwork.ru/projects?c=11&keyword={keyword}'
        res = self.session.get(url=url)
        res.raise_for_status()
        return res.text

    def parse_page(self, text: str, keyword):
        soup = bs4.BeautifulSoup(text, 'lxml')
        container = soup.select_one('div.wants-content').select('div.wants-card__left')
        for block in container:
            self.parse_block(block=block, keyword=keyword)

    def parse_block(self, block, keyword):
        url_block = block.select_one('a')
        if not url_block:
            logger.error('no url_block')
            return
        url = url_block.get('href')
        if not url:
            logger.error('no href')
            return

        title_block = url_block
        if not title_block:
            logger.error(f'no title_block on {url} {title_block}')
            return

        title_block = title_block.text
        title_block = title_block.replace('/', '').strip()

        itm = block.select_one('div.breakwords.first-letter.js-want-block-toggle.js-want-block-toggle-full')
        if not itm:
            logger.error(f'no itm on {url} {title_block}')
            return

        itm = itm.text.replace('/', '').strip()

        self.result.append(ParserResult(
            url=f'{url}',
            title_name=title_block,
            article_name=itm,
        ))

        self.dictionary_list.append({
            'url': f'{url}',
            'title': title_block,
            'article': itm,
            'keyword': keyword,
            'send': False
        })

    def save_result(self):
        # Читаем файл и пишем его в existing_data
        if not os.path.isfile('kwork.json'):
            with open('kwork.json', 'w') as f:
                logger.debug(f'Creating json file...')
                json.dump(self.dictionary_list, f, indent=3, ensure_ascii=False)
                f.close()
        else:
            with open('kwork.json') as file:
                existing_data = json.load(file)
                file.close()
            merged_data = existing_data
            list_of_urls = [url for dict in existing_data for url in dict.values()]
            appended = False
            # Проверяем для каждой записи, есть ли она в existing_data найденные нами записи,
            # если нет - добавляем в конец листа найденную запись.
            if existing_data:
                for item in self.dictionary_list:
                    if item['url'] in list_of_urls:
                        logger.debug(f'{item["url"]} - {item["title"] } already exist.')
                    else:
                        logger.debug(f'Appending: {item["url"]} - {item["title"]}  to the list.')
                        merged_data.append(item)
                        appended = True
                # Если в лист merged_data была добавлена запись - переписываем файл.
                if appended:
                    with open('kwork.json', 'w') as f:
                        logger.debug(f'Writing json file...')
                        json.dump(merged_data, f, indent=3, ensure_ascii=False)
                        f.close()

    def run(self):
        for keyword in self.keywords:
            text = self.load_page(keyword=keyword)
            self.parse_page(text=text, keyword=keyword)
            self.save_result()


def main():
    p = Client()
    p.run()


if __name__ == '__main__':
    main()