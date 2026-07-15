import asyncio
import re
from pprint import pprint

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
            'https://ikfeniks.ru/#/macrocatalog/houses/1337465/bigGrid?studio=null&category=flat&activity=sell',
            'https://ikfeniks.ru/#/macrocatalog/houses/1341385/bigGrid?studio=null&category=flat&activity=sell',
            'https://ikfeniks.ru/#/macrocatalog/houses/1344332/bigGrid?studio=null&category=flat&activity=sell',
            'https://ikfeniks.ru/#/macrocatalog/houses/1338848/bigGrid?studio=null&category=flat&activity=sell',
            'https://ikfeniks.ru/#/macrocatalog/houses/1340768/bigGrid?studio=null&category=flat&activity=sell',
            'https://ikfeniks.ru/#/macrocatalog/houses/1341384/bigGrid?studio=null&category=flat&activity=sell',
            'https://ikfeniks.ru/#/macrocatalog/houses/1332616/bigGrid?studio=null&category=flat&activity=sell',
            'https://ikfeniks.ru/#/macrocatalog/houses/1330976/bigGrid?studio=null&category=flat&activity=sell',
            'https://ikfeniks.ru/#/macrocatalog/houses/1328253/bigGrid?studio=null&category=flat&activity=sell',
            'https://ikfeniks.ru/#/macrocatalog/houses/1335646/bigGrid?studio=null&category=flat&activity=sell',
            'https://ikfeniks.ru/#/macrocatalog/houses/1332940/bigGrid?studio=null&category=flat&activity=sell',
            'https://ikfeniks.ru/#/macrocatalog/houses/1334507/bigGrid?studio=null&category=flat&activity=sell',
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
        try:
            dct['gk'] = sp.select_one('div.font-middle-400.gray-text-900').text
        except:
            ...
        try:
            dct['rayon'] = sp.select('div.font-middle-400.gray-text-900')[-1].text.split('(')[0].strip()
        except:
            ...
        try:
            dct['floor'] = int(sp.select_one('div.headline-3.gray-text-900').text.split('/')[0].strip())
        except:
            ...

        return dct

    @staticmethod
    def parse_areas(text: str) -> list[float | str]:
        nums = [
            float(n.replace(',', '.'))
            for n in re.findall(r'(\d+(?:,\d+)?)\s*м²', text)
        ]

        result = ['-', '-', '-']

        for i, num in enumerate(nums[:3]):
            result[i] = num

        return result

    def pars_mini_links(self, url: str) -> None:
        try:

            logger.info(
                f'Fenix; Start pars URL '
                f'{self.__all_links.index(url) + 1} '
                f'out of {len(self.__all_links)}'
            )

            self.driver.get(url)

            self.driver.wait_for_element(
                'a[title="Квартиры"]',
                wait=15
            )

            self.driver.sleep(2)

            entrances = self.driver.select_all('div.chess-entrance')

            for entrance_index in range(len(entrances)):

                entrance_selector = (
                    f'div.chess-entrance:nth-child({entrance_index + 1})'
                )

                rows = self.driver.select_all(
                    f'{entrance_selector} div.chess-floor'
                )

                for row_index in range(len(rows)):

                    row_selector = (
                        f'{entrance_selector} '
                        f'div.chess-floor:nth-child({row_index + 1})'
                    )

                    cards = self.driver.select_all(
                        f'{row_selector} div.chess-item.unselectable'
                    )

                    for card_index in range(len(cards)):

                        try:

                            current_card_selector = (
                                f'{row_selector} '
                                f'div.chess-item.unselectable:nth-child({card_index + 1})'
                            )

                            self.driver.wait_for_element(
                                current_card_selector,
                                wait=10
                            )

                            card = self.driver.select(current_card_selector)

                            if not card:
                                continue

                            price_el = card.select('div.item-box-price')

                            if not price_el:
                                continue

                            price = (
                                price_el.text
                                .strip()
                                .lower()
                            )

                            if price in ['продано', 'бронь']:
                                continue

                            click_selector = (
                                f'{current_card_selector} > div > div'
                            )

                            self.driver.run_js(
                                f"""
                                document.querySelector('{click_selector}')
                                .scrollIntoView({{
                                    behavior: 'instant',
                                    block: 'center'
                                }});
                                """
                            )

                            self.driver.sleep(0.5)

                            # клик
                            self.driver.run_js(
                                f"""
                                document.querySelector('{click_selector}')
                                .click();
                                """
                            )

                            # ждём открытия модалки
                            self.driver.wait_for_element(
                                'div.object__close-button',
                                wait=15
                            )

                            # ждём появления заголовка квартиры
                            self.driver.wait_for_element(
                                'div.headline-0.gray-text-700',
                                wait=15
                            )

                            self.driver.sleep(1)

                            soup = BeautifulSoup(
                                self.driver.page_html,
                                'lxml'
                            )

                            title_el = soup.select_one(
                                'div.headline-0.gray-text-700'
                            )

                            if not title_el:
                                raise Exception(
                                    'Не найден заголовок карточки'
                                )

                            __type = (
                                title_el.text
                                .replace('\u2068', '')
                                .replace('\u2069', '')
                                .replace('\n', ' ')
                                .strip()
                                .lower()
                            )

                            # защита от мусорной модалки
                            if '№' not in __type:
                                raise Exception(
                                    f'Открылась некорректная карточка: {__type}'
                                )

                            try:
                                object_id = int(
                                    __type.split('№')[-1]
                                    .strip()
                                )
                            except:
                                raise Exception(
                                    f'Не удалось получить '
                                    f'№ объекта из: {__type}'
                                )

                            _dct = self.get_gk_rayon_floor(soup)

                            new_gk = (
                                _dct['gk']
                                .replace('очередь', 'оч.')
                                .replace('«', '"')
                                .replace('»', '"')
                            )

                            sq, sq_g, sq_k = self.parse_areas(soup.select_one('div.tile.tile-default.p-v-20.p-h-24.b-r-12.max-w-360.relative.f-grow-xs.f-grow-sm.max-w-none-xs.max-w-none-sm.min-w-180').text)
                            print(sq, sq_g, sq_k)

                            price_all = soup.select_one('div.object-view-content__desc-price.tile.p-v-20.p-h-24.b-r-12.row-gap-12.max-w-360.relative.f-grow-xs.f-grow-sm.max-w-none-xs.max-w-none-sm.tile-default.min-w-240').select_one(
                                'div.headline-0.gray-text-700'
                            ).text

                            if not price_all:
                                raise Exception(
                                    'Не найдена цена'
                                )

                            price_m2 = soup.select_one(
                                'div.font-middle-400.gray-text-500'
                            )

                            if not price_m2:
                                raise Exception(
                                    'Не найдена цена за м2'
                                )

                            res_dct = {

                                "Тип": (
                                    f'{__type[0]}К'
                                    if __type[0] in ['1', '2', '3', '4']
                                    else 'СТ'
                                ),

                                "S общ": sq,

                                "S жил": sq_g,

                                "S кухни": sq_k,

                                "Отд.": 'Черн',
                                "С/у": '-',
                                "Балкон": "-",
                                "Этаж": _dct['floor'],
                                "№ объекта": object_id,
                                "ЖК, оч. и корп.": new_gk,
                                "Продавец": 'Феникс',
                                "Район": _dct['rayon'],
                                "Сдача": '-',

                                "Цена 100%": self.get_pretty_str(
                                    price_all
                                ),

                                "за м2": self.get_pretty_str(
                                    price_m2.text
                                ),

                                "Баз. цена": '-',
                                "Вознаграж.": '',
                            }

                            self.result_mass.append(res_dct)

                            logger.info(
                                f'Fenix; Success pars item '
                                f'(Section-{entrance_index + 1}, '
                                f'Row-{row_index + 1}, '
                                f'Item-{card_index + 1})'
                            )

                            # закрываем модалку
                            self.driver.click(
                                'div.object__close-button'
                            )

                            self.driver.sleep(1.5)

                            # ждём возврата шахматки
                            self.driver.wait_for_element(
                                'a[title="Квартиры"]',
                                wait=15
                            )

                        except Exception as ex:

                            logger.warning(
                                f'Fenix/Card; Invalid pars item '
                                f'(Section-{entrance_index + 1}, '
                                f'Row-{row_index + 1}, '
                                f'Item-{card_index + 1}) '
                                f'ERROR: {ex}'
                            )

                            try:
                                self.driver.click(
                                    'div.object__close-button'
                                )
                                self.driver.sleep(1)
                            except:
                                pass

                            continue

        except Exception as ex:

            asyncio.run(
                self.update_err(
                    error="FenixParser: " + str(ex)
                )
            )

            logger.warning(
                f'Fenix; Invalid pars URL '
                f'(URL - {url}) '
                f'ERROR: {ex}'
            )

    def pars_all_data(self) -> None:
        try:
            for link in self.__all_links:
                self.pars_mini_links(link)
        except Exception as ex:
            self._fatal_error = True
            # asyncio.run(self.update_err(error="FenixParser // Fatal ERROR  -  " + str(ex)))
            logger.error(f'Fatal ERROR Fenix ->\n{ex}\n\n')

        self.floor_count = len(self.result_mass)


if __name__ == '__main__':
    per = FenixParser(
        exel=True,
        headless=False
    )
    per.run()