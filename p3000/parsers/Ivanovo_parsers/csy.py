import asyncio
from pprint import pprint

from loguru import logger

from p3000.parsers.base import BaseParserRequests

from requests import post


class CSYParser(BaseParserRequests):
    def __init__(self, err_name = None, exel: bool = False, single: bool = False):
        super().__init__(
            all_links='',
            site_name='csy',
            exel=exel,
            err_name=err_name if err_name else ["single", 'CSY'],
            single=single
        )

        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'ru,en;q=0.9',
            'referer': 'https://xn--37-nmcin.xn--p1ai/',
            'Content-Type': 'application/json',
            'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "YaBrowser";v="25.4", "Yowser";v="2.5"',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 YaBrowser/25.4.0.0 Safari/537.36',
            'priority': 'u=1, i',
            'origin': 'https://xn--37-nmcin.xn--p1ai',
            'content-length': '566'
        }

    def get_dict_rayon(self) -> dict:
        try:
            result = dict()
            response = post(
                url='https://api.macroserver.ru/estate/catalog/?domain=xn--37-nmcin.xn--p1ai&check=NStoGCiODcOh9bhKcb6uqRJo3SbI32-ITKzpo_5jiseyiHBGrMLIAEQsvXyqJ1c4fDE3NDc5NDA4MDF8MmQ5NmE&type=catalog&inline=true&issetJQuery=1&uuid=989ed084-0fd0-4168-80d2-d27ce1a88daa&cookie_base64=eyJfeW1fdWlkIjoiMTc0Nzg0NDY0MDc4NzcyMzQ4NCJ9&time=1747940801&token=7f6b072129390d7cc6b9a08f3f353597/',
                json={"action": "get_data", "data": {"cabinetMode": False}, "auth_token": None, "locale": None}
            )
            _data = response.json()

            for item in _data['houses']:
                if '&nbsp;' in item['name']:
                    result[item['id']] = item['name'].replace('&nbsp;', ' ')
            return result
        except Exception as ex:
            asyncio.run(self.update_err(error="CSYParser: " + str(ex)))
            logger.warning(f'''CSY; Invalid pars Rayon\nExeption: {ex}\n''')

    def pars_all_data(self) -> None:
        try:
            full_json: list[dict] = []
            rayons = self.get_dict_rayon()
            for num in range(0, 100):
                response = post(
                    url='https://api.macroserver.ru/estate/catalog/?domain=xn--37-nmcin.xn--p1ai&check=NStoGCiODcOh9bhKcb6uqRJo3SbI32-ITKzpo_5jiseyiHBGrMLIAEQsvXyqJ1c4fDE3NDc5MjI5Nzh8ZGFjOTk&type=catalog&inline=true&issetJQuery=1&uuid=9116f588-7855-4c7e-9745-d476fc86bb8f&cookie_base64=eyJfeW1fdWlkIjoiMTc0Nzg0NDY0MDc4NzcyMzQ4NCJ9&time=1747922978&token=1f206bd94ddbe8d37b075921cd25e2a7/',
                    json={"action": "objects_list", "data": {"category": "flat", "activity": "sell", "page": num,
                                                             "filters": {"studio": "null", "rooms": [], "restorations": [],
                                                                         "promos": [], "tags": [], "riser_side": [],
                                                                         "geo_city": None, "floors": [], "houses_ids": [],
                                                                         "type": None, "areaFrom": None, "areaTo": None,
                                                                         "priceFrom": None, "priceTo": None,
                                                                         "priceM2From": None, "priceM2To": None,
                                                                         "priceRentFrom": None, "priceRentTo": None,
                                                                         "priceRentM2From": None, "priceRentM2To": None,
                                                                         "status": None}, "complex_id": None,
                                                             "house_id": None, "orders": [], "complex_search": [],
                                                             "house_search": [], "lazy": True, "cabinetMode": False},
                          "auth_token": None, "locale": None},
                )
                _data = response.json()
                logger.info(f"CSY/JSON; {num}")
                if not _data['objects']:
                    logger.warning('CSY/JSON; exit')
                    break
                full_json.extend(_data['objects'])

            for item in full_json:
                try:
                    if item['status'] != 'available':
                        logger.info('CSY; Item was sale')
                        continue
                    area_ob = '-'
                    try:
                        area_ob = round(float(item['estate']['estate_area']), 2)
                    except:
                        ...

                    _dct = {
                        "Тип": 'СТ' if item.get('studia', '') else item["rooms"].upper(),
                        "S общ": area_ob,
                        "S жил": '-',
                        "S кухни": '-',
                        "Отд.": '-',
                        "С/у": '-',
                        "Балкон": "-",
                        "Этаж": int(item['estate']['estate_floor']),
                        "№ объекта": '-',
                        "ЖК, оч. и корп.": item['complex_title'].replace('»', '"').replace('«', '"'),
                        "Продавец": 'Центр Строительных Услуг',
                        "Район": rayons[item['house_id']],
                        "Сдача": '-',
                        "Цена 100%": int(item['estate']['estate_price'].split('.')[0]),
                        "за м2": round(float(item['estate']['estate_price_m2']), 2),
                        "Баз. цена": '-',
                        "Вознаграж.": '',
                    }
                    self.result_mass.append(_dct)
                    logger.info(f'CSY; Success pars Item №{full_json.index(item) + 1} out of {len(full_json)}')
                except Exception as ex:
                    asyncio.run(self.update_err(error="CSYParser: " + str(ex)))
                    logger.warning(f'CSY; Invalid item: {str(item)[:100]}...')
        except Exception as ex:
            self._fatal_error = True
            asyncio.run(self.update_err(error="CSYParser // Fatal ERROR  -  " + str(ex)))
            logger.error(f'Fatal ERROR CSY ->\n{ex}\n\n')

        self.floor_count = len(self.result_mass)
        logger.success(f'CSY; Success pars Item LEN == {self.floor_count}')


# if __name__ == '__main__':
#     per = CSYParser(
#         exel=True
#     )
#     per.run()