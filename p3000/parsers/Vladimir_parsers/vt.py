from pprint import pprint
from typing import Optional

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
            # 'Суздаль',
            'Ковров',
            # 'Владимир',
        ]

    @staticmethod
    def change_gk_name(name: str) -> str:
        try:
            #
            if 'парадный' in name.lower():
                return ''
            elif 'cвобода' in name.lower():
                return ''
            elif 'квартал нового тысячелетия 1 оч. корп' in name.lower():
                return 'Квартал нового тысячелетия 1 оч. корп.1'
            elif not name:
                return ''

            elif 'восток, к1 добросельская д.178' in name.lower():
                return 'Восток 1 оч. корп. 1'
            elif 'восток, к2 добросельская д.180' in name.lower():
                return 'Восток 2 оч. корп. 2'
            #

            # Ковров
            if 'фамилия' in name.lower():
                return f'Фамилия {name[-1]} оч. корп. {name[-1]}'
            elif 'туманова' in name:
                return 'Дом на Туманова'
            elif 'аурум' in name.lower():
                return 'Аурум'
            elif 'грани' in name:
                return 'ЖК Грани'
            elif 'гармония' in name:
                return 'ЖК Гармония'
            elif 'черемушки' in name:
                return f'ЖК Черёмушки'

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
            # /Ковров


            # Суздаль
            elif 'мечта' in name.lower():
                return 'Мечта'
            elif 'всполье' in name:
                return f'Всполье 1 оч. корп. {name[-1]}'.strip()
            # /Суздаль


            # Владимир
            elif '"горького"' in name:
                return f'Горького 1 оч. корп. {name.split(",")[0][-1]}'
            elif 'Загородный парк' in name:
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
                if ', к' in name:
                    return f'Отражение 1 оч. корп. {name.split(", к")[1].split()[0]}'

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
                res = name.replace(',', ' 1 оч.').replace('новаторов', 'Новаторов').replace('корп.', 'корп. ').replace('  ', ' ').strip()
                _korp = res[-1]
                return f"{res.split(' корп. ')[0]} корп. {_korp}"
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
            elif 'фестивальный' in name.lower():
                mass_name = name.replace('Фестивальный', 'ЖК Фестивальный').split(', ')
                return f'{mass_name[0]} {mass_name[1]} оч. корп. {mass_name[-1]}'

            elif 'сталинградский бульвар' in name:
                return ''
            elif 'Glorax' in name:
                return ''
            elif 'мичурина' in name:
                return ''
            elif 'Таунхаусы' in name:
                return ''

            # elif 'Эталон' in name:
            #     return ''
            # elif 'володарского' in name:
            #     return ''
            # elif 'Новопарк' in name:
            #     return ''
            # elif 'Комьюнити' in name:
            #     return ""
            # elif 'Микрорайон Славный' in name or 'verizino life' in name:
            #     return ''
            # elif 'восход в коврове' in name.lower():
            #     return ''
            # /Владимир

            return name
        except Exception as ex:
            logger.warning(f'VT; !!! Change name err ({name}) !!! \n{ex} ')

    def parse_flat_info(self, sp) -> Optional[dict]:
        info_gk = ''
        try: #
            info_gk = sp.select_one('app-cdk-cell.app-cdk-cell.cdk-column-new-builder.app-cdk-column-new-builder.resizing.ng-star-inserted > app-eav-cell').get('title').strip().capitalize()
            print(info_gk)
            gk_name = self.change_gk_name(info_gk)
            # print(info_gk[0].strip().capitalize(), '  <--->  ', gk_name)

            if gk_name == '':
                logger.warning(f'VT; GK_Name dont exists (name #{info_gk}#)')
                return {}

            price_full = int(sp.select_one('app-cdk-cell.app-cdk-cell.cdk-column-price.app-cdk-column-price.resizing.ng-star-inserted > app-eav-cell').get('title').replace(' ', '').split(',')[0])
            price_m = int(sp.select_one('app-cdk-cell.app-cdk-cell.cdk-column-price_quad_meter.app-cdk-column-price_quad_meter.resizing.ng-star-inserted > app-eav-cell').get('title').replace(' ', '').split(',')[0])

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
            tp = ''
            try:
                tp = sp.select_one('app-cdk-cell.app-cdk-cell.cdk-column-rooms.app-cdk-column-rooms.resizing.ng-star-inserted > app-eav-cell').get('title')
            except:
                ...
            if tp:
                dct['Тип'] = 'СТ' if 'тудия' in tp else f'{tp}К'
                if dct['Тип'] == '5К':
                    return None

            if dct['Тип'] == '-':
                logger.warning(f'VT; Skip flat (dont such type flat)')
                return {}
            # --- Этаж ---
            m_floor = None
            try:
                m_floor = sp.select_one('app-cdk-cell.app-cdk-cell.cdk-column-floor.app-cdk-column-floor.resizing.ng-star-inserted > app-eav-cell').get('title')
            except:
                ...
            if m_floor:
                dct['Этаж'] = int(m_floor)

            # --- Площади ---
            # Формат 40.53/11.6/16.4 м²
            total, living, kitchen = 0, 0, 0
            try:
                total = sp.select_one(
                    'app-cdk-cell.app-cdk-cell.cdk-column-total_area.app-cdk-column-total_area.resizing.ng-star-inserted > app-eav-cell').get('title').replace(',', '.')
            except:
                ...
            try:
                living = sp.select_one(
                    'app-cdk-cell.app-cdk-cell.cdk-column-living_area.app-cdk-column-living_area.resizing.ng-star-inserted > app-eav-cell').get('title').replace(',', '.')
            except:
                ...
            try:
                kitchen = sp.select_one(
                    'app-cdk-cell.app-cdk-cell.cdk-column-sq_kitchen.app-cdk-column-sq_kitchen.resizing.ng-star-inserted > app-eav-cell').get('title').replace(',', '.')
            except:
                ...

            dct['S общ'] = float(total) if total else '-'
            dct['S жил'] = float(living) if living else '-'
            dct['S кухни'] = float(kitchen) if kitchen else '-'
            # --- Год сдачи ---
            m_year = ''
            try:
                m_year = sp.select_one('app-cdk-cell.app-cdk-cell.cdk-column-ddu_date.app-cdk-column-ddu_date.resizing.ng-star-inserted > app-eav-cell').get('title')
            except:
                ...
            if m_year:
                dct['Сдача'] = int(m_year.split('.')[-1])


            return dct
        except Exception as ex:
            logger.warning(f'VT; err text {info_gk}; EX: {ex}')

    def auth_by_name(self, name: str, _part: int):
        try:
            if _part == 0:
                self.driver.wait_for_element('button.chip-button.nowrap.button-only', wait=10)
                self.driver.run_js(
                    '''
    const buttons = document.querySelectorAll('button[aria-describedby="cdk-describedby-message-ng-1-3"]');
    buttons[1]?.click();'''
                )
                self.driver.sleep(1)
                self.driver.run_js('''document.querySelector('div.map.flex.align-center.gap-6.justify-between.pointer > app-toggle > div').click()''')
                self.driver.sleep(2)
                self.driver.run_js("""
                    const items = document.querySelectorAll('div.item-container.selectable.check-end');
                    items[items.length - 1]?.click();
                """)
                self.driver.sleep(1)
                self.driver.run_js("document.querySelector('button.chip-button.nowrap.button-only').click()")
                print('---- Settings')
                self.driver.sleep(2)
            else:
                self.driver.run_js(
                    '''
const p = document.querySelectorAll('button.chip-button.nowrap.button-only')
p[0]?.click()'''
                )
            self.driver.run_js('''[...document.querySelectorAll('div.mat-mdc-tooltip-trigger.primary-button.flex.align-center.justify-center.gap-4.medium.neutral')].find(el => el.textContent.includes('Сбросить'))?.click();''')
            #[...document.querySelectorAll('div.mat-mdc-tooltip-trigger.primary-button.flex.align-center.justify-center.gap-4.medium.neutral')].find(el => el.textContent.includes('Сбросить'))?.click();
            print('---- Resset settings')
            self.driver.sleep(2)

            # self.driver.run_js('''[...document.querySelectorAll('span')].find(el => el.textContent.includes('Квартира во вторичке'))?.click();''')
            # print('---- delete filter')
            # self.driver.sleep(2)

            self.driver.run_js('''[...document.querySelectorAll('span')].find(el => el.textContent.includes('Не выбран'))?.click();''')
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
            self.driver.run_js('''document.querySelector('button.app-flat-button.app-button-base.green.medium.searchButton').click()''',)
            print(f'---- Select view')
            self.driver.sleep(3)
            self.driver.run_js('''document.querySelector('div.footer.flex.align-center.justify-between > div > button:last-child').click()''')
            print(f'---- Select commit')
            self.driver.sleep(4)
        except Exception as ex:
            logger.warning(f"VT; Error auth name (NAME == {name})\n {ex}")

    def pars_data(self):
        _part = 0
        for name in self.pars_names:
            self.driver.get('https://is.vt24.ru/object-realty-new')
            self.driver.sleep(4)
            try:

                # self.driver.prompt()

                self.auth_by_name(name=name, _part=_part)
                _part += 1

                self.driver.sleep(4)


                self.driver.wait_for_element('div.app-cdk-header-row', wait=10)
                self.driver.sleep(1)

                logger.info(f"VT; ALL Items == {self.floor_count}")
                try:
                    for num in range(150):
                        logger.info(f'VT; Iteration number {num}')
                        self.driver.run_js(
                            "document.querySelector('div.load-more-button-component.border-radius-4.flex.justify-center.p-10').click()")
                        self.driver.sleep(2)
                except:
                    ...

                logger.success('VT; Success pars all cards link')

                self.driver.sleep(4)
                soup = BeautifulSoup(self.driver.page_html, 'lxml')

                cnt_real, cnt_good = 0, 0
                for item in soup.select('app-cdk-row'):
                    try:
                        cnt_real += 1

                        if not item.select_one("app-cdk-cell.app-cdk-cell.cdk-column-is_module_sn_24.app-cdk-column-is_module_sn_24.resizing.ng-star-inserted").text:
                            logger.info(f"ZASTROISHIK SKIP")
                            continue

                        dct = self.parse_flat_info(item)
                        if dct:
                            cnt_good += 1
                            logger.info(f'VT; Pars Flat --- {dct["ЖК, оч. и корп."]}')
                            self.result_mass.append(
                                dct
                            )
                            continue
                    except :
                        logger.info(f"--- SKIP; {name}")

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
                try:
                    self.driver.wait_for_element('input#email', wait=10)
                    self.driver.type('input#email', 'partners@stroimgroup.ru', wait=10)
                except:
                    try:
                        self.driver.reload()
                        self.driver.sleep(1)
                        self.driver.wait_for_element('input#email', wait=10)
                        self.driver.type('input#email', 'partners@stroimgroup.ru', wait=10)
                    except:
                        self.driver.reload()
                        self.driver.sleep(1)
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