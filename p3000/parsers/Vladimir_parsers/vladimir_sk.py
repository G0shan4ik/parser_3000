from loguru import logger
from bs4 import BeautifulSoup
import lxml

from p3000.parsers.base import BaseAsyncParserRequests

import aiohttp
import asyncio
from requests import get


class VladimirParser(BaseAsyncParserRequests):
    def __init__(self, err_name = None, exel: bool = False, single: bool = False):
        super().__init__(
            all_links=[
                'https://vladimir.sk-continent.ru/api/v1/property/properties/?type=0&page=1&page_size=1',
                'https://www.sk-continent.ru/api/v1/property/properties/?type=0&page=1&page_size=1'
            ],
            site_name='vladimir_sk',
            exel=exel,
            err_name=err_name if err_name else ["single", 'VladimirSK'],
            single=single
        )

        self.session = None

        self.__rooms_pattern = {
            "4-комнатная": "4К",
            "3-комнатная": "3К",
            "2-комнатная": "2К",
            "1-комнатная": "1К",
            "Студия": 'СТ'
        }
        self.__facing_pattern = {
            "Строительная": "П/Чист",
            "Черновая отделка": "Черн",
            "": "",
        }
        self.__S_Y = {
            '1 раздельный': 'P',
            "2 совмещенных": 2,
            "1 совмещенный": "C",
            "2 раздельных": 2,
        }


    async def return_s_y(self, url: str) -> str | int:
        async with self.session.get(url) as response:
            soup = BeautifulSoup(await response.text(encoding='utf-8'), 'lxml')

        mass = soup.select_one('div.flat-details-properties').text.split('\n\n')
        for item in mass:
            if 'Тип санузла' in item:
                idx = mass.index(item)
                return self.__S_Y[mass[idx + 1]]

    @staticmethod
    def num(n) -> float | int:
        try:
            return int(n)
        except ValueError:
            return float(n)

    async def init_session(self) -> None:
        self.session = aiohttp.ClientSession()

    async def close_session(self) -> None:
        if self.session:
            await self.session.close()

    async def pars_all_data(self, url: str) -> None:
        try:
            logger.info(f"VladimirSK; Start pars URL == {url}")
            pagination: int = get(url=url).json()['count']
            self.floor_count += pagination

            url = f'{url[:-1]}{pagination}'

            async with self.session.get(url) as response:
                data = await response.json()
                await asyncio.sleep(0)

            domain = 'https://www.sk-continent.ru' if 'www' in url else 'https://vladimir.sk-continent.ru'

            cnt = 0

            for item in data['results']:
                await asyncio.sleep(0)
                cnt += 1
                try:
                    logger.info(
                        f'VladimirSK; Континент, "{"Владимир" if "vladimir" in url else "Ковров"}"; link {cnt} out of {pagination}')
                    try:
                        price_100 = self.num(item["new_price"].replace('.00', ''))
                    except:
                        price_100 = self.num(item["price"].replace('.00', ''))
                    if item['status'] == 'AVAILABLE':
                        self.result_mass.append(
                            {
                                "Тип": self.__rooms_pattern[item['rooms_count']],
                                "S общ": self.num(item['area'].replace(' м²', '')),
                                "S жил": "-",
                                "S кухни": self.num(item['area_kitchen']),
                                "Отд.": self.__facing_pattern[item["facing"]],
                                "С/у": await self.return_s_y(f'{domain}{item["absolute_url"]}'),
                                "Балкон": "-",
                                "Этаж": item['floor_of'],
                                "№ объекта": int(item['id']),
                                "ЖК, оч. и корп.": item['house'],
                                "Продавец": item['project_title'],
                                "Район": "-",
                                "Сдача": item["development_quarter"].replace('квартал', 'кв.'),
                                "Цена 100%": price_100,
                                "за м2": self.num(price_100 / self.num(item['area'].replace(' м²', ''))),
                                "Баз. цена": self.num(item["price"].replace('.00', '')),
                                "Вознаграж.": '',
                            }
                        )
                        await asyncio.sleep(0)


                except Exception as ex:
                    if 'совмещенный, 1 раздельный' not in str(ex):
                        await self.update_err(error="VladimirParser: " + str(ex))
                    logger.warning(
                        f'''VladimirSK; Invalid link: {f'https://vladimir.sk-continent.ru{item["absolute_url"]}'}\nExeption: {ex}\n''')
        except Exception as ex:
            self._fatal_error = True
            await self.update_err(error="VladimirParser // Fatal ERROR  -  " + str(ex))
            logger.error(f'Fatal ERROR VladimirSK for url({url}) ->\n{ex}\n\n')

        self.floor_count = len(self.result_mass)


if __name__ == '__main__':
    per = VladimirParser(
        exel=True
    )
    asyncio.run(per.run())