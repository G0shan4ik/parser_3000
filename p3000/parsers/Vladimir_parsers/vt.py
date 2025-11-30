from loguru import logger
from bs4 import BeautifulSoup
import lxml

import re

from p3000.parsers.base import BaseParserSelenium


class VTParser(BaseParserSelenium):
    def __init__(self, err_name = None, headless: bool = True, retry_count: int = 3, exel: bool = False, single: bool = False):
        super().__init__(
            start_url='https://is.vt24.ru/cabinet',
            site_name='vt',
            headless=headless,
            retry_count=retry_count,
            exel=exel,
            err_name=err_name if err_name else ["single", 'VT'],
            single=single
        )
        self.cnt: int = 0
        self.driver = None

        self.iter_count: int = 0

        self.pars_links: list[str] = []

        self.pars_names: list[str] = [
            # 'Владимир'
            'Суздаль',
            'Ковров',
        ]

    @staticmethod
    def change_gk_name(name: str) -> str:
        try:
            # Ковров
            if 'фамилия' in name.lower():
                return f'Фамилия {name[-1]} оч. корп. {name[-1]}'
            elif 'туманова' in name:
                return 'Дом на Туманова'
            elif 'аурум' in name.lower():
                return 'Аурум'
            elif 'триумфальный' in name:
                return ''
            elif 'чайковский' in name:
                return ''
            elif 'маршал' in name:
                return ''
            elif 'держава' in name:
                return ''
            elif 'свобода" в микрорайоне' in name:
                return ''
            elif 'грани' in name:
                return ''

            elif 'гармония' in name:
                return ''
            elif 'черемушки' in name:
                return ''
            # /Ковров


            # Суздаль
            elif 'нового тысячелетия' in name:
                return f'Квартал нового тысячелетия 1 оч. корп. {name[-1]}'.strip()
            elif 'Мечта' in name:
                return 'Мечта'
            elif 'всполье' in name:
                return f'Всполье 1 оч. корп. {name[-1]}'.strip()
            # /Суздаль


            # Владимир
            elif '"горького"' in name:
                return f'Горького 1 оч. корп. {name.split(",")[0][-1]}'
            elif 'Загородный парк' in name:
                # if '/' in name:
                #     return 'Загородный парк 1 оч. корп. 5/1'
                return f'Загородный парк 1 оч. корп. {name.split("корп.")[1].split("(")[0].strip()}'
            elif 'Дом на мира' in name:
                return f'Дом на Мира {name.split(", ")[1]}'
            elif 'веризинский' in name:
                return f'Веризинский д. 5 2 оч. корп. {name.split(",")[-2][-1]}'.replace(', -', '').strip()
            elif 'Заречье ' in name:
                if 'дом' in name:
                    return ''
                korp = name[-1]
                korp_2 = name.split(', ')[1][0]
                res_name = f'Заречье Парк {6 if korp_2 in ["4", "5"] else 5} оч. корп. {korp_2} корпус {korp}'
                if '6 оч.' not in res_name:
                    return res_name.replace('корпус', 'корп')
                return res_name
            elif 'на манежном' in name:
                return f'Клубный дом на Манежном'
            elif 'Жуковского' in name:
                return f'Дом на улице Жуковского'
            elif 'Жилой дом на лакина' in name:
                return f'Жилой дом на Лакина {name.split(", ")[0].split()[-1].replace("б", "Б")}'
            elif 'Отражение, ' in name:
                if 'Отражение, корпус 1' in name:
                    return ''
                if 'корп.' in name:
                    return f'Отражение 1 оч. корп. {name.split("корп.")[1].split()[0]}'

                return f'Отражение 1 оч. корп. {name.split("корпус ")[1].split()[0]}'
            elif 'Гвардейский, 4 по' in name or '/' in name:
                s = 'Гвардейский 2 оч. корп. '
                if '/' in name:
                    res = s + name.split('д.')[1].split()[0].replace('/', '.').split('(')[0].replace(' по гп', '').replace('  ', ' ').strip()
                    return res.replace('  ', ' ') if 'Гвардейский 2 оч. корп. 4' not in res else f'{res} по ГП'.replace('  ', ' ').strip()
                res = s + name.split(', ')[1].split('(')[0].replace(' по гп', '').replace('  ', ' ').strip()
                return res.replace('  ', ' ') if 'Гвардейский 2 оч. корп. 4' not in res else f'{res} по ГП'.replace('  ', ' ').strip()
            elif 'Содышка' in name:
                if 'Содышка, дом 133б' in name or 'Содышка, корпус 4' in name:
                    return ''
                return name.split(',')[0]
            elif 'Uno' in name:
                return name.replace('Uno', 'UNO').replace('.', '')
            elif 'Дом на б.' in name:
                return 'Дом на Большой Нижегородской'
            elif 'Восток, корп.1' in name:
                return 'Восток 1 оч. корп. 1'
            elif 'Восток, корп.2' in name:
                return 'Восток 2 оч. корп. 2'
            elif 'Соколиный' in name:
                return f'Соколиный парк 1 оч. корп. {name[-1]}'
            elif 'Квартал новаторов, ' in name:
                return name.replace(',', ' 1 оч.').replace('новаторов', 'Новаторов').replace('корп.', 'корп. ').replace('  ', ' ').strip()
            elif '"смоленская ' in name:
                if '3а' in name:
                    return f'Смоленская 3А'
                else: return f'ЖК Смоленская 3Б'
            elif 'Гвардейский' in name:
                return f"Гвардейский 1 оч. корп. {name.split(', ')[1].split('(')[0]}".replace(' по гп', '').strip()
            elif 'на ул.чайковского' in name:
                korp = name[-1]
                return f'ЖК на ул.Чайковского, корп {korp}'
            elif 'мельничном' in name:
                return f'Дом на Мельничном проезде,{name.split(",")[1]}'
            elif 'Дом на батурина' in name:
                return f'Дом на Батурина,{name.split(",")[1]}'

            elif 'Таунхаусы' in name:
                return ''
            elif 'Glorax' in name:
                return ''
            elif 'володарского' in name:
                return ''
            elif 'Новопарк' in name:
                return ''
            elif 'Комьюнити' in name:
                return ""
            elif 'сталинградский бульвар, ' in name:
                # return f'''Сталинградский бульвар, {name.split('"')[1][-1]}'''
                return ''

            elif 'Микрорайон Славный' in name or 'verizino life' in name:
                return ''
            elif 'восход в коврове' in name.lower():
                return ''
            # /Владимир


            return name
        except Exception as ex:
            logger.warning(f'VT; !!! Change name err ({name}) !!! \n{ex} ')

    def parse_flat_info(self, text: str, info_gk: [str], prices: [str]) -> dict:
        try:
            gk_name = self.change_gk_name(info_gk[0].strip().capitalize())
            # print(info_gk[0].strip().capitalize(), '  <--->  ', gk_name)
            if gk_name == '':
                logger.warning(f'VT; GK_Name dont exists (name #{info_gk[0].strip().capitalize()}#)')
                return {}

            price_full = int(prices[0].replace(' ₽', '').replace(' ', ''))
            price_m = int(prices[-1].replace('₽/м²', '').replace(' ', ''))
            dct = {
                'Тип': '-',
                'S общ': round(float(price_full/price_m), 1),
                'S жил': '-',
                'S кухни': '-',
                'Отд.': '-',
                'С/у': '-',
                'Балкон': '-',
                'Этаж': '-',
                '№ объекта': '-',
                'ЖК, оч. и корп.': gk_name,
                'Продавец': '-',
                'Район': '-',
                'Сдача': '-',
                'Цена 100%': price_full,
                'за м2': price_m,
                'Баз. цена': '-',
                'Вознаграж.': ''
            }

            # --- Тип квартиры ---
            # Студия
            if re.search(r'\bстудия\b', text, re.I):
                dct['Тип'] = 'СТ'
            # N-комнатная
            else:
                m_rooms = re.search(r'(\d+)[-– ]*комн', text, re.I)
                if m_rooms:
                    dct['Тип'] = f"{m_rooms.group(1)}К"

            # --- Этаж ---
            m_floor = re.search(r'(\d+)\s*/\s*\d+\s*эт', text, re.I)
            if m_floor:
                dct['Этаж'] = int(m_floor.group(1))

            # --- Площади ---
            # Формат 40.53/11.6/16.4 м²
            m_area_full = re.search(r'([\d,.]+)/([\d,.]+)/([\d,.]+)\s*м²', text)
            if m_area_full:
                total, living, kitchen = m_area_full.groups()
                # dct['S общ'] = float(total.replace(',', '.'))
                dct['S жил'] = float(living.replace(',', '.'))
                dct['S кухни'] = float(kitchen.replace(',', '.'))
            # else:
            #     # Формат только 40.53 м²
            #     m_area_simple = re.search(r'([\d,.]+)\s*м²', text)
            #     if m_area_simple:
            #         dct['S общ'] = round(float(, 1))

            # --- Год сдачи ---
            m_year = re.search(r'(\d{4})\s*г', text)
            if m_year:
                dct['Сдача'] = int(m_year.group(1))
            if dct['Тип'] == '-':
                logger.warning(f'VT; Skip flat (dont such type flat)')
                return {}
            return dct
        except Exception as ex:
            logger.warning(f'VT; err text == {text}; info_gk == {info_gk}; prices == {prices};\n {ex}')

    def auth_by_name(self, name: str):
        try:
            self.driver.wait_for_element('button.chip-button.nowrap.button-only', wait=10)
            self.driver.run_js("document.querySelector('button.chip-button.nowrap.button-only').click()")
            print('---- Settings')
            self.driver.sleep(2)
            self.driver.run_js('''[...document.querySelectorAll('span.app-button-wrapper')].find(el => el.textContent.includes('Сбросить'))?.click();''')
            print('---- Resset settings')
            self.driver.sleep(2)
            self.driver.run_js('''[...document.querySelectorAll('span')].find(el => el.textContent.includes('Квартира во вторичке, Квартира в новостройке'))?.click();''')
            print('---- Open burger')
            self.driver.sleep(2)
            self.driver.run_js("document.querySelector('span.app-option-text').click()")
            print('---- delete filter')
            self.driver.sleep(2)
            self.driver.run_js('''document.querySelector('button.location-switcher.app-stroked-button.app-button-base.medium.light-gray').click()''')
            print('---- Go into country')
            self.driver.sleep(3)
            self.driver.run_js('''[...document.querySelectorAll('div.areas__item.ng-star-inserted')].find(el => el.textContent.includes('Россия'))?.click();''')
            print('---- Select Russia')
            self.driver.sleep(3)
            self.driver.run_js(
                '''[...document.querySelectorAll('div.areas__item.ng-star-inserted')].find(el => el.textContent.includes('Владимирская'))?.click();''')
            print('---- Select Vladimirskaya')

            query = '''[...document.querySelectorAll('div.areas__item')].find(el => el.textContent.includes('Владимир'))?.click();'''

            if name == 'Ковров':
                query = "[...document.querySelectorAll('div.areas__item.ng-star-inserted')].find(el => el.textContent.includes('Ковров'))?.click();"
            elif name == 'Суздаль':
                query = '''[...document.querySelectorAll('div.areas__item.ng-star-inserted')].find(el => el.textContent.includes('Суздаль'))?.click();'''

            self.driver.sleep(3)
            self.driver.run_js(query)
            print(f'---- SELECT NAME == {name}')
            self.driver.sleep(3)
            self.driver.run_js('''[...document.querySelectorAll('span.app-button-wrapper')].find(el => el.textContent.includes('Показать'))?.click();''',)
            print(f'---- Select view')
            self.driver.sleep(3)
            self.driver.run_js('''document.querySelector('button.app-flat-button.app-button-base.medium.green.ng-star-inserted').click()''')
            print(f'---- Select commit')
            self.driver.sleep(4)
        except Exception as ex:
            logger.warning(f"VT; Error auth name (NAME == {name})\n {ex}")

    def pars_data(self):
        self.driver.get('https://is.vt24.ru/object-realty-new')
        self.driver.sleep(4)
        for name in self.pars_names:
            try:
                self.auth_by_name(name=name)
                self.driver.sleep(4)

                self.driver.wait_for_element('div.relation-card-wrapper', wait=10)
                self.driver.sleep(1)
                # soup = BeautifulSoup(self.driver.page_html, 'lxml')
                # self.floor_count = int(soup.select_one('div.objects-count').text.split()[0])
                logger.info(f"VT; ALL Items == {self.floor_count}")
                try:
                    while True:
                        for num in range(77777):
                            logger.info(f'VT; Iteration number {num}')
                            self.driver.run_js(
                                "document.querySelector('div.load-more-button-component.border-radius-4.flex.justify-center.p-10').click()")
                            self.driver.sleep(2)
                            # break
                        # break
                except:
                    ...

                logger.success('VT; Success pars all cards link')

                self.driver.sleep(4)
                soup = BeautifulSoup(self.driver.page_html, 'lxml')
                # with open(f'a.html', 'w') as file:
                #     file.write(str(soup))
                cnt_real, cnt_good = 0, 0
                for item in soup.select_one('div.container-search-box').select('relation-card-wrapper'):
                    try:
                        cnt_real += 1
                        dct = self.parse_flat_info(
                            text=item.select_one('span.mr-4').text,
                            info_gk=[
                                item.select_one('a.nb-title.font-size-12.line-height-16.string-truncate.ng-star-inserted').text,
                            ],
                            prices=[
                                item.select_one('span.font-size-16.font-weight-600.line-height-24.string-truncate').text,
                                item.select_one('span.secondary-color.font-size-11.line-height-16').text
                            ],
                        )
                        if dct:
                            cnt_good += 1
                            logger.info(f'VT; Pars Flat --- {dct["ЖК, оч. и корп."]}')
                            self.result_mass.append(
                                dct
                            )
                            continue
                        logger.info(f"https://is.vt24.ru/{item.select('a')[-1].get('href')}")
                    except :
                        logger.info(f"--- SKIP; https://is.vt24.ru/{item.select('a')[-1].get('href')}")

                # self.pars_links = [f'https://is.vt24.ru{item.get("href")}' for item in soup.select_one('div.container-search-box').select('a') if 'object-realty-new' in item.get("href")]
                # for link in self.pars_links:
                #     try:
                #         self.result_mass.append(self.pars_card(link))
                #     except Exception as ex:
                #         logger.warning(f'VT; Error pars card (link {link});\nException: {ex}\n\n')
                logger.success(f'VT; {name}: cnt_real == {cnt_real}; cnt_good == {cnt_good}')
            except Exception as ex:
                logger.error(f"VT; Error pars link (LINK == {name})\n {ex}")

    def pars_all_data(self) -> None:
        try:
            logger.info('VT; Started authorize')
            try:
                self.driver.get(self.start_url)
                self.driver.sleep(3)
                self.driver.wait_for_element('input#email', wait=10)
                self.driver.type('input#email', 'partners@stroimgroup.ru', wait=10)
                self.driver.sleep(2)
                self.driver.wait_for_element('input#password', wait=10)
                self.driver.type('input#password', 'Roma200607', wait=10)
                self.driver.run_js("document.querySelector('button.button-login__btn.app-flat-button.app-button-base.medium.blue').click()")
                self.driver.sleep(4)
            except Exception as ex:
                self.iter_count += 1
                logger.warning(f"VT; Authorise error; Start next iteration (iter count == {self.iter_count})\n {ex}")
                #  <-- /sign in -->

            self.pars_data()
            self.floor_count = len(self.result_mass)
        except Exception as ex:
            self._fatal_error = True
            logger.error(f'Fatal ERROR VT ->\n{ex}\n\n')

        logger.info(f'VY; VT flats count == {self.floor_count}')


if __name__ == '__main__':
    per = VTParser(
        exel=True,
        headless=False,
    )
    per.run()