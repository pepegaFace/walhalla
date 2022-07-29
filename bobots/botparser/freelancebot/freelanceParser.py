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

ParserResult = collections.namedtuple(
    'ParseResult',
    (
        'url',
        'title_name',
        'article_name',
    ),
)

class Client:
    keywords = ['python+нейросеть', 'laravel+верстка', 'frontend', 'фронтэнд', 'верстка', 'телеграм', 'telegram',
                'bot', 'бот']
    dictionary_list = []

    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36',
             'Accept-Language':'ru',
        }
        self.result = []
        self.json_result = []

    def load_page(self, keyword, page: int = None,):
        url = f'https://freelance.habr.com/tasks?q={keyword}'
        res = self.session.get(url=url)
        res.raise_for_status()
        logger.debug(f'Parsing {url}...')
        return res.text

    def parse_page(self, text: str, keyword):
        soup = bs4.BeautifulSoup(text, 'lxml')
        container = soup.select('div.task__column_desc')
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

        title_block = block.select_one('a')
        if not title_block:
            logger.error(f'no title_block on https://freelance.habr.com{url}{title_block}')
            return

        # Wrangler /
        title_block = title_block.text
        title_block = title_block.replace('/', '').strip()

        urll = f'https://freelance.habr.com{url}'
        response = requests.get(urll)
        soup1 = bs4.BeautifulSoup(response.text, 'lxml')
        get_content = soup1.select('div.task__description')
        for itm in get_content:
            itm = itm.text
            itm = itm.replace('/', '').strip()
        if not itm:
            logger.error('no content')
            return

        self.result.append(ParserResult(
            url=f'https://freelance.habr.com{url}',
            title_name=title_block,
            article_name=itm,
        ))

        self.dictionary_list.append({
            'url': f'https://freelance.habr.com{url}',
            'title': title_block,
            'article': itm,
            'keyword': keyword,
            'send': False
        })

    def save_result(self):
        # Читаем файл и пишем его в existing_data
        if not os.path.isfile('freelance.json'):
            with open('freelance.json', 'w') as f:
                logger.debug(f'Creating json file...')
                json.dump(self.dictionary_list, f, indent=3, ensure_ascii=False)
                f.close()
        else:
            with open('freelance.json') as file:
                existing_data = json.load(file)
                file.close()
            list_of_urls = [url for dict in existing_data for url in dict.values()]
            merged_data = existing_data
            appended = False
            # Проверяем для каждой записи, есть ли она в existing_data,
            # если нет - добавляем в конец листа найденную запись.
            if existing_data:
                for item in self.dictionary_list:
                    if item['url'] in list_of_urls:
                        logger.debug(f'{item["url"]} - {item["title"] } already exist.')
                    else:
                        logger.debug(f'Appending: {item["url"]} - {item["title"] }to the list.')
                        merged_data.append(item)
                        appended = True
                # Если в лист merged_data была добавлена запись - переписываем файл.
                if appended:
                    with open('freelance.json', 'w') as f:
                        logger.debug(f'Writing json file...')
                        json.dump(merged_data, f, indent=3, ensure_ascii=False)
                        f.close()

    def run(self):
        for keyword in self.keywords:
            text = self.load_page(keyword=keyword)
            self.parse_page(text=text, keyword=keyword)
            self.save_result()


# class Command(BaseCommand):
#     help = 'parse Full'
#     def handle(self, *args, **options):
#         p = Client()
#         p.run()


def main():
    p = Client()
    p.run()


if __name__ == '__main__':
    main()