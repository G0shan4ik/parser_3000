import asyncio
import re

from loguru import logger
from bs4 import BeautifulSoup
import lxml

from p3000.parsers.base import BaseParserSelenium


class FenixParser(BaseParserSelenium):
    def __init__(self, err_name = None, headless: bool = True, retry_count: int = 3, exel: bool = False, single: bool = False):
        super().__init__(
            start_url='',
            site_name='fenix',
            headless=headless,
            retry_count=retry_count,
            exel=exel,
            err_name=err_name if err_name else ["single", 'Fenix'],
            single=single
        )

        self.__all_links: list[str] = [
            'https://ikfeniks.ru/#/macrocatalog/houses/1338848/bigGrid?studio=null&floorNum=1&category=flat&activity=sell',
            'https://ikfeniks.ru/#/macrocatalog/houses/1341385/bigGrid?studio=null&floorNum=1&category=flat&activity=sell',
            'https://ikfeniks.ru/#/macrocatalog/houses/1332616/bigGrid?studio=null&floorNum=1&category=flat&activity=sell',
            'https://ikfeniks.ru/#/macrocatalog/houses/1328253/bigGrid?studio=null&floorNum=1&category=flat&activity=sell',
            'https://ikfeniks.ru/#/macrocatalog/houses/1331364/bigGrid?studio=null&floorNum=1&category=flat&activity=sell',
            'https://ikfeniks.ru/#/macrocatalog/houses/1337465/bigGrid?studio=null&floorNum=1&category=flat&activity=sell',
            'https://ikfeniks.ru/#/macrocatalog/houses/1328716/bigGrid?studio=null&floorNum=1&category=flat&activity=sell',
            'https://ikfeniks.ru/#/macrocatalog/houses/1334507/bigGrid?studio=null&floorNum=1&category=flat&activity=sell',
            'https://ikfeniks.ru/#/macrocatalog/houses/1332940/bigGrid?studio=null&floorNum=1&category=flat&activity=sell',
            'https://ikfeniks.ru/#/macrocatalog/houses/1335646/bigGrid?studio=null&floorNum=1&category=flat&activity=sell',
            'https://ikfeniks.ru/#/macrocatalog/houses/1330976/bigGrid?studio=null&floorNum=1&category=flat&activity=sell',
            'https://ikfeniks.ru/#/macrocatalog/houses/1329578/bigGrid?studio=null&floorNum=5&category=flat&activity=sell'
        ]

        self.driver = None

    @staticmethod
    def get_2_area(sp: BeautifulSoup):
        res_mass = ['-', '-']
        try:
            txt = sp.select_one('div.object-view-content__desc-area-items').text
            pattern = r"\d+[\.,]?\d*"
            numbers = re.findall(pattern, txt)

            return [float(num.replace(",", ".")) for num in numbers]
        except:
            return res_mass

    @staticmethod
    def get_pretty_str(string):
        return int(
            string.replace('\n', '').strip().replace('/', '').replace('\xa0', '').replace('\u2068', '').replace('₽',
                                                                                                                '').replace(
                'м²', '').replace('\u2069', ''))

    @staticmethod
    def get_gk_rayon_floor(sp: BeautifulSoup):
        dct = {
            'gk': '-',
            'rayon': '-',
            'floor': '-'
        }
        for item in sp.select('div.object-view-content__desc-address'):
            if 'ЖК' in item.text:
                dct['gk'] = item.text
            elif 'Россия' in item.text:
                dct['rayon'] = item.text.split('г. Иваново, ')[-1]
            elif 'этаж' in item.text:
                dct['floor'] = int(item.text[-2])
        return dct

    def pars_mini_links(self, url: str) -> None:
        try:
            cnt_entrance, cnt_item, cnt_row = 0, 0, 0

            logger.info(f'Fenix; Start pars URL {self.__all_links.index(url) + 1} out of {len(self.__all_links)}')

            self.driver.get(url)
            self.driver.sleep(5)
            for item in self.driver.select_all('div.chess-entrance'):
                cnt_entrance += 1
                cnt_item, cnt_row = 0, 0
                for row in item.select_all("div.chess-items-container"):
                    cnt_row += 1
                    cnt_item = 0
                    for card in row.select_all('div.chess-item.unselectable'):
                        cnt_item += 1
                        self.driver.wait_for_element('div.item-box-price')
                        if card.select('div.item-box-price').text.lower() not in ['продано', 'бронь']:
                            try:
                                self.driver.run_js(
                                    f"document.querySelector('div.chess-entrance:nth-child({cnt_entrance}) > div > div.chess-floor:nth-child({cnt_row}) > div > div.chess-item.unselectable:nth-child({cnt_item}) > div > div').click();")
                                self.driver.wait_for_element('div.object-modal__close-button')
                                self.driver.wait_for_element('span.object-view-content__desc-name')
                                soup = BeautifulSoup(self.driver.page_html, 'lxml')

                                s1, s2 = self.get_2_area(soup)
                                _dct = self.get_gk_rayon_floor(soup)
                                __type = soup.select_one("span.object-view-content__desc-name").text.replace("\u2068",
                                                                                                             "").replace(
                                    "\u2069", "").lower()

                                new_gk = _dct['gk'] if 'Россия, Ивановская область,  г. Иваново, ул' not in _dct[
                                    'gk'] else _dct['gk'].split('(')[-1].replace(')', '')
                                new_gk = new_gk.replace('очередь', 'оч.').replace('«', '"').replace('»', '"')
                                if ',' not in new_gk:
                                    for num in range(10):
                                        if str(num) in new_gk:
                                            new_gk = new_gk.replace(f' {num}', f', {num}')

                                self.result_mass.append(
                                    {
                                        "Тип": f'{__type[0]}К' if __type[0] in ['1', '2', '3', '4'] else 'СТ',
                                        "S общ": float(
                                            soup.select_one('span.object-view-content__desc-area').text.replace(',',
                                                                                                                '.').split()[
                                                0]),
                                        "S жил": s1,
                                        "S кухни": s2,
                                        "Отд.": 'Черн',
                                        "С/у": '-',
                                        "Балкон": "-",
                                        "Этаж": _dct['floor'],
                                        "№ объекта": int(__type.split('№')[-1]),
                                        "ЖК, оч. и корп.": new_gk,
                                        "Продавец": 'Феникс',
                                        "Район": _dct['rayon'],
                                        "Сдача": '-',
                                        "Цена 100%": self.get_pretty_str(
                                            soup.select_one('div.object-view-content__desc-price-info-price').text),
                                        "за м2": self.get_pretty_str(
                                            soup.select_one('div.object-view-content__desc-price-info-price-m2').text),
                                        "Баз. цена": '-',
                                        "Вознаграж.": '',
                                    }
                                )
                                logger.info(
                                    f'Fenix; Succes pars item (Section-{cnt_entrance}, Row-{cnt_row}, Item-{cnt_item})')
                                self.driver.wait_for_element('div.object-modal__close-button')
                                self.driver.click('div.object-modal__close-button')
                            except Exception as ex:
                                asyncio.run(self.update_err(error="FenixParser: " + str(ex)))
                                logger.warning(f'Fenix/Card; !Flag! Invalid pars URL (URL - {url})')
        except Exception as ex:
            asyncio.run(self.update_err(error="FenixParser: " + str(ex)))
            logger.warning(f'Fenix; Invalid pars URL (URL - {url})')

    def pars_all_data(self) -> None:
        try:
            for link in self.__all_links:
                self.pars_mini_links(link)
        except Exception as ex:
            self._fatal_error = True
            asyncio.run(self.update_err(error="FenixParser // Fatal ERROR  -  " + str(ex)))
            logger.error(f'Fatal ERROR Fenix ->\n{ex}\n\n')

        self.floor_count = len(self.result_mass)


# if __name__ == '__main__':
#     per = FenixParser(
#         exel=True,
#         headless=False
#     )
#     per.run()