import asyncio

from loguru import logger
from bs4 import BeautifulSoup
import lxml

from p3000.parsers.base import BaseParserSelenium

from requests import get


class KSKHoldingParser(BaseParserSelenium):
    def __init__(self, err_name = None, headless: bool = True, retry_count: int = 3, exel: bool = False, single: bool = False):
        super().__init__(
            start_url='https://www.ivksk.ru/nedv/',
            site_name='ksk_holding',
            headless=headless,
            retry_count=retry_count,
            exel=exel,
            err_name=err_name if err_name else ["single", 'KSKHolding'],
            single=single
        )

        self.__all_links: list[str] = []

        self.driver = None

    @staticmethod
    def get_flat_type_and_num(text: str) -> str:
        if '4' in text:
            return '4К'
        elif '3' in text:
            return '3К'
        elif '2' in text:
            return '2К'
        elif '1' in text:
            return '1К'
        else:
            return 'СТ'

    @staticmethod
    def get_fl_corp_sd_otd(sp: BeautifulSoup):
        dct = {
            'floor': '-',
            'sdacha': '-',
            'otdelka': '-'
        }
        for item in sp.select_one('table.table.table-borderless').select('tr'):
            if item.select_one('td').text.lower() == 'этаж':
                dct['floor'] = int(item.select('td')[-1].text)
            elif item.select_one('td').text.lower() == 'сдача':
                dct['sdacha'] = item.select('td')[-1].text.replace(' год', '')
            elif item.select_one('td').text.lower() == 'отделка':
                dct['otdelka'] = item.select('td')[-1].text
        return dct

    def get_room_area(self, sp: BeautifulSoup):
        txt = sp.select('h4.text-bold')[1].text.split(', ')

        room = self.get_flat_type_and_num(txt[0])
        area = float(txt[-1].split(' м')[0])

        return [room, area]

    def get_all_house_links(self) -> None:
        try:
            response = get(
                self.start_url
            )
            soup = BeautifulSoup(response.text, 'lxml')

            for house in soup.select_one('div.doma-grid').select('div.col-md-6'):
                self.__all_links.append(house.select_one('a').get('href'))
            logger.success(f'KSKHolding; Success Pars All_Links (count == {len(self.__all_links)})')
        except Exception as ex:
            asyncio.run(self.update_err(error="KSKHoldingParser: " + str(ex)))
            logger.warning(f'KSKHolding; Invalid pars All_Links')

    def pars_flat(self, link: str) -> dict:
        try:
            response = get(
                link
            )
            soup = BeautifulSoup(response.text, 'lxml')
            _dct = self.get_fl_corp_sd_otd(sp=soup)
            room, area = self.get_room_area(sp=soup)

            gk = soup.select('h5')[1].text.replace('ё', 'е')
            if 'Терешкова' in gk or 'Комаров' in gk:
                gk = 'ЖК "Звездный" Литер "Терешкова - Комаров"'
            elif '"Альфа Центавра"' in gk:
                gk = 'ЖК "Альфа Центавра"'

            _room = room.replace('K', 'К')

            if 'Дельта Центавра' in gk:
                if 88.8 <= float(area) <= 119.15:
                    _room = '2К'
                elif 119.15 < float(area):
                    _room = '3К'

            return {
                "Тип": _room,
                "S общ": area,
                "S жил": '-',
                "S кухни": '-',
                "Отд.": _dct['otdelka'],
                "С/у": '-',
                "Балкон": "-",
                "Этаж": _dct['floor'],
                "№ объекта": '-',
                "ЖК, оч. и корп.": gk,
                "Продавец": 'КСК Холдинг',
                "Район": soup.select('div.mt-3')[1].text.split('Иваново, ')[-1],
                "Сдача": int(_dct['sdacha']) if len(_dct['sdacha']) == 4 else _dct['sdacha'].replace(' г.', '').replace(
                    'квартал', 'кв.'),
                "Цена 100%": int(soup.select_one('div.fs-3.lh-1').text.replace(' ', '').replace('₽', '')),
                "за м2": int(soup.select_one('div.text-muted.mt-2').text.split(' ₽')[0].replace(' ', '')),
                "Баз. цена": '-',
                "Вознаграж.": '',
            }
        except Exception as ex:
            asyncio.run(self.update_err(error="KSKHoldingParser: " + str(ex)))
            logger.warning(f'KSKHolding; Invalid pars flat (url - {link})')

    def pars_house(self, url: str) -> None:
        try:
            logger.info(f'KSKHolding; Start pars house - {url}')
            data: list[dict] = []

            self.driver.get(url)
            for _ in range(15):
                try:
                    self.driver.click('div.text-center.mt-4rem > div.btn.ksk-grey-btn.dom-more-btn')
                except:
                    ...
            soup = BeautifulSoup(self.driver.page_html, 'lxml')

            items = soup.select_one('div.row').select('div.kv-item')
            for item in items:
                logger.info(f'KSKHolding; Pars item №{items.index(item)} out of {len(items)}')
                data.append(self.pars_flat(item.select_one('div.kv-layout').get('onclick').split("href = '")[-1][:-1]))

            self.result_mass.extend(data)
        except Exception as ex:
            asyncio.run(self.update_err(error="KSKHoldingParser: " + str(ex)))
            logger.warning(f'KSKHolding; Invalid pars house (link - {url})')

    def pars_all_data(self) -> None:
        try:
            self.get_all_house_links()

            for link in self.__all_links:
                logger.info(f'KSKHolding; Pars link №{self.__all_links.index(link) + 1} out of {len(self.__all_links)}')
                self.pars_house(link)
        except Exception as ex:
            self._fatal_error = True
            asyncio.run(self.update_err(error="KSKHoldingParser // Fatal ERROR  -  " + str(ex)))
            logger.error(f'Fatal ERROR KSKHolding ->\n{ex}\n\n')

        self.floor_count = len(self.result_mass)


# if __name__ == '__main__':
#     per = KSKHoldingParser(
#         exel=True
#     )
#     per.run()