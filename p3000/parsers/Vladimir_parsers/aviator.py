import asyncio

from loguru import logger
from bs4 import BeautifulSoup
import lxml

from p3000.parsers.base import BaseParserRequests

from requests import get


class AviatorParser(BaseParserRequests):
    def __init__(self, err_name = None, exel: bool = False, single: bool = False):
        super().__init__(
            all_links=[
                'https://kvartal-aviator.ru/kupit-kvartiru-v-kovrove/studii/',
                'https://kvartal-aviator.ru/kupit-kvartiru-v-kovrove/odnokomnatnye-kvartiry/',
                'https://kvartal-aviator.ru/kupit-kvartiru-v-kovrove/evrodvushki/',
                'https://kvartal-aviator.ru/kupit-kvartiru-v-kovrove/dvuhkomnatnye-kvartiry/',
                'https://kvartal-aviator.ru/kupit-kvartiru-v-kovrove/trehkomnatnye-kvartiry/',
                'https://kvartal-aviator.ru/kupit-kvartiru-v-kovrove/dom2/dvuhkomnatnye-kvartiry/',
                'https://kvartal-aviator.ru/kupit-kvartiru-v-kovrove/dom2/trehkomnatnye-kvartiry/',
                'https://kvartal-aviator.ru/kupit-kvartiru-v-kovrove/dom2/evrotreshki/',
                'https://kvartal-aviator.ru/kupit-kvartiru-v-kovrove/dom2/odnokomnatnye-kvartiry/',
                'https://kvartal-aviator.ru/kupit-kvartiru-v-kovrove/dom2/studii/'
            ],
            site_name='aviator',
            exel=exel,
            err_name=err_name if err_name else ["single", 'Aviator'],
            single=single
        )

        self.__pars_links: list[str] = []

    @staticmethod
    def get_2_price(data: BeautifulSoup) -> list[int]:
        try:
            one_price = int(data.select_one('span.i-hero__cost').text.replace(' руб.', '').replace(' ', ''))
            bez_price = int(data.select_one('span.i-hero__cost_line').text.replace(' руб.', '').replace(' ', ''))
            return [one_price, bez_price]
        except:
            ...
        one_price = int(data.select_one('span.i-hero__cost').text.replace(' руб.', '').replace(' ', ''))
        bez_price = '-'
        return [one_price, bez_price]

    @staticmethod
    def get_type_flat(data: BeautifulSoup) -> str:
        name = data.select_one('h1.i-hero__name').text.split()[0]
        if 'Студия' in name:
            return 'СТ'
        elif '1' in name:
            return '1К'
        elif '2' in name or 'Евродвушка' in name:
            return '2К'
        elif '3' in name or 'Евротрешка' in name:
            return '3К'

    @staticmethod
    def get_useful_information(data: BeautifulSoup) -> dict:
        data = [i.text.replace('\n', ' ').strip() for i in data.select_one('ul.i-hero__list').select('li')]
        res_data = {
            'Сдача': '-',
            'Этаж': '-',
            'S общ': '-'
        }
        for item in data:
            if 'Срок сдачи дома' in item:
                res_data['Сдача'] = item.replace('Срок сдачи дома ', '').replace('квартал ', 'кв.')[:-3]
            elif 'Этаж' in item:
                res_data['Этаж'] = int(item.replace('Этаж ', ''))
            elif 'Площадь, м²' in item:
                res_data['S общ'] = float(item.replace('Площадь, м² ', '').replace(',', '.'))

        return res_data

    def pars_all_data(self) -> None:
        try:
            for url in self.all_links:
                response = get(
                    url
                )
                soup = BeautifulSoup(response.text, 'lxml')
                for item in soup.select_one('div.choice__table').select('a'):
                    self.__pars_links.append(f'https://kvartal-aviator.ru{item.get("href")}')

            logger.info('Aviator; Pars all Aviator links; Start pars data')

            for item in self.__pars_links:
                logger.info(
                    f'Aviator; Link ({self.__pars_links.index(item) + 1} out of {len(self.__pars_links)})\n{item}')

                response = get(item)
                soup = BeautifulSoup(response.text, 'lxml')
                try:
                    if soup.select_one('span.i-hero__cost').text != 'Продано':
                        price_1, price_2 = self.get_2_price(soup)
                    else:
                        logger.info(f'Aviator; Link  -S O L D   O U T-  ({self.__pars_links.index(item) + 1} out of {len(self.__pars_links)})\n{item}')
                        continue
                    useful_information: dict = self.get_useful_information(soup)
                    self.result_mass.append(
                        {
                            "Тип": self.get_type_flat(soup),
                            "S общ": useful_information['S общ'],
                            "S жил": '-',
                            "S кухни": '-',
                            "Отд.": '-',
                            "С/у": '-',
                            "Балкон": 'Л' if 'Лоджия' in soup.select_one('ul.i-hero__list').text else '-',
                            "Этаж": int(useful_information['Этаж']),
                            "№ объекта": '-',
                            "ЖК, оч. и корп.": f'''Квартал "Авиатор", корпус {'2' if 'dom2' in item else '1'}''',
                            "Продавец": 'Квартал "Авиатор"',
                            "Район": '-',
                            "Сдача": useful_information['Сдача'],
                            "Цена 100%": price_1,
                            "за м2": int(float(price_1) / useful_information['S общ']),
                            "Баз. цена": price_2 if price_2 else price_1,
                            "Вознаграж.": '',
                        }
                    )

                except Exception as ex:
                    if 'ЗНАЧ' in str(ex):
                        logger.info(
                            f'Aviator; Link  -S O L D   O U T-  ({self.__pars_links.index(item) + 1} out of {len(self.__pars_links)})\n{item}')
                    else:
                        asyncio.run(self.update_err(error="AviatorParser: " + str(ex)))
                        logger.warning(f'''Invalid link Aviator: {item}\nExeption: {ex}\n''')
        except Exception as ex:
            self._fatal_error = True
            asyncio.run(self.update_err(error="AviatorParser // Fatal ERROR  -  " + str(ex)))
            logger.error(f'Fatal ERROR Aviator ->\n{ex}\n\n')

        self.floor_count = len(self.result_mass)


if __name__ == '__main__':
    per = AviatorParser(
        exel=True
    )
    per.run()