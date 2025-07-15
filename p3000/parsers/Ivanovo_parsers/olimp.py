from loguru import logger

from p3000.parsers.base import BaseAsyncParserRequests

import aiohttp
import json

import asyncio


class OlimpParser(BaseAsyncParserRequests):
    def __init__(self, err_name = None, exel: bool = False):
        super().__init__(
            all_links=[
                'https://domoplaner.ru/widget-api/widget/418-toSOJO/',
                'https://domoplaner.ru/widget-api/widget/418-Ggqq02/',
                'https://domoplaner.ru/widget-api/widget/418-Hm8uny/'
            ],
            site_name='olimp',
            exel=exel,
            err_name=err_name if err_name else ["single", 'Olimp']
        )

        self.session = None

        self.dct_names = {
            'ЖК Олимпийский': ['418/toSOJO', 'ул. Павла Большевикова'],
            'ЖК Фаворит': ['418/Ggqq02', 'Проспект Шереметевский'],
            'ЖК Континент 5': ['418/Hm8uny', 'Переулок Конспиративный']
        }

    async def init_session(self) -> None:
        self.session = aiohttp.ClientSession()

    async def close_session(self) -> None:
        if self.session:
            await self.session.close()

    async def pars_all_data(self, url: str) -> None:
        try:
            async with self.session.get(url) as response:
                data = json.loads(await response.text(encoding='utf-8'))
            len_flats = len(data['flats'])
            logger.info(f"Start pars Olimp; URL == {url}; Count links == {len_flats}")
            for flat in data['flats']:
                await asyncio.sleep(0)
                try:
                    dirty_sdacha = str(data['houses'][0]['date_release'])
                    sdacha = f'{dirty_sdacha[-1]} кв. {dirty_sdacha[:-1]}'
                    self.result_mass.append(
                        {
                            "Тип": 'СТ' if flat['is_studio'] != 0 else f"{flat['rooms']}К",
                            "S общ": flat['area'],
                            "S жил": flat['area_living'] if flat['area_living'] else '-',
                            "S кухни": flat['area_kitchen'] if flat['area_kitchen'] else '-',
                            "Отд.": '-',
                            "С/у": '-',
                            "Балкон": "-",
                            "Этаж": flat['floor_number'],
                            "№ объекта": flat['number'],
                            "ЖК, оч. и корп.": data['projectInfo']['title'],
                            "Продавец": 'ОЛИМП',
                            "Район": self.dct_names[data['projectInfo']['title']][1],
                            "Сдача": sdacha,
                            "Цена 100%": flat['price_with_discount'],
                            "за м2": flat['metr_price'],
                            "Баз. цена": '-',
                            "Вознаграж.": '',
                        }
                    )
                    await asyncio.sleep(0)
                    logger.info(
                        f'Olimp; Pars link (https://olimpstroy37.ru/#dp/{self.dct_names[data["projectInfo"]["title"]][0]}/plans?state=plans&flat_id={flat["id"]}); link {data["flats"].index(flat)+1} out of {len_flats}')
                except Exception as ex:
                    await self.update_err(error="OlimpParser " + str(ex))
                    logger.warning(
                        f'Invalid link Olimp: https://olimpstroy37.ru/#dp/{self.dct_names[data["projectInfo"]["title"]][0]}/plans?state=plans&flat_id={flat["id"]}\nExeption: {ex}\n')
        except Exception as ex:
            self._fatal_error = True
            await self.update_err(error="OlimpParser // Fatal ERROR  -  " + str(ex))
            logger.error(f'Fatal ERROR Olimp for url({url}) ->\n{ex}\n\n')


if __name__ == '__main__':
    per = OlimpParser(
        exel=True,
    )
    asyncio.run(per.run())