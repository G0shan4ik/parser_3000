import asyncio

from loguru import logger

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import lxml

from p3000.parsers.base import BaseAsyncParserRequests


class GloraxParser(BaseAsyncParserRequests):
    def __init__(self, err_name = None, exel: bool = False, single: bool = False):
        super().__init__(
            all_links=[
                'https://glorax.com/flats?project=glorax-oktiabrskii&order=price'
            ],
            site_name='glorax',
            exel=exel,
            err_name=err_name if err_name else ["single", 'Glorax'],
            single=single
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
    def extract_living_area(text: str) -> int|float:
        try:
            from bs4 import BeautifulSoup
            import lxml

            soup = BeautifulSoup(text, 'lxml')
            res = float(soup.select_one('div.LotCharacteristics_livingSquare__viR_f').text.replace('Жилая площадь', '').split(' ')[0].replace(',', '.'))
            return res
        except:
            return 0

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

    async def pars_links(self) -> None:
        try:
            logger.info('Glorax; Start pars all Glorax pars_links')
            page = 1
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
                logger.info(
                    f'''Glorax pars page {page}''')
                response = await (await self.session.request.get(
                    url=f'https://glorax-api-dev.city-digital.ru/api/v1/filter/lots?page={page}&perPage=15&order=price&filter[type]=flat&filter[project]=glorax-oktiabrskii&filter[withReserved]=false',
                    headers=headers
                )).json()

                if page > 30:
                    break

                for item in response['data']:
                    s_live = self.extract_living_area(
                        await (
                            await self.session.request.get(f'https://glorax.com/flats/{item["id"]}')
                        ).text()
                    )

                    self.result_mass.append(
                        {
                            "Тип": f'{item["rooms"]}К' if item['rooms'] != 0 else 'СТ',
                            "S общ": item['square'],
                            "S жил": s_live,
                            "S кухни": '-',
                            "Отд.": '-',
                            "С/у": '-',
                            "Балкон": "-",
                            "Этаж": item["floor"],
                            "№ объекта": item['roomNum'],
                            "ЖК, оч. и корп.": 'Glorax Октябрьский',
                            "Продавец": 'СЗ АРКТУР',
                            "Район": "Октябрьский р-н",
                            "Сдача": item['deliveryDate'][:4] if item['deliveryDate'][:4].isdigit() else '-',
                            "Цена 100%": item['priceOffer'],
                            "за м2": round(float(float(item['priceOffer']) / float(item['square'])), 2),
                            "Баз. цена": '-',
                            "Вознаграж.": '',
                        }
                    )
                    await asyncio.sleep(0)

                page += 1
        except Exception as ex:
            await self.update_err(error="GloraxParser: " + str(ex))
            logger.warning(
                f'''Glorax pars_links error\nExeption: {ex}\n''')

    async def pars_all_data(self, url: str) -> None:
        try:
            logger.success(f"Glorax; Start pars; URL == {url}")

            await self.pars_links()
        except Exception as ex:
            self._fatal_error = True
            await self.update_err(error="GloraxParser // Fatal ERROR  -  " + str(ex))
            logger.error(f'Fatal ERROR Glorax for url({url}) ->\n{ex}\n\n')

        self.floor_count = len(self.result_mass)


if __name__ == '__main__':
    per = GloraxParser(
        exel=True
    )
    asyncio.run(per.run())

