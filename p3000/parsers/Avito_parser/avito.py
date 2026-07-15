import re
from datetime import datetime
from pprint import pprint

from loguru import logger
from bs4 import BeautifulSoup
import lxml

from enum import Enum

from random import randint

from p3000.parsers.base import BaseParserSelenium
from cache_core import CacheCore


class StatusDelay(Enum):
    DEFAULT_PAGE = 'default_page'
    PAGE = 'page'
    DEFAULT_CARD = 'default_card'
    CARD = 'card'


class AvitoParser(BaseParserSelenium):
    def __init__(self, site_name: str, err_name = None, headless: bool = True, retry_count: int = 3, exel: bool = False, single: bool = False, _date: str = ''):
        super().__init__(
            start_url='https://www.avito.ru',
            site_name=site_name,
            headless=headless,
            retry_count=retry_count,
            exel=exel,
            err_name=err_name if err_name else ["single", 'VT'],
            single=single
        )
        self.cnt: int = 0
        self.driver = None

        self._date = _date

        self.delay: int = 2

        self.pars_links: dict = {
            'Vladimir': 'https://www.avito.ru/vladimir/kvartiry/prodam/novostroyka/na-stadii-sdachi-ASgBAgECAkSSA8YQ5geOUgFFuMENFHsiZnJvbSI6bnVsbCwidG8iOjF9?f=ASgBAgECBESSA8YQ5geOUpC~DZKuNdKEEsyKiwMBRbjBDRR7ImZyb20iOm51bGwsInRvIjoxfQ&localPriority=0&p=1',
            'Ivanovo': 'https://www.avito.ru/ivanovo/kvartiry/prodam/ot-zastrojshika/novostroyka-ASgBAgICA0SSA8YQ5geOUpC~DZKuNQ?f=ASgBAgECBESSA8YQ5geOUpC~DZKuNdKEEsyKiwMBRbjBDRR7ImZyb20iOm51bGwsInRvIjoxfQ&localPriority=0&p=1',
            'Kovrov': 'https://www.avito.ru/kovrov/kvartiry/prodam/ot-zastrojshika/novostroyka-ASgBAgICA0SSA8YQ5geOUpC~DZKuNQ?f=ASgBAgECBESSA8YQ5geOUpC~DZKuNdKEEsyKiwMBRbjBDRR7ImZyb20iOm51bGwsInRvIjoxfQ&localPriority=0&p=1'
        }

        self.pars_names: list[str] = [
            'Kovrov',
            'Ivanovo',
            'Vladimir',
        ]
        self.rus_name = {
            'Kovrov': 'Ковров',
            'Vladimir': 'Владимир',
            'Ivanovo': 'Иваново',
        }

    @staticmethod
    def get_other_data(sp):
        rooms, full_area, kitchen_area, leave_area, floor, balkon, otd, toilet = '-', '-', '-', '-', '-', '-', '-', '-'
        new_sp = ''
        for good_teg in sp.select('ul'):
            if 'Количество комнат' in good_teg.text:
                new_sp = good_teg
        for item in new_sp.select('li'):
            if 'Количество комнат' in item.text:
                rooms = f"{int(item.text.replace('Количество комнат: ', ''))}К" if 'студия' not in item.text else 'СТ'
            elif 'Общая площадь' in item.text:
                match = re.search(r'([\d.,]+)\s*м²', item.text)
                full_area = float(match.group(1).replace(',', '.'))
            elif 'Площадь кухни' in item.text:
                match = re.search(r'([\d.,]+)\s*м²', item.text)
                kitchen_area = float(match.group(1).replace(',', '.'))
            elif 'Жилая площадь' in item.text:
                match = re.search(r'([\d.,]+)\s*м²', item.text)
                leave_area = float(match.group(1).replace(',', '.'))
            elif 'Этаж' in item.text:
                floor = int(item.text.replace('Этаж: ', '').split(' из ')[0])
            elif 'Балкон или лоджия' in item.text:
                balkon = 'Л' if 'л' == item.text.split(': ')[-1][0] else 'Б'
            elif 'Отделка' in item.text:
                otd = 'Без отделки' if 'без' in item.text else item.text.replace('Отделка: ', '').replace('чистовая', 'Чист').replace('предЧист', 'П/Чист')
            elif 'Санузел' in item.text:
                toilet = 'C' if 'совмещенный' in item.text.lower() else 'Р'

        return [rooms, full_area, kitchen_area, leave_area, floor, balkon, otd, toilet]

    @staticmethod
    def get_other_data_2_0(sp):
        gk, sdacha = '-', '-'
        for item in sp.select_one('ul').select('li'):
            if 'Название новостройки' in item.text:
                gk = item.text.replace('Название новостройки: ', '')
            elif 'Срок сдачи' in item.text:
                sdacha = item.text.replace('Срок сдачи: Сдан ', '').replace('Срок сдачи: Сдача в ', '')
            elif 'Корпус, строение' in item.text:
                gk += item.text.replace('Корпус, строение:', '').lower().replace('дом', 'д').replace('корпус',
                                                                                                     'корп').replace(
                    ',', '')

        return [gk, sdacha]

    def get_delay(self, status: StatusDelay):
        if status.value == 'default_page':
            self.driver.sleep(randint(self.delay * 3, self.delay * 4))
            for _ in range(randint(2, 4)):
                self.driver.scroll()
                self.driver.sleep(randint(1, 2))
            self.driver.sleep(randint(self.delay * 2, self.delay * 4))
            for _ in range(randint(2, 4)):
                self.driver.scroll()
                self.driver.sleep(randint(1, 2))
            self.driver.sleep(randint(self.delay * 3, self.delay * 4))
        elif status.value == 'page':
            self.driver.sleep(randint(self.delay * 10, self.delay * 15))
            for _ in range(randint(2, 5)):
                self.driver.scroll()
                self.driver.sleep(randint(1, 3))
            self.driver.sleep(randint(self.delay * 10, self.delay * 15))
        elif status.value == 'default_card':
            self.driver.sleep(randint(self.delay, self.delay * 2))
            for _ in range(randint(2, 4)):
                self.driver.scroll()
                self.driver.sleep(randint(1, 2))
            self.driver.sleep(randint(self.delay * 2, self.delay * 3))
        elif status.value == 'card':
            self.driver.sleep(randint(self.delay * 10, self.delay * 15))
            for _ in range(randint(2, 5)):
                self.driver.scroll()
                self.driver.sleep(randint(1, 3))
            self.driver.sleep(randint(self.delay * 10, self.delay * 15))
        elif status.value == 'MAX_DELAY':
            self.driver.sleep(randint(self.delay * 30, self.delay * 60))
            for _ in range(randint(5, 10)):
                self.driver.scroll()
                self.driver.sleep(randint(1, 4))
            self.driver.sleep(randint(self.delay * 35, self.delay * 45))

    @staticmethod
    def check_unique_dct(full_data: list[dict], dct: dict):
        for item in full_data:
            if dct['Тип'] == item['Тип'] and dct['Этаж'] == item['Этаж'] and dct['S общ'] == item['S общ'] and \
                    dct['ЖК, оч. и корп.'] == item['ЖК, оч. и корп.'] and \
                    dct['за м2'] == item['за м2'] and dct['Цена 100%'] == item['Цена 100%']:
                return True
        return False

    def auth_avito(self, link: str, try_cnt: int) -> None:
        if try_cnt == 0:
            self.driver.get(self.start_url)
            self.driver.sleep(randint(self.delay*2, self.delay*4))
            self.driver.scroll()

        self.driver.sleep(randint(self.delay, self.delay*2))
        self.driver.get(link)
        for _ in range(randint(5, 10)):
            self.driver.scroll()
            self.driver.sleep(randint(1, 3))
        self.driver.sleep(randint(1, self.delay))

    def pars_data(self, name:str):
        # self.driver.driver.set_page_load_timeout(10)
        try:
            _cache = CacheCore(cache_name=f'{name}')

            _all_pars_card_url = _cache.get()
            _all_pars_card_url.sort()
            cnt = 0

            logger.success(f'Avito ({name}); ALL PARS CARDS LINK == {len(_all_pars_card_url)}')

            for card_link in _all_pars_card_url:
                logger.info(f'Avito ({name}); Start Pars CARD {_all_pars_card_url.index(card_link) + 1} out of {len(_all_pars_card_url)} ({card_link})')
                cnt += 1
                try:
                    if _cache.exists(card_link) is False:
                        continue
                    try:
                        self.driver.get(card_link, wait=5)
                    except:
                        try:
                            self.driver.reload()
                            self.driver.sleep(randint(1, 2))
                        except:
                            self.driver.reload()
                            self.driver.sleep(randint(1, 2))

                    if cnt % 50 == 0:
                        self.get_delay(StatusDelay.CARD)
                    else:
                        self.get_delay(StatusDelay.DEFAULT_CARD)

                    soup = BeautifulSoup(self.driver.page_html, 'lxml')
                    if 'Объявление закрыто.' in str(soup) or 'Объявление истекло.' in str(soup) or 'Объявление не посмотреть' in str(soup) or 'Оно ещё на проверке' in str(soup):
                        logger.warning(f'Avito ({name}); Объявление закрыто URL: {card_link}')
                        _all_pars_card_url.remove(card_link)
                        _cache.update(
                            key='pars_cards_urls',
                            value=list(set(_all_pars_card_url))
                        )
                        continue

                    zastroy = ''
                    rooms, full_area, kitchen_area, leave_area, floor, balkon, otd, toilet = self.get_other_data(
                        soup.select_one('div[data-marker="item-view/item-params"]'))
                    gk, sdacha = self.get_other_data_2_0(soup.select('div[data-marker="item-view/item-params"]')[1])

                    if 'Застройщик' in soup.select_one('div[data-marker="item-view/seller-info"]').text:
                        zastroy = [item for item in
                                   soup.select_one('div[data-marker="item-view/seller-info"]').text.split('Застройщик')
                                   if item][0].strip()

                    if zastroy:
                        ...
                    else:
                        __num = f'{_all_pars_card_url.index(card_link) + 1} out of {len(_all_pars_card_url)}'
                        logger.warning(f'Avito ({name}); Not ---  ZASTROY  {__num} --- {card_link}')
                        continue

                    dct = {
                        'Дата': self._date,
                        'Город': self.rus_name[name],
                        'Тип': rooms,
                        'S общ': full_area,
                        'S жил': leave_area,
                        'S кухни': kitchen_area,
                        'Отд.': otd,
                        'С/у': toilet,
                        'Балкон': balkon,
                        'Этаж': floor,
                        '№ объекта': '-',
                        'ЖК, оч. и корп.': gk,
                        'Продавец': 'Игротек' if zastroy.strip() == 'ЖК Заречье парк' else zastroy,
                        'Район': soup.select_one('div[itemprop="address"]').text,
                        'Сдача': sdacha,
                        'Цена 100%': int(soup.select_one('span[itemprop="price"]').get('content')),
                        'за м2': int(int(soup.select_one('span[itemprop="price"]').get('content')) / full_area),
                        'Баз. цена': '-',
                        'Вознаграж.': ''
                    }

                    if self.check_unique_dct(_cache.get_all_values(), dct):
                        logger.warning(f'Avito ({name}) (check_unique_dct); ПОВТОР ОБЪЯВЛЕНИЯ URL: {card_link}')
                        _all_pars_card_url.remove(card_link)
                        _cache.update(
                            key='pars_cards_urls',
                            value=list(set(_all_pars_card_url))
                        )
                        continue

                    _cache.add(
                        key=card_link,
                        value=dct
                    )
                    pprint(dct)

                    self.driver.sleep(randint(self.delay, self.delay * 2))
                except Exception as ex:
                    soup = BeautifulSoup(self.driver.page_html, 'lxml')
                    with open(f'index_error.html', 'w', encoding='utf-8') as file:
                        file.write(str(soup))

                    logger.warning(f"Avito; Error (pars_data) {card_link};  Exeption -> {ex}\n\n")
                    self.driver.sleep(randint(20, 50))

            self.result_mass = _cache.get_all_values()
            self.floor_count = _cache.size()
        except Exception as ex:
            logger.warning(f'Warning link : {ex}')

    def pars_all_pages(self, name: str, start_url: str):
        _cache = CacheCore(cache_name=f'{name}')
        soup = BeautifulSoup(self.driver.page_html, 'lxml')

        full_pages_num = int(int(soup.select_one('span[data-marker="page-title/count"]').text)/50) + 2

        __cache_urls = _cache.get()

        for num in range(1, full_pages_num):
            _new_link = start_url.replace('&p=1', f'&p={num}')
            logger.info(f'AvitoParser ({name}); Start Pars PAGE Link №{num} out of {full_pages_num - 1} {_new_link}')

            if num != 1:
                try:
                    self.driver.get(_new_link)
                except:
                    try:
                        self.driver.reload()
                    except:
                        self.driver.reload()

                self.get_delay(StatusDelay.DEFAULT_PAGE)

            if num == full_pages_num - 1:
                self.get_delay(StatusDelay.PAGE)

            __soup = BeautifulSoup(self.driver.page_html, 'lxml')
            _all_pars_card_url = []

            for _item in __soup.select('a[data-marker="item-photo-sliderLink"]'):
                link = _item.get('href')
                if f'https://www.avito.ru{link}'.split('?')[0] in [item.split('?')[0] for item in __cache_urls]:
                    logger.warning(f'Avito ({name}); Link already exist https://www.avito.ru{link}')
                    continue
                _all_pars_card_url.append(f'https://www.avito.ru{link}')
                logger.info(f'Avito ({name}); NEW LINK https://www.avito.ru{link}')

            if _all_pars_card_url:
                __cache_urls.extend(_all_pars_card_url)
                _cache.update(
                    key='pars_cards_urls',
                    value=list(set(__cache_urls))
                )
                print(len(_cache.get()))

            logger.info(f'Avito ({name}); Page {num}, card {len(_all_pars_card_url)}')
        logger.success(f'Avito ({name}); ALL PARS CARDS LINK == {len(_cache.get())}')


    def pars_all_data(self) -> None:
        try_cnt = 0
        for _name in self.pars_names:
            self.site_name = _name

            logger.info(f'AvitoParser ({_name}); Started authorize')
            self.auth_avito(link=self.pars_links[_name], try_cnt=try_cnt)
            try_cnt += 1
            logger.success(f'AvitoParser ({_name}); SUCCESS authorize')

            logger.info(f'AvitoParser ({_name}); Start Pars PAGES')
            self.pars_all_pages(name=_name, start_url=self.pars_links[_name])
            logger.success(f'AvitoParser ({_name}); SUCCESS Pars PAGES')

            logger.info(f'AvitoParser ({_name}); Start Pars ALL_DATA')
            self.pars_data(name=_name)
            logger.success(f'AvitoParser ({_name}); SUCCESS Pars ALL_DATA')

            # _cache = CacheCore(cache_name=f'{_name}')
            # self.result_mass = _cache.get_all_values()
            # self.floor_count = _cache.size()
            #
            # _exel_name = f"all_exel/exel_2026-17-10/{datetime.now().date()}_{self.site_name}.xlsx"     # МЕНЯТЬ ДАТУ ПАПКИ
            # self.to_exel(mass=self.result_mass, exel_name=_exel_name)
            # logger.info(f'AvitoitoParser; Avito flats {_name} count == {self.floor_count}')

        logger.info(f'AvitoParser; Avito flats count == {self.floor_count}')
        self.driver.sleep(randint(5, 10))
        self.driver.close()


if __name__ == '__main__':
    per = AvitoParser(
        site_name='avito',
        exel=False,
        headless=False,

        _date='17.07.2026'  # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    )
    per.run()