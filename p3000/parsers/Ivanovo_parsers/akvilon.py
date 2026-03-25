import asyncio
import re
from requests import Session

from loguru import logger
from bs4 import BeautifulSoup
import lxml

from p3000.parsers.base import BaseParserRequests


class AkvilonParser(BaseParserRequests):
    def __init__(self, err_name=None, exel: bool = False, single: bool = False):
        super().__init__(
            all_links=[],
            site_name='akvilon',
            exel=exel,
            err_name=err_name if err_name else ["single", 'Akvilon'],
            single=single
        )
        self.token_url = 'https://sso.profitbase.ru/api/oauth2/token'
        self.payload = {
            "client_id": "site_widget",
            "client_secret": "site_widget",
            "grant_type": "site_widget",
            "scope": "SITE_WIDGET",
            "referer": "https://xn---37-6cdzdqntl0cmx.xn--p1ai"
        }

        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Origin": "https://xn---37-6cdzdqntl0cmx.xn--p1ai",
            "Referer": "https://xn---37-6cdzdqntl0cmx.xn--p1ai/",
            "User-Agent": "Mozilla/5.0",
            "X-Tenant-Id": "20569"
        }

        self.bearer = ''

        self.__pars_links: list[str] = []

    def pars_all_data(self) -> None:
        try:
            with Session() as _session:
                response = _session.post(self.token_url, json=self.payload, headers=self.headers)
                if response.status_code == 200:
                    self.bearer = response.json()['access_token']
                    logger.success('Aviator; Pars Bearer')
                else:
                    self._fatal_error = True
                    asyncio.run(self.update_err(error="AkvilonParser // Invalid Bearer  -  "))
                    logger.error(f'Invalid Bearer Akvilon\n\n')
                    return

                response_data = _session.get(
                    url='https://pb20569.profitbase.ru/api/v4/json/property?houseId=145409&returnFilteredCount=true',
                    headers = {
                    "authorization": f"Bearer {self.bearer}",
                    "Accept": "application/json, text/plain, */*",
                    "Origin": "https://smart-catalog.profitbase.ru",
                    "Referer": "https://smart-catalog.profitbase.ru/",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 YaBrowser/25.12.0.0 Safari/537.36"
                    }
                )
                from pprint import pprint
                data = response_data.json()
                for item in data['data']['properties']:
                    try:
                        logger.info(f'Akvilon {item["status"] if item["status"] != "AVAILABLE" else item["status"] + " pars!"}')
                        if item['status'] == 'AVAILABLE':
                            self.result_mass.append(
                                {
                                    "Тип": f"{item['rooms_amount']}К" if item['rooms_amount'] != 0 else 'СТ',
                                    "S общ": item['area']['area_total'],
                                    "S жил": item['area']['area_living'],
                                    "S кухни": item['area']['area_kitchen'],
                                    "Отд.": '-',
                                    "С/у": '-',
                                    "Балкон": '-',
                                    "Этаж": item['floor'],
                                    "№ объекта": int(item['number']),
                                    "ЖК, оч. и корп.": 'ЖК Манифест',
                                    "Продавец": 'Akvilon',
                                    "Район": '-',
                                    "Сдача": '-',
                                    "Цена 100%": int(item['price']['value']),
                                    "за м2": int(item['price']['pricePerMeter']),
                                    "Баз. цена": '-',
                                    "Вознаграж.": '',
                                }
                            )
                    except Exception as ex:
                        asyncio.run(self.update_err(error="AkvilonParser: " + str(ex)))
                        logger.warning(f'''Invalid link Akvilon: {item}\nExeption: {ex}\n''')
        except Exception as ex:
            self._fatal_error = True
            asyncio.run(self.update_err(error="AkvilonParser // Fatal ERROR  -  " + str(ex)))
            logger.error(f'Fatal ERROR Akvilon ->\n{ex}\n\n')

        self.floor_count = len(self.result_mass)


if __name__ == '__main__':
    per = AkvilonParser(
        exel=True
    )
    per.run()