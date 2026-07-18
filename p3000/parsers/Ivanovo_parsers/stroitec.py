from pprint import pprint
from random import randint

from loguru import logger
from bs4 import BeautifulSoup
import lxml

import re

from p3000.parsers.base import BaseParserSelenium


class StroiTecParser(BaseParserSelenium):
    def __init__(self, err_name = None, headless: bool = True, retry_count: int = 3, exel: bool = False, single: bool = False):
        super().__init__(
            start_url='https://zhk-ledovyi-park-ivanovo.ru/',
            site_name='stroitec',
            headless=headless,
            retry_count=retry_count,
            exel=exel,
            err_name=err_name if err_name else ["single", 'StroiTec'],
            single=single
        )
        self.cnt: int = 0
        self.driver = None

        self.iter_count: int = 0

        self.pars_links: list[str] = []

    @staticmethod
    def check_type_kv(text: str):
        if 'однокомнатная' in text.lower():
            return '1К'
        elif 'двухкомнатная' in text.lower():
            return '2К'
        elif 'трёхкомнатная' in text.lower():
            return '3К'
        elif 'четырёхкомнатная' in text.lower():
            return '4К'
        else:
            return 'СТ'

    def pars_data(self):
        self.driver.get('https://zhk-ledovyi-park-ivanovo.ru/apartments/')

        cnt_while = 0
        while True:
            sp = BeautifulSoup(self.driver.page_html, 'lxml')
            if 'Показать еще' in sp.select_one('div.more > a').text and cnt_while <= 10:
                cnt_while += 1
                self.driver.run_js("document.querySelector('div.more > a.btn_more.btn').click()")
                self.driver.sleep(randint(1, 3))
                self.driver.scroll()
                continue

            self.driver.sleep(randint(3, 5))
            break

        soup = BeautifulSoup(self.driver.page_html, 'lxml')

        for item in soup.select_one('div.filter_result').select('div.item'):
            if 'по запросу' in item.select_one('div.text_container > div.params').select('div.param')[-1].text:
                continue
            else:
                data = item.select_one('div.text_container > div.params').select('div.param')
                full_price = int(data[-1].select_one('div._comment').text[3:-1].replace(' ', ''))

                dct = {
                    'Тип': self.check_type_kv(data[0].select_one('div._comment').text),
                    'S общ': float(item.get('data-area')),
                    'S жил': '-',
                    'S кухни': '-',
                    'Отд.': '-',
                    'С/у': '-',
                    'Балкон': '-',
                    'Этаж': '-',
                    '№ объекта': '-',
                    'ЖК, оч. и корп.': 'ЖК Ледовый Парк',
                    'Продавец': 'ООО СЗ «СТРОЙТЭК»',
                    'Район': 'г. Иваново, ул. Велижская',
                    'Сдача': '-',
                    'Цена 100%': full_price,
                    'за м2': int(full_price/float(item.get('data-area'))),
                    'Баз. цена': '-',
                    'Вознаграж.': ''
                }
                self.result_mass.append(
                    dct
                )

    def pars_all_data(self) -> None:
        try:
            self.pars_data()
            self.floor_count = len(self.result_mass)
        except Exception as ex:
            self._fatal_error = True
            logger.error(f'Fatal ERROR VT ->\n{ex}\n\n')

        logger.info(f'VY; VT flats count == {self.floor_count}')


# if __name__ == '__main__':
#     per = StroiTecParser(
#         exel=True,
#         # headless=Tru,
#     )
#     per.run()