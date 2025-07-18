import asyncio
import time
from random import randint

from loguru import logger

from p3000.parsers.base import BaseParserRequests

import requests


class DefaultKvartalParser(BaseParserRequests):
    def __init__(self, err_name = None, exel: bool = False, single: bool = False):
        super().__init__(
            all_links=[''],
            site_name='default_kvartal',
            exel=exel,
            err_name=err_name if err_name else ["single", 'DefaultKvartal'],
            single=single
        )

        self.headers_1 = {
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Content-Type': 'application/json',
            'Host': 'sso.profitbase.ru',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0',
            'origin': 'https://ivkvartal.ru',
            'referer': 'https://ivkvartal.ru/',
            'x-tenant-id': '19650',
            'priority': 'u=1, i',
            'content-length': '139',
            'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "YaBrowser";v="25.4", "Yowser";v="2.5"'
        }

        self.data_1 = {
            "client_id": "site_widget",
            "client_secret": "site_widget",
            "grant_type": "site_widget",
            "referer": "https://ivkvartal.ru",
            "scope": "SITE_WIDGET"
        }

    def get_all_pars_urls(self, cnt: int) -> None:
        try:
            for idx in range(1, int(cnt / 75) + 1):
                self.all_links.append(
                    f'https://pb19650.profitbase.ru/api/v4/json/property?projectIds%5B0%5D=48335&projectIds%5B1%5D=48960&projectIds%5B2%5D=48833&projectIds%5B3%5D=48793&projectIds%5B4%5D=48334&projectIds%5B5%5D=51027&isHouseFinished=0&status%5B0%5D=AVAILABLE&limit=75&offset={75 * idx}&full=true&returnFilteredCount=true'
                )
            logger.success('DefaultKvartal; Create All Pars Links)')
        except Exception as ex:
            asyncio.run(self.update_err(error="DefaultKvartalParser: " + str(ex)))
            logger.warning(f'''DefaultKvartal; Invalid pars all_links\nExeption: {ex}\n''')

    def pars_all_data(self) -> None:
        try:
            with requests.Session() as session:
                response = session.post(
                    url='https://sso.profitbase.ru/api/oauth2/token',
                    headers=self.headers_1,
                    json=self.data_1,
                )
                token = response.json()["access_token"]
                main_headers = {
                    'authorization': f'Bearer {token}',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0',
                    'referer': 'https://smart-catalog.profitbase.ru/',
                    'priority': 'u=1, i',
                    'origin': 'https://smart-catalog.profitbase.ru',
                    'Accept': 'application/json, text/plain, */*',
                    'Accept-Encoding': 'gzip, deflate, br, zstd',
                    'Accept-Language': 'ru,en;q=0.9',
                    'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "YaBrowser";v="25.4", "Yowser";v="2.5"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"'
                }
                full_json: list[dict] = []

                response = session.get(
                    url='https://pb19650.profitbase.ru/api/v4/json/property?projectIds%5B0%5D=48335&projectIds%5B1%5D=48960&projectIds%5B2%5D=48833&projectIds%5B3%5D=48793&projectIds%5B4%5D=48334&projectIds%5B5%5D=51027&isHouseFinished=0&status%5B0%5D=AVAILABLE&limit=75&full=true&returnFilteredCount=true',
                    headers=main_headers
                )
                _data = response.json()
                full_json.append(_data)
                self.get_all_pars_urls(cnt=_data['data']['filteredCount'])
                logger.info(f'DefaultKvartal/JSON; Pars 1 из {len(self.all_links) + 1}')
                for _url in self.all_links:
                    try:
                        _sleep = randint(1, 2)
                        logger.info(f'DefaultKvartal/JSON; ----- SLEEP {_sleep} second')
                        time.sleep(_sleep)
                        logger.info(f'DefaultKvartal/JSON; Pars {self.all_links.index(_url) + 2} out of {len(self.all_links) + 1}')
                        response_2 = session.get(
                            url=_url,
                            headers=main_headers
                        )
                        full_json.append(response_2.json())
                    except Exception as ex:
                        if _url :
                            asyncio.run(self.update_err(error="DefaultKvartalParser: " + str(ex)))
                        logger.warning(f'DefaultKvartal/JSON; Invalid url: {_url}')

            for one_json in full_json:
                for item in one_json['data']['properties']:
                    try:
                        if 'К ' in item['number']:
                            logger.warning('DefaultKvartal; Error  >--коммерция--<')
                            continue
                        if float(item['area']['area_total']) < 13:
                            logger.warning('DefaultKvartal; Error  >--KLADOVKA--<')
                            continue
                        if item['floor'] == -1:
                            logger.warning('DefaultKvartal; Error  >--KLADOVKA--<')
                            continue
                        _type = ''
                        _type = f'{item["rooms_amount"]}К'
                        if item['studio']:
                            _type = 'СТ'

                        try:
                            otd = 'П/Чист' if item['attributes']['facing'].capitalize() == 'Предчистовая' else 'Без отделки'
                        except:
                            otd = 'Без отделки'

                        _dct = {
                            "Тип": _type,
                            "S общ": item['area']['area_total'],
                            "S жил": item['area']['area_living'],
                            "S кухни": item['area']['area_kitchen'] if item['area']['area_kitchen'] else '-',
                            "Отд.": otd,
                            "С/у": '-',
                            "Балкон": "-",
                            "Этаж": item['custom_fields'][5]['value'],
                            "№ объекта": item['number'],
                            "ЖК, оч. и корп.": item['projectName'].replace('  ', ' '),
                            "Продавец": 'Квартал',
                            "Район": ', '.join(item['address'].split(', ')[:3]),
                            "Сдача": '',
                            "Цена 100%": item['custom_fields'][1]['value'],
                            "за м2": item['custom_fields'][9]['value'],
                            "Баз. цена": '-',
                            "Вознаграж.": '',
                        }
                        self.result_mass.append(_dct)
                        logger.info(f"DefaultKvartal; Success pars Item ({full_json.index(one_json) + 1}) №{one_json['data']['properties'].index(item) + 1} out of {len(one_json['data']['properties'])}")
                    except Exception as ex:
                        asyncio.run(self.update_err(error="DefaultKvartalParser: " + str(ex)))
                        logger.warning(f'DefaultKvartal; Invalid item: {str(item)[:100]}...')
        except Exception as ex:
            self._fatal_error = True
            asyncio.run(self.update_err(error="DefaultKvartalParser // Fatal ERROR  -  " + str(ex)))
            logger.error(f'Fatal ERROR DefaultKvartal ->\n{ex}\n\n')

        self.floor_count = len(self.result_mass)


# if __name__ == '__main__':
#     per = DefaultKvartalParser(
#         exel=True,
#     )
#     per.run()