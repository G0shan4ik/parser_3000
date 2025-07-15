import asyncio
from abc import ABC, abstractmethod
from typing import Awaitable

from botasaurus.browser import Driver, browser
from botasaurus.user_agent import UserAgent

import pandas as pd
from datetime import datetime

from loguru import logger

import aiohttp

from p3000.bott.helpers import FlagsManager, FlagKey



class BaseModel:
    def __init__(self, site_name: str, err_name: [FlagKey]):
        self.site_name: str = site_name
        self.err_name: [FlagKey] = err_name

    async def update_err(self, error: str) -> None:
        fl = FlagsManager()

        dct_err: dict = await fl.read_flag_value(
            key=self.err_name[0],
            subkey="errors"
        )
        dct_err = dct_err if dct_err else dict()

        if dct_err.get(self.err_name[0]):
            dct_err[self.err_name[0]].append([self.err_name[1], error])
        else: dct_err[self.err_name[0]] = [self.err_name[1], error]

        await fl.update_flag_value(
            key=self.err_name[0],
            subkey="errors",
            value=dct_err
        )

    def to_exel(self, mass: list[dict]) -> None:
        df = pd.DataFrame(mass)
        df.to_excel(f"all_exel/{datetime.now().date()}_{self.site_name}.xlsx")

        logger.success(f'{self.site_name.upper()}; <-- Success created file (name -> {self.site_name})')


class BaseParserSelenium(ABC, BaseModel):
    def __init__(self, start_url: str|list[str], site_name: str, err_name: [FlagKey], headless: bool, retry_count: int, exel: bool):
        super().__init__(
            site_name=site_name,
            err_name=err_name
        )
        self.start_url: str|list[str] = start_url
        self.__headless: bool = headless
        self.retry_count: int = retry_count
        self.exel = exel

        self.result_mass: list[dict] = []
        self.driver: Driver

        self.floor_count: int = 0

        self._fatal_error: bool = False

    @abstractmethod
    def pars_all_data(self) -> None:
        ...

    def run(self) -> list[list[dict] | int]:
        @browser(
            user_agent=UserAgent.user_agent_98,
            add_arguments=['--disable-dev-shm-usage', '--no-sandbox'],
            max_retry=self.retry_count,
            headless=self.__headless
        )
        def run_parser(driver: Driver, data: str) -> None:
            self.driver = driver
            self.driver.get(data)
            logger.success(f'{self.site_name.upper()}; START pars {self.site_name.upper()} --->')

            self.pars_all_data()
            if not self._fatal_error:
                logger.success(f'{self.site_name.upper()}; FINISH pars; All_Items == {self.floor_count} --->')
            else: logger.warning(f'{self.site_name.upper()}; FINISH pars; All_Items == {self.floor_count} --->')

            if self.exel and not self._fatal_error:
                self.to_exel(mass=self.result_mass)

        run_parser(data="https://www.google.com/")
        return [self.result_mass, self.floor_count]


class BaseParserRequests(ABC, BaseModel):
    def __init__(self, all_links: list[str] | str, site_name: str, err_name: [FlagKey], exel: bool):
        super().__init__(
            site_name=site_name,
            err_name=err_name
        )

        self.all_links: list[str] | str = all_links
        self.site_name: str = site_name
        self.exel: bool = exel

        self.result_mass: list[dict] = []
        self.floor_count: int = 0

        self._fatal_error: bool = False

    @abstractmethod
    def pars_all_data(self) -> None:
        ...

    def run(self) -> list[list[dict] | int]:
        logger.success(f'{self.site_name.upper()}; START pars {self.site_name.upper()} --->')

        self.pars_all_data()

        if not self._fatal_error:
            logger.success(f'{self.site_name.upper()}; FINISH pars; All_Items == {self.floor_count} --->')
        else: logger.warning(f'{self.site_name.upper()}; FINISH pars; All_Items == {self.floor_count} --->')

        if self.exel and not self._fatal_error:
            self.to_exel(mass=self.result_mass)

        return [self.result_mass, self.floor_count]


class BaseAsyncParserRequests(ABC, BaseModel):
    def __init__(self, all_links: list[str] | str, site_name: str, err_name: [FlagKey], exel: bool):
        super().__init__(
            site_name=site_name,
            err_name=err_name
        )

        self.all_links: list[str] | str = all_links
        self.exel = exel

        self.site_name: str = site_name

        self.result_mass: list[dict] = []
        self.session: aiohttp.ClientSession

        self.floor_count: int = 0

        self._fatal_error: bool = False

    @abstractmethod
    async def init_session(self) -> None:
        ...

    @abstractmethod
    async def close_session(self) -> None:
        ...

    @abstractmethod
    async def pars_all_data(self, url: str|None) -> None:
        ...

    async def run(self) -> list[list[dict] | int]:
        logger.success(f'{self.site_name.upper()}; START pars {self.site_name.upper()} --->')

        await self.init_session()
        logger.info(f"{self.site_name.upper()}; INIT Async Session")

        processes: [Awaitable] = []
        for url in self.all_links:
            processes.append(self.pars_all_data(url=url))

        for process in self.chunks(processes, 5):
            await asyncio.gather(*process)

        if not self._fatal_error:
            logger.success(f'{self.site_name.upper()}; FINISH pars; All_Items == {self.floor_count} --->')
        else: logger.warning(f'{self.site_name.upper()}; FINISH pars; All_Items == {self.floor_count} --->')

        await self.close_session()
        logger.info(f"{self.site_name.upper()}; CLOSE Async Session")

        if self.exel and not self._fatal_error:
            self.to_exel(mass=self.result_mass)

        return [self.result_mass, self.floor_count]

    @staticmethod
    def chunks(lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]