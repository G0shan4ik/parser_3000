import asyncio

from loguru import logger
from bs4 import BeautifulSoup
import lxml

from p3000.parsers.base import BaseParserSelenium


class NmarketParser(BaseParserSelenium):
    def __init__(self, err_name = None, headless: bool = True, retry_count: int = 3, exel: bool = False, single: bool = False):
        super().__init__(
            start_url='https://auth.nmarket.pro/Account/Login',
            site_name='nmarket',
            headless=headless,
            retry_count=retry_count,
            exel=exel,
            err_name=err_name if err_name else ["single", 'Nmarket'],
            single=single
        )

        self.cnt: int = 0
        self.driver = None

        self.fl_cnt: int = -1
        self.iter_count: int = 0

        self.__cnt_glorax = 0

    @staticmethod
    def num(s) -> str | int | float:
        s = s.replace('\n', '').replace(' ', '')
        try:
            return int(s)
        except ValueError:
            try:
                return float(s.replace(',', '.'))
            except:
                return s

    def pars_all_data(self) -> None:
        try:
            #  <-- sign in -->
            logger.info('Nmarket; Started authorize')
            while self.fl_cnt == -1:
                try:
                    self.driver.get(self.start_url)
                    self.driver.sleep(3)
                    self.driver.type('input[type="tel"]', '9302025559', wait=10)
                    self.driver.get('https://auth.nmarket.pro/Account/PhoneLogin?phoneNumber=79302025559')
                    self.driver.sleep(2)
                    self.driver.type('input[type="password"]', '10061984аqA', wait=10)
                    self.driver.run_js("document.querySelector('button#login_phone_pass_click').click()")
                    self.driver.sleep(1)
                    self.driver.get('https://vld.nmarket.pro/search/apartmentgrid?isSmartLineMode=true')
                    self.driver.sleep(4)
                    #  <-- /sign in -->
                    self.driver.wait_for_element('div.search-result-counter', wait=10)
                    soup = BeautifulSoup(self.driver.page_html, 'lxml')
                    self.fl_cnt = int(soup.select_one('div.search-result-counter').text.split(' - ')[-1].replace('\xa0', ''))
                    if self.fl_cnt > 20000:
                        self.driver.reload()
                        self.driver.sleep(3)
                        continue
                except:
                    self.iter_count += 1
                    logger.warning(f'Nmarket; Authorise error; Start next iteration (iter count == {self.iter_count})')

            self.driver.reload()
            self.driver.sleep(3)
            self.driver.scroll()
            self.driver.scroll()
            self.driver.sleep(1)
            self.driver.scroll()
            self.driver.wait_for_element('div.pagination', wait=10)
            soup = BeautifulSoup(self.driver.page_html, 'lxml')
            # all_pages = int(soup.select_one('div.pagination.ng-star-inserted').select('div.ng-star-inserted')[-2].text)
            all_pages = int(soup.select_one('div.pagination').select('div')[-2].text)
            if self.fl_cnt == -1 or self.fl_cnt == 0:
                self.fl_cnt = int(soup.select_one('div.search-result-counter').text.split(' - ')[-1].replace('\xa0', ''))

            logger.info(f"Nmarket; ALL floor_count == {self.fl_cnt}")
            logger.info(f"Nmarket; ALL pages == {all_pages}")

            if all_pages > 7000:
                self._fatal_error = True
                logger.error(f"Nmarket; The site is not working property")

            for item in range(1, 777):
                try:
                    url = f'https://vld.nmarket.pro/search/apartmentgrid?isSmartLineMode=true&apartment.page={item}'
                    logger.info(f"Nmarket; Page №{item};  Url == {url}")
                    self.driver.get(url)
                    self.driver.sleep(3)
                    self.driver.scroll()
                    self.driver.scroll()
                    self.driver.scroll()
                    self.driver.scroll()
                    self.driver.sleep(1)
                    self.driver.scroll()
                    self.driver.wait_for_element('td.apartment-grid__table-td', wait=10)
                    self.driver.sleep(1)

                    soup = BeautifulSoup(self.driver.page_html, 'lxml')
                    dct = {}

                    for row in soup.select_one('tbody.apartment-grid__table-tbody').select('tr'):
                        ful_price = int(row.select_one('td:nth-child(16)').text.replace('\xa0', ''))
                        m_price = int(row.select_one('td:nth-child(17)').text.replace('\xa0', ''))
                        if 'Glorax' in row.select_one('td:nth-child(12)').text.strip():
                            ful_price = ful_price * 0.85
                            m_price = m_price * 0.85
                            logger.info('Nmarket; skip Glorax')
                            self.__cnt_glorax += 1
                            continue
                        dct = {
                            "Тип": row.select_one('td:nth-child(2)').text,
                            "S общ": self.num(row.select_one('td:nth-child(4)').text),
                            "S жил": self.num(row.select_one('td:nth-child(5)').text),
                            "S кухни": self.num(row.select_one('td:nth-child(6)').text),
                            "Отд.": row.select_one('td:nth-child(7)').text.strip(),
                            "С/у": self.num(row.select_one('td:nth-child(8)').text),
                            "Балкон": row.select_one('td:nth-child(9)').text.strip(),
                            "Этаж": int(row.select_one('td:nth-child(10)').text.strip().replace(' ', '').split('/')[0]),
                            "№ объекта": int(row.select_one('td:nth-child(11)').text.strip()),
                            "ЖК, оч. и корп.": row.select_one('td:nth-child(12)').text.strip(),
                            "Продавец": row.select_one('td:nth-child(13)').text.strip(),
                            "Район": row.select_one('td:nth-child(14)').text.strip(),
                            "Сдача": row.select_one('td:nth-child(15)').text.strip(),
                            "Цена 100%": ful_price,
                            "за м2": m_price,
                            "Баз. цена": int(row.select_one('td:nth-child(18)').text.replace('\xa0', '')),
                            "Вознаграж.": int(row.select_one('td:nth-child(19)').text.replace('\xa0', '')),
                        }
                        self.result_mass.append(dct)

                    if (len(self.result_mass) % item == 0 or
                            (all_pages == item and (len(self.result_mass) - len(dct)) % (all_pages - 1) == 0)):
                        logger.info(f"Nmarket; Page №{item}; Floor_count == {len(self.result_mass)}")
                    else: logger.warning(f"Nmarket; Page №{item}; Floor_count == {len(self.result_mass)}")

                except Exception as ex:
                    if self.fl_cnt == len(self.result_mass):
                        break
                    self.cnt += 1
                    logger.warning(f'Nmarket; Invalid link; Exception count№{self.cnt}; Page №{item}\n(ex -> {ex})\n')
                    if self.cnt == 4:
                        break

            self.floor_count = len(self.result_mass)
        except Exception as ex:
            self._fatal_error = True
            logger.error(f'Fatal ERROR Nmarket ->\n{ex}\n\n')

        logger.info(f'Nmarket; Glorax flats coutn == {self.__cnt_glorax}')

        self.floor_count = len(self.result_mass) + self.__cnt_glorax


if __name__ == '__main__':
    per = NmarketParser(
        exel=True,
        headless=False,
    )
    per.run()