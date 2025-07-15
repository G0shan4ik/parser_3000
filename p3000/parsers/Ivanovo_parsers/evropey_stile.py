import asyncio

from loguru import logger
from bs4 import BeautifulSoup
import lxml

from p3000.parsers.base import BaseParserRequests, FlagKey

import requests


class EuropeyStileParser(BaseParserRequests):
    def __init__(self, err_name: FlagKey = 'EuropeyStile', exel: bool = False):
        super().__init__(
            all_links=[
                'https://европейскийстиль.рф/catalog?filter=eyJzIjpbIm4iXX0%3D&size=l',
                'https://европейскийстиль.рф/catalog?filter=eyJzIjpbIm4iXX0%3D',
                'https://европейскийстиль.рф/catalog?filter=eyJzIjpbIm4iXX0%3D&size=s'
            ],
            site_name='europey_stile',
            exel=exel,
            err_name=err_name
        )

        self.__pars_links: list[str] = []

    def pars_flat(self, link: str) -> dict:
        try:
            response = requests.get(link)
            if response.status_code not in [200, 201, 202, 203, 204]:
                logger.warning(f'EuropeyStile; Invalid Link  <MINI>  status_code == {response.status_code}; Link ({link})')
                return {}
            soup = BeautifulSoup(response.text, 'lxml')

            txt = soup.select_one('h1').text
            s_obsh, s_kuh, balk, = '', '-', '-'
            try:
                other_data = soup.select('div.Article_Body__3nPyw')[1].select_one('p').text.replace('● ', '').split(
                    '\n')
                for item in other_data:
                    if 'общая площадь' in item.lower():
                        s_obsh = float(item.replace('Общая площадь ', '').replace(' кв.м', ''))
                    elif 'кухня' in item.lower():
                        s_kuh = float(item.replace(' кв.м', '').split()[-1])
                    elif 'веранд' in item.lower():
                        balk = 'В'
                    elif 'лоджи' in item.lower():
                        balk = 'Л'
                    elif 'балкон' in item.lower():
                        balk = 'Б'
            except:
                try:
                    s_obsh = int(txt.split('площадью ')[-1].split(' кв.м')[0])
                except ValueError:
                    s_obsh = float(txt.split('площадью ')[-1].split(' кв.м')[0])

            return {
                "Тип": f'{txt[0]}К',
                "S общ": s_obsh,
                "S жил": '-',
                "S кухни": s_kuh,
                "Отд.": '-',
                "С/у": '-',
                "Балкон": balk,
                "Этаж": int(txt.split('-м этаже')[0][-1]),
                "№ объекта": int(txt.split('(№')[-1][:-1]),
                "ЖК, оч. и корп.": 'ЖК "Модерн"',
                "Продавец": 'Европейский стиль',
                "Район": soup.select_one('address').text,
                "Сдача": '-',
                "Цена 100%": int(
                    soup.select('div.TileSectionHead_Label__2llHF')[0].text.replace(' ', '').split('₽')[0]),
                "за м2": int(soup.select('div.TileSectionHead_Label__2llHF')[-1].text.replace(' ', '').split('₽')[0]),
                "Баз. цена": '-',
                "Вознаграж.": '',
            }
        except Exception as ex:
            asyncio.run(self.update_err(error="EuropeyStile " + str(ex)))
            logger.warning(f'''Invalid link EuropeyStile: {link}\nExeption: {ex}\n''')
            print(f'!!!!!   ERROR   !!!!!! MINI_LINK ({link})')

    def pars_all_data(self) -> None:
        try:
            logger.info('Start pars EuropeyStile')
            for link in self.all_links:
                logger.info(
                    f'EuropeyStile; Pars  -PAGE-  ({link}); {self.all_links.index(link) + 1} out of {len(self.all_links)}')
                response = requests.get(link)
                if response.status_code not in [200, 201, 202, 203, 204]:
                    logger.warning(f'EuropeyStile; Invalid URL status_code == {response.status_code}; URL ({link})')
                    continue
                soup = BeautifulSoup(response.text, 'lxml')
                try:
                    for item in soup.select_one('div.Tile_Grid__2SwpW.Tile_List__194LR').select('div.Tile_Tile__1zWP-'):
                        logger.info(
                            f'''EuropeyStile; Pars link ({f"https://европейскийстиль.рф{item.select_one('a').get('href')}"})''')
                        _data = self.pars_flat(f"https://европейскийстиль.рф{item.select_one('a').get('href')}")
                        if _data:
                            self.result_mass.append(_data)
                except AttributeError as ex:
                    asyncio.run(self.update_err(error="EuropeyStile; AttributeError;  -  " + str(ex)))
                    logger.warning(f'EuropeyStile; AttributeError link ({link})')
        except Exception as ex:
            self._fatal_error = True
            asyncio.run(self.update_err(error="EuropeyStile // Fatal ERROR  -  " + str(ex)))
            logger.error(f'Fatal ERROR EuropeyStile ->\n{ex}\n\n')


if __name__ == '__main__':
    per = EuropeyStileParser(
        exel=True
    )
    per.run()