import asyncio

from requests import Session

from loguru import logger
from bs4 import BeautifulSoup
import lxml

from p3000.parsers.base import BaseParserRequests


class MiyataParser(BaseParserRequests):
    def __init__(self, err_name=None, exel: bool = False, single: bool = False):
        super().__init__(
            all_links=[],
            site_name='miyata',
            exel=exel,
            err_name=err_name if err_name else ["single", 'Miyata'],
            single=single
        )

        self.feed_url = 'https://pb20569.profitbase.ru/export/profitbase_xml/4620e1292e1dcf04987de49a024f01b8?scheme=https'

        self.headers = {
            "Accept": "application/xml, text/xml, */*",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 YaBrowser/25.12.0.0 Safari/537.36"
        }

    @staticmethod
    def get_text(offer: BeautifulSoup, selector: str, default: str = '-') -> str:
        item = offer.select_one(selector)
        return item.text.strip() if item and item.text.strip() else default

    @staticmethod
    def get_custom_field(offer: BeautifulSoup, field_id: str, default: str = '-') -> str:
        for field in offer.find_all('custom-field'):
            name = field.find('field')
            if name and name.text.strip() == field_id:
                value = field.find('value')
                return value.text.strip() if value and value.text.strip() else default
        return default

    @staticmethod
    def to_number(value: str):
        try:
            return float(value.replace(',', '.'))
        except (ValueError, AttributeError):
            return '-'

    @staticmethod
    def to_price(value: str):
        try:
            number = float(str(value).replace(' ', '').replace('\xa0', '').replace(',', '.'))
            return int(number) if number.is_integer() else round(number, 2)
        except (ValueError, AttributeError):
            return '-'

    def pars_offer(self, offer: BeautifulSoup) -> dict:
        rooms = self.get_text(offer, 'rooms', '0')
        studio = self.get_text(offer, 'studio', '0')
        floor = self.get_text(offer, 'floor')
        number = self.get_text(offer, 'number')
        section = self.get_text(offer, 'building-section')

        full_area = self.get_text(offer, 'area > value')
        full_area_value = self.to_number(full_area)
        living_area = self.get_text(offer, 'living-space > value')
        kitchen_area = self.get_text(offer, 'kitchen-space > value')

        price_value = self.get_text(offer, 'price > value')
        if price_value == '-':
            price_value = self.get_custom_field(offer, 'price')
        price = self.to_price(price_value)

        price_m_value = self.get_text(offer, 'price > price-per-square-meter')
        if price_m_value == '-':
            price_m_value = self.get_custom_field(offer, 'price_meter')
        price_m = self.to_price(price_m_value)

        if price_m == '-' and price != '-' and full_area_value not in ('-', 0):
            price_m = round(price / full_area_value, 2)

        facing = self.get_text(offer, 'facing')
        if facing == 'Без отделки':
            otd = 'Без отделки'
        elif 'Предчист' in facing:
            otd = 'П/Чист'
        elif 'Чист' in facing:
            otd = 'Чист'
        else:
            otd = facing

        combined = self.get_text(offer, 'combined-bathroom-unit', '0')
        separated = self.get_text(offer, 'separated-bathroom-unit', '0')
        if combined not in ('-', '', '0') and separated not in ('-', '', '0'):
            tualet = 'С/Р'
        elif combined not in ('-', '', '0'):
            tualet = 'С'
        elif separated not in ('-', '', '0'):
            tualet = 'Р'
        else:
            tualet = '-'

        loggia = self.get_text(offer, 'loggia-count', '0')
        balcony = self.get_text(offer, 'balcony-count', '0')
        if loggia not in ('-', '', '0'):
            balkon = 'Л'
        elif balcony not in ('-', '', '0'):
            balkon = 'Б'
        else:
            balkon = '-'

        object_name = self.get_text(offer, 'object > name')
        locality = self.get_text(offer, 'object > location > locality-name')
        district = self.get_text(offer, 'object > location > district')
        year = self.get_text(offer, 'house > built-year')
        quarter = self.get_text(offer, 'house > ready-quarter')

        gk = f'ЖК "{object_name}", секция {section}' if section != '-' else f'ЖК "{object_name}"'
        rayon = f'{locality}, {district} р-н' if district != '-' else locality
        sdacha = f'{quarter} кв. {year}' if year != '-' and quarter != '-' else '-'
        number_value = int(number) if number.isdigit() else number

        return {
            "Тип": 'СТ' if rooms == '0' or studio == '1' else f'{rooms}К',
            "S общ": full_area_value,
            "S жил": self.to_number(living_area),
            "S кухни": self.to_number(kitchen_area),
            "Отд.": otd,
            "С/у": tualet,
            "Балкон": balkon,
            "Этаж": int(floor) if floor.isdigit() else floor,
            "№ объекта": number_value,
            "ЖК, оч. и корп.": gk,
            "Продавец": 'Аквилон',
            "Район": rayon,
            "Сдача": sdacha,
            "Цена 100%": price,
            "за м2": price_m,
            "Баз. цена": '-',
            "Вознаграж.": '',
        }

    def pars_all_data(self) -> None:
        try:
            with Session() as _session:
                response = _session.get(
                    url=self.feed_url,
                    headers=self.headers
                )
                soup = BeautifulSoup(response.text, 'xml')
                offers = soup.find_all('offer')

                logger.success(f'Miyata; Pars feed; All offers == {len(offers)}')

                for item in offers:
                    try:
                        status = self.get_text(item, 'status')
                        if status != 'AVAILABLE':
                            logger.info(f'Miyata; Item is {status}')
                            continue

                        logger.info(
                            f'Miyata; Success pars Item ({offers.index(item) + 1} out of {len(offers)}) '
                            f'№{self.get_text(item, "number")}')

                        self.result_mass.append(self.pars_offer(item))
                    except Exception as ex:
                        asyncio.run(self.update_err(error="MiyataParser: " + str(ex)))
                        logger.warning(
                            f'Miyata; Invalid offer: {item.get("internal-id")}\nExeption: {ex}\n')
        except Exception as ex:
            self._fatal_error = True
            asyncio.run(self.update_err(error="MiyataParser // Fatal ERROR  -  " + str(ex)))
            logger.error(f'Fatal ERROR Miyata ->\n{ex}\n\n')

        self.floor_count = len(self.result_mass)


if __name__ == '__main__':
    per = MiyataParser(
        exel=True
    )
    per.run()
