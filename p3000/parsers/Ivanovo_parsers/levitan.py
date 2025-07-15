import asyncio

from loguru import logger
from bs4 import BeautifulSoup
import lxml

from p3000.parsers.base import BaseParserSelenium

from requests import get


class LevitanParser(BaseParserSelenium):
    def __init__(self, err_name = None, headless: bool = True, retry_count: int = 3, exel: bool = False):
        super().__init__(
            start_url='https://жк-левитан.рф/apartments/',
            site_name='levitan',
            headless=headless,
            retry_count=retry_count,
            exel=exel,
            err_name=err_name if err_name else ["single", 'Levitan']
        )

        self.driver = None

    def pars_flat(self, link: str) -> None:
        try:
            response = get(link)

            soup = BeautifulSoup(response.text, 'lxml')
            data = [item.strip() for item in soup.select('div.flex-wrap.justify-content-space-between')[0].text.split('\n')
                    if item]
            full_price, full_area, rooms, tualet, otd, sdacha, leave_area, floor, = '-', '-', '-', '-', '-', '-', '-', '-'
            for idx in range(len(data)):
                if 'На этаже' == data[idx]:
                    full_price = int(data[idx + 1].replace(' ', '')[:-1])
                elif 'Площадь' == data[idx]:
                    full_area = float(data[idx + 1].replace(' кв.м', ''))
                elif 'Количество комнат' == data[idx]:
                    rooms = int(data[idx + 1])
                elif 'Сан. узел' == data[idx]:
                    tualet = data[idx + 1][0]
                elif 'Отделка' == data[idx]:
                    otd = data[idx + 1][:4]
                elif 'Сдача квартиры' == data[idx]:
                    sdacha = data[idx + 1]
                elif 'Жилая площадь' == data[idx]:
                    leave_area = float(data[idx + 1].replace(' кв.м', ''))
                elif 'Этаж' == data[idx]:
                    floor = int(data[idx + 1].split()[0])
            price_m = 0
            try:
                price_m = int(full_price / full_area)
            except:
                price_m = float(full_price / full_area)
            self.result_mass.append(
                {
                    "Тип": f'{rooms}К',
                    "S общ": full_area,
                    "S жил": leave_area,
                    "S кухни": '-',
                    "Отд.": otd,
                    "С/у": tualet,
                    "Балкон": "-",
                    "Этаж": floor,
                    "№ объекта": soup.select_one('h1').text.split('№')[-1],
                    "ЖК, оч. и корп.": 'ЖК Левитан',
                    "Продавец": 'Аквилон',
                    "Район": "Иваново, Проспект Ленина д. 55",
                    "Сдача": sdacha,
                    "Цена 100%": full_price,
                    "за м2": price_m,
                    "Баз. цена": '-',
                    "Вознаграж.": '',
                }
            )
        except Exception as ex:
            asyncio.run(self.update_err(error="LevitanParser: " + str(ex)))
            logger.warning(f'Levitan; Invalid link: {link}')

    def pars_all_data(self) -> None:
        try:
            self.driver.get(self.start_url)
            self.driver.sleep(1)
            try:
                for _ in range(7):
                    self.driver.click('div.ajax-filter-count.ajax-more.button-ajax-more')
                    self.driver.sleep(1)
            except:
                logger.warning('Levitan; Scroll err')
            soup = BeautifulSoup(self.driver.page_html, 'lxml')
            for card in soup.select_one('div.wrapper-apartments.ajax-container.flex-wrap').select('a'):
                link = card.get('href')
                if 'Продана' not in card.select_one('div.tags.flex').text:
                    logger.info(f'Levitan; <-- START Pars Link ({link})')
                    self.pars_flat(link)
                    logger.info(f'Levitan; SUCCESS --> Pars Link ({link})')
        except Exception as ex:
            self._fatal_error = True
            asyncio.run(self.update_err(error="LevitanParser // Fatal ERROR  -  " + str(ex)))
            logger.error(f'Fatal ERROR Levitan ->\n{ex}\n\n')

        self.floor_count = len(self.result_mass)


# if __name__ == '__main__':
#     per = LevitanParser(
#         exel=True
#     )
#     per.run()