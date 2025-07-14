import asyncio
from typing import Awaitable

from loguru import logger

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import lxml

from p3000.parsers.base import BaseAsyncParserRequests


class GloraxParser(BaseAsyncParserRequests):
    def __init__(self, err_name = None, exel: bool = False):
        super().__init__(
            all_links=[
                'https://glorax.com/flats?city=7&project=74&area_min=29.07&area_max=77.64&order=price',
            ],
            site_name='glorax',
            exel=exel,
            err_name=err_name if err_name else ["single", 'Glorax']
        )

        self.session = None

        self.rooms_pattern = {
            4: "4К",
            3: "3К",
            2: "2К",
            1: "1К",
            0: 'СТ'
        }

        self.playwright = None
        self.browser = None
        self.context = None
        self.session = None

    @staticmethod
    def get_pretty_data_1(sp) -> dict:
        dct = dict()
        for item in sp.select_one('div.column_fpjNO._desktop_6P5R7').select('div'):
            data = item.select('span')
            if 'LotBottomArea' in str(item):
                for new_item in item.select('div.area_5M9Eq'):
                    dt = new_item.select_one('span.t5').text.replace('\n', '').replace('м2', '').strip()
                    if 'м2' in new_item.select_one('span.t5').text:
                        dt = float(
                            new_item.select_one('span.t5').text.replace('\n', '').replace('м2', '').replace(',',
                                                                                                            '.').strip())
                    dct[new_item.select_one('span.l6').text] = dt
                continue
            try:
                dct[data[0].text] = data[1].text.replace('\n', '').replace('м2', '').replace(',', '.').strip()
            except:
                break
        return dct

    async def init_session(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch()
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.2 Safari/605.1.15",
            base_url='https://glorax.com',
        )
        self.session = await self.context.new_page()

    async def close_session(self):
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def pars_links(self) -> list[list]:
        try:
            logger.info('Glorax; Start pars all Glorax pars_links')
            lim, offset, result = 21, 0, []
            headers = {
                'referer': 'https://glorax.com/flats?city=7&project=74&area_min=29.07&area_max=77.64&price_min=4009998.9975&price_max=10349999.0025&floor_min=2&floor_max=15&order=price',
                'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "YaBrowser";v="25.2", "Yowser";v="2.5"',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36',
                'sec-ch-ua-platform': '"Windows"',
                'sec-ch-ua-mobile': '?0',
                'accept': 'application/json, text/plain, */*',
                'accept-encoding': 'gzip, deflate, br, zstd',
                'accept-language': 'ru,en;q=0.9'
            }
            while True:
                response = await (await self.session.request.get(
                    url=f'https://glorax.com/api/flats/?limit={lim}&offset={offset}&booked=false&city=7&project=74&area_min=29.07&area_max=77.64&price_min=4009998.9975&price_max=10349999.0025&floor_min=2&floor_max=15&order=price',
                    headers=headers
                )).json()
                if len(response['results']) < 1:
                    break
                offset += lim
                for item in response['results']:
                    result.append(
                        [
                            f'https://glorax.com/flats/{item["id"]}',
                            item["price"],
                            item["furnish_display"],
                            f'{item["completion_quarter"]} кв. {item["completion_year"]}',
                            int(item['rooms']),
                            item["number"]
                        ]
                    )
                    await asyncio.sleep(0)
            self.floor_count = len(result)
            logger.info(f'Glorax; Len Pars Glorax Links == {len(result)}')
            return result
        except Exception as ex:
            await self.update_err(error="GloraxParser: " + str(ex))
            logger.warning(
                f'''Glorax pars_links error\nExeption: {ex}\n''')

    async def pars_data(self, data: str) -> None:
        link, price, otd, completion, rooms, number = data.split('#')
        try:
            logger.info(f'Glorax; Start pars url == {link}')
            price = int(float(price))
            response = await self.session.request.get(
                url=link
            )
            soup = BeautifulSoup(await response.text(), 'lxml')
            pr_data = self.get_pretty_data_1(sp=soup)
            self.result_mass.append(
                {
                    "Тип": self.rooms_pattern[int(rooms)],
                    "S общ": float(pr_data["Общая площадь"]),
                    "S жил": float(pr_data["Жилая площадь"]),
                    "S кухни": '-',
                    "Отд.": otd,
                    "С/у": '-',
                    "Балкон": "-",
                    "Этаж": pr_data["Этаж"],
                    "№ объекта": int(number),
                    "ЖК, оч. и корп.": 'Glorax Октябрьский',
                    "Продавец": 'СЗ АРКТУР',
                    "Район": "Октябрьский р-н",
                    "Сдача": completion,
                    "Цена 100%": price,
                    "за м2": round(float(float(price) / float(pr_data["Общая площадь"])), 2),
                    "Баз. цена": '-',
                    "Вознаграж.": '',
                }
            )
            await asyncio.sleep(0)
        except Exception as ex:
            await self.update_err(error="GloraxParser: " + str(ex))
            logger.warning(
                f'''Invalid link Glorax: {link}\nExeption: {ex}\n''')

    async def pars_all_data(self, url: str) -> None:
        try:
            logger.info(f"Start pars Glorax; URL == {url}")
            response = await self.session.request.get(
                url
            )
            if response.status not in [200, 201, 202, 203, 204]:
                await self.update_err(error="GloraxParser: " + f"Status code error == {response.status}")
                logger.warning('Invalid status code')

            all_links: list[list] = await self.pars_links()
            processes: [Awaitable] = []

            for lnk in all_links:
                logger.info(f'Glorax; Create PROCESS for Link №{all_links.index(lnk) + 1} out of {len(all_links)}')
                processes.append(self.pars_data(f'{lnk[0]}#{lnk[1]}#{lnk[2]}#{lnk[3]}#{lnk[4]}#{lnk[-1]}'))

            for process in self.chunks(processes, 4):
                await asyncio.gather(*process)
        except Exception as ex:
            self._fatal_error = True
            await self.update_err(error="GloraxParser // Fatal ERROR  -  " + str(ex))
            logger.error(f'Fatal ERROR Glorax for url({url}) ->\n{ex}\n\n')


if __name__ == '__main__':
    per = GloraxParser(
        exel=True
    )
    asyncio.run(per.run())