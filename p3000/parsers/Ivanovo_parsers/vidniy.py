import asyncio

from loguru import logger
from bs4 import BeautifulSoup
import lxml

from p3000.parsers.base import BaseParserRequests

from requests import get


class VidniyParser(BaseParserRequests):
    def __init__(self, err_name = None, exel: bool = False, single: bool = False):
        super().__init__(
            all_links=[
                'https://видный37.рф/liter-8.html',
                'https://видный37.рф/liter-9.html',
                'https://видный37.рф/liter-i.html',
                'https://видный37.рф/liter-k.html',
                'https://видный37.рф/liter-s.html',
                'https://видный37.рф/liter-l.html',
                'https://видный37.рф/liter-m.html'
            ],
            site_name='vidniy',
            exel=exel,
            err_name=err_name if err_name else ["single", 'Vidniy'],
            single=single
        )

        self.__pars_links: list[str] = []

    def pars_flat(self, link: str) -> dict:
        try:
            response = get(link)

            soup = BeautifulSoup(response.text, 'lxml')
            data = [item.text.strip() for item in soup.select_one('ul.appartment-page__info').select('li') if item]
            full_area, rooms, otd, sdacha, = '-', '-', '-', '-'
            for idx in range(len(data)):
                if 'Общая площадь' in data[idx]:
                    full_area = float(data[idx].split(': ')[-1])
                elif 'Количество комнат' in data[idx]:
                    rooms = int(data[idx].split(': ')[-1])
                elif 'Тип отделки' in data[idx]:
                    per = data[idx].split(': ')[-1]
                    otd = per if per != 'нет' else 'Без отделки'
                elif 'Срок сдачи' in data[idx]:
                    sdacha = data[idx].split(': ')[-1] if len(data[idx].split(': ')[-1]) > 1 else '-'

            full_price = int(soup.select_one('div.appartment-page__price').text.replace(' ', ''))
            price_m = 0
            try:
                price_m = int(full_price / full_area)
            except:
                price_m = float(full_price / full_area)

            return {
                "Тип": f'{rooms}К' if rooms != '-' else 'СТ',
                "S общ": full_area,
                "S жил": '-',
                "S кухни": '-',
                "Отд.": otd,
                "С/у": '-',
                "Балкон": "-",
                "Этаж": int(soup.select_one('div.appartment-banner__info.mb-3').text.split()[0]),
                "№ объекта": '-',
                "ЖК, оч. и корп.": 'ЖК Микрорайон "Видный"',
                "Продавец": 'СЗ ЖСК',
                "Район": "г. Иваново, мкр. Видный д. 4",
                "Сдача": '-',
                "Цена 100%": full_price,
                "за м2": price_m,
                "Баз. цена": '-',
                "Вознаграж.": '',
            }
        except Exception as ex:
            asyncio.run(self.update_err(error="Vidniy: " + str(ex)))
            logger.warning(f'''Vidniy; Invalid link: {link}\nExeption: {ex}\n''')

    def pars_all_data(self) -> None:
        try:
            for link in self.all_links:
                logger.info(f'Vidniy; Pars  -PAGE-  ({link}); {self.all_links.index(link) + 1} out of {len(self.all_links)}')
                response = get(link)
                soup = BeautifulSoup(response.text, 'lxml')

                for item in soup.select('div.appartments-table__row.row.row--nowrap.row--gutter_0'):
                    for lnk in item.select('a'):
                        if 'Продано' in lnk.text:
                            continue
                        logger.info(
                            f'Vidniy; Pars link  (https://видный37.рф/{lnk.get("href")})')
                        dct = self.pars_flat(f'https://видный37.рф/{lnk.get("href")}')
                        if dct:
                            self.result_mass.append(dct)
        except Exception as ex:
            self._fatal_error = True
            asyncio.run(self.update_err(error="Vidniy // Fatal ERROR  -  " + str(ex)))
            logger.error(f'Fatal ERROR Vidniy ->\n{ex}\n\n')

        self.floor_count = len(self.result_mass)


# if __name__ == '__main__':
#     per = VidniyParser(
#         exel=True
#     )
#     per.run()