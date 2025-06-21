import asyncio
from abc import ABC, abstractmethod
from contextlib import closing
from typing import Awaitable

from botasaurus.browser import Driver, browser
from botasaurus.user_agent import UserAgent

import pandas as pd
from datetime import datetime

from loguru import logger

import aiohttp


class BaseParserSelenium(ABC):
    def __init__(self, start_url: str|list[str], site_name: str, headless: bool, retry_count: int, exel: bool):
        self.start_url: str|list[str] = start_url
        self.__headless: bool = headless
        self.retry_count: int = retry_count
        self.exel = exel

        self.site_name: str = site_name

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
            logger.success(f'START pars {self.site_name.upper()} --->')

            self.pars_all_data()
            if not self._fatal_error:
                logger.success(f'FINISH pars {self.site_name.upper()} --->')
            else: logger.warning(f'FINISH pars {self.site_name.upper()} --->')

            if self.exel:
                self.to_exel(mass=self.result_mass)

        run_parser(data="https://www.google.com/")
        return [self.result_mass, self.floor_count]

    def to_exel(self, mass: list[dict]) -> None:
        df = pd.DataFrame(mass)
        df.to_excel(f"all_exel/{datetime.now().date()}_{self.site_name}.xlsx")

        logger.success(f'<-- Success created file (name -> {self.site_name})')


class BaseParserRequests(ABC):
    def __init__(self, all_links: list[str] | str, site_name: str, exel: bool):
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
        logger.success(f'START pars {self.site_name.upper()} --->')

        self.pars_all_data()

        if not self._fatal_error:
            logger.success(f'FINISH pars {self.site_name.upper()} --->')
        else: logger.warning(f'FINISH pars {self.site_name.upper()} --->')

        if self.exel:
            self.to_exel(mass=self.result_mass)

        return [self.result_mass, self.floor_count]

    def to_exel(self, mass: list[dict]) -> None:
        df = pd.DataFrame(mass)
        df.to_excel(f"all_exel/{datetime.now().date()}_{self.site_name}.xlsx")

        logger.success(f'<-- Success created file (name -> {self.site_name})')


class BaseAsyncParserRequests(ABC):
    def __init__(self, all_links: list[str] | str, site_name: str, exel: bool):
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
        logger.success(f'START pars {self.site_name.upper()} --->')

        await self.init_session()
        logger.info(f"INIT Async Session for {self.site_name}")

        processes: [Awaitable] = []
        for url in self.all_links:
            processes.append(self.pars_all_data(url=url))

        for process in self.chunks(processes, 5):
            await asyncio.gather(*process)

        if not self._fatal_error:
            logger.success(f'FINISH pars {self.site_name.upper()} --->')
        else: logger.warning(f'FINISH pars {self.site_name.upper()} --->')

        await self.close_session()
        logger.info(f"CLOSE Async Session for {self.site_name}")

        if self.exel:
            self.to_exel(mass=self.result_mass)

        return [self.result_mass, self.floor_count]

    def to_exel(self, mass: list[dict]) -> None:
        df = pd.DataFrame(mass)
        df.to_excel(f"all_exel/{datetime.now().date()}_{self.site_name}.xlsx")

        logger.success(f'<-- Success created file (name -> {self.site_name})')

    @staticmethod
    def chunks(lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]