import asyncio

from loguru import logger
from bs4 import BeautifulSoup
import lxml

from p3000.parsers.base import BaseParserSelenium, FlagKey


class LegendaParser(BaseParserSelenium):
    def __init__(self, err_name = None, headless: bool = True, retry_count: int = 3, exel: bool = False):
        super().__init__(
            start_url=[
                'https://legendakovrova.ru/',
                'https://legendakovrova.ru/?tfc_sort[790548645]=title:asc&tfc_quantity[790548645]=y&tfc_page[790548645]=2&tfc_div=:::'
            ],
            site_name='legenda',
            headless=headless,
            retry_count=retry_count,
            exel=exel,
            err_name=err_name if err_name else ["single", 'Olimp']
        )

        self.driver = None

        self.__pars_links: [str] = []

    @staticmethod
    def get_formatted_price(s: str) -> int:
        return int(s.replace(' р.', '').replace(' ', ''))

    @staticmethod
    def get_valid_floor(s: str) -> list[str]:
        s = s.split('/')
        return s

    @staticmethod
    def get_valid_type(s: str) -> str:
        text = s.split('комн.')
        if '4' in text[0]:
            return '4К'
        elif '3' in text[0]:
            return '3К'
        elif '2' in text[0]:
            return '2К'
        elif '1' in text[0]:
            return '1К'
        else:
            return 'Пентхаус'

    def pars_all_data(self) -> None:
        try:
            for item in self.start_url:
                try:
                    self.driver.get(item)
                    self.driver.sleep(1)
                    self.driver.scroll()
                    self.driver.scroll()
                    self.driver.sleep(1)
                    soup = BeautifulSoup(self.driver.page_html, 'lxml')
                    flats = soup.select_one(
                        'div.t951__grid-cont.js-store-grid-cont.t-store__grid-cont_col-width_stretch.t-container.t-store__grid-cont_mobile-grid.t951__container_mobile-grid'
                    ).select('a')
                    for h in flats:
                        self.__pars_links.append(h.get('href'))
                except Exception as ex:
                    asyncio.run(self.update_err(error="LegendaParser " + str(ex)))
                    logger.warning(f'Invalid URL_1 Legenda ({item}) ->\n{ex}\n')

            logger.info('Success pars all pars_links for Legenda')

            for item in self.__pars_links:
                try:
                    logger.info(f'Legenda; Link {self.__pars_links.index(item) + 1} out of {len(self.__pars_links)}')
                    self.driver.get(item)
                    self.driver.sleep(1)
                    soup = BeautifulSoup(self.driver.page_html, 'lxml')
                    payload = soup.select('div.tn-atom')

                    try:
                        price = self.get_formatted_price(payload[7].text)
                        val_type = self.get_valid_type(payload[6].text)
                        s_full = float(payload[5].text.split('м')[0])
                        otd = payload[14].text[:4]
                        sdacha = payload[18].text.replace(' года', '').replace('кв', 'кв.')
                        cnt = 0
                    except ValueError:
                        cnt = 4
                        price = self.get_formatted_price(payload[11].text)
                        val_type = self.get_valid_type(payload[10].text)
                        s_full = float(payload[9].text.split('м')[0])
                        otd = payload[18].text[:4]
                        sdacha = payload[22].text.replace(' года', '').replace('кв', 'кв.')

                    for floor in self.get_valid_floor(payload[8 + cnt].text):
                        self.result_mass.append(
                            {
                                "Тип": val_type,
                                "S общ": s_full,
                                "S жил": "-",
                                "S кухни": "-",
                                "Отд.": otd,
                                "С/у": "-",
                                "Балкон": "-",
                                "Этаж": int(floor.split('-')[0]),
                                "№ объекта": "-",
                                "ЖК, оч. и корп.": 'Клубный дом "Легенда"',
                                "Продавец": "CG Development",
                                "Район": "-",
                                "Сдача": sdacha,
                                "Цена 100%": price,
                                "за м2": int(float(price) / s_full),
                                "Баз. цена": price,
                                "Вознаграж.": "",
                            }
                        )
                except Exception as ex:
                    asyncio.run(self.update_err(error="LegendaParser " + str(ex)))
                    logger.warning(f'Invalid URL_2 Legenda ({item}) ->\n{ex}\n')
        except Exception as ex:
            self._fatal_error = True
            asyncio.run(self.update_err(error="LegendaParser // Fatal ERROR  -  " + str(ex)))
            logger.error(f'Fatal ERROR Legenda ->\n{ex}\n\n')

        self.floor_count = len(self.result_mass)

# if __name__ == '__main__':
#     per = LegendaParser(
#         exel=True,
#         retry_count=1
#     )
#     per.run()