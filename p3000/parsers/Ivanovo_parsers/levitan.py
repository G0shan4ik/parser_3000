import asyncio

from requests import Session

from loguru import logger

from p3000.parsers.base import BaseParserRequests


class LevitanParser(BaseParserRequests):
    def __init__(self, err_name=None, exel: bool = False, single: bool = False):
        super().__init__(
            all_links=[],
            site_name='levitan',
            exel=exel,
            err_name=err_name if err_name else ["single", 'Levitan'],
            single=single
        )

        self.referer = 'http://xn----8sbfldpkjw2c.xn--p1ai'
        self.token_url = 'https://sso.profitbase.ru/api/oauth2/token'

        self.payload = {
            "client_id": "site_widget",
            "client_secret": "site_widget",
            "grant_type": "site_widget",
            "scope": "SITE_WIDGET",
            "referer": self.referer
        }

        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Origin": self.referer,
            "Referer": f'{self.referer}/',
            "User-Agent": "Mozilla/5.0",
            "X-Tenant-Id": "20569"
        }

        self.bearer = ''

    @staticmethod
    def get_custom_field(item: dict, field_id: str, default='-'):
        for field in item.get('custom_fields', []):
            if field.get('id') == field_id and field.get('value') is not None:
                return field['value']
        return default

    @staticmethod
    def get_otd(item: dict) -> str:
        facing = str(item['attributes'].get('facing') or '').lower()
        if facing in ('', 'нет', 'none'):
            return 'Без отделки'
        elif 'предчист' in facing:
            return 'П/Чист'
        elif 'чист' in facing:
            return 'Чист'
        return facing

    @staticmethod
    def get_tualet(item: dict) -> str:
        combined = item['attributes'].get('combined_bathroom_count') or 0
        separated = item['attributes'].get('separated_bathroom_count') or 0
        if combined:
            return 'С'
        elif separated:
            return 'Р'
        return '-'

    @staticmethod
    def get_sdacha(item: dict) -> str:
        building_state = LevitanParser.get_custom_field(item, 'building_states')
        return 'Сдан' if 'сдан' in str(building_state).lower() else building_state

    @staticmethod
    def to_number(value):
        try:
            return float(str(value).replace(' ', '').replace(',', '.'))
        except (ValueError, TypeError):
            return '-'

    @staticmethod
    def to_price(value):
        try:
            number = float(str(value).replace(' ', '').replace(',', '.'))
            return int(number) if number.is_integer() else round(number, 2)
        except (ValueError, TypeError):
            return '-'

    def pars_all_data(self) -> None:
        try:
            with Session() as _session:
                response = _session.post(self.token_url, json=self.payload, headers=self.headers)
                if response.status_code == 200:
                    self.bearer = response.json()['access_token']
                    logger.success('Levitan; Pars Bearer')
                else:
                    self._fatal_error = True
                    asyncio.run(self.update_err(error="LevitanParser // Invalid Bearer  -  "))
                    logger.error('Invalid Bearer Levitan\n\n')
                    return

                main_headers = {
                    "authorization": f"Bearer {self.bearer}",
                    "Accept": "application/json, text/plain, */*",
                    "Origin": "https://smart-catalog.profitbase.ru",
                    "Referer": "https://smart-catalog.profitbase.ru/",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 YaBrowser/25.12.0.0 Safari/537.36"
                }

                response_data = _session.get(
                    url='https://pb20569.profitbase.ru/api/v4/json/property?propertyTypeAliases%5B0%5D=property&status%5B0%5D=AVAILABLE&limit=100&full=true&returnFilteredCount=true',
                    headers=main_headers
                )
                data = response_data.json()

                if data['data']['filteredCount'] % 100 == 0:
                    rng = data['data']['filteredCount'] // 100
                else:
                    rng = data['data']['filteredCount'] // 100 + 1

                for idx in range(rng):
                    if idx != 0:
                        response_data = _session.get(
                            url=f'https://pb20569.profitbase.ru/api/v4/json/property?propertyTypeAliases%5B0%5D=property&status%5B0%5D=AVAILABLE&limit=100&offset={100 * idx}&full=true&returnFilteredCount=true',
                            headers=main_headers
                        )
                        data = response_data.json()

                    for item in data['data']['properties']:
                        try:
                            number = item['number']

                            self.result_mass.append(
                                {
                                    "Тип": f"{item['rooms_amount']}К" if item['rooms_amount'] != 0 else 'СТ',
                                    "S общ": self.to_number(item['area']['area_total']),
                                    "S жил": self.to_number(item['area']['area_living']),
                                    "S кухни": '-',
                                    "Отд.": self.get_otd(item),
                                    "С/у": self.get_tualet(item),
                                    "Балкон": '-',
                                    "Этаж": item['floor'],
                                    "№ объекта": int(number) if str(number).isdigit() else number,
                                    "ЖК, оч. и корп.": 'ЖК Левитан',
                                    "Продавец": 'Аквилон',
                                    "Район": "Иваново, Проспект Ленина д. 55",
                                    "Сдача": self.get_sdacha(item),
                                    "Цена 100%": self.to_price(item['price'].get('value')),
                                    "за м2": self.to_price(item['price'].get('pricePerMeter')),
                                    "Баз. цена": '-',
                                    "Вознаграж.": '',
                                }
                            )
                            logger.info(
                                f'Levitan; Success pars Item №{number} out of {data["data"]["filteredCount"]}')
                        except Exception as ex:
                            asyncio.run(self.update_err(error="LevitanParser: " + str(ex)))
                            logger.warning(
                                f'''Invalid item Levitan: {str(item)[:100]}...\nExeption: {ex}\n''')
        except Exception as ex:
            self._fatal_error = True
            asyncio.run(self.update_err(error="LevitanParser // Fatal ERROR  -  " + str(ex)))
            logger.error(f'Fatal ERROR Levitan ->\n{ex}\n\n')

        self.floor_count = len(self.result_mass)


if __name__ == '__main__':
    per = LevitanParser(
        exel=True
    )
    per.run()
