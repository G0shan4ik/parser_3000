import inspect

import pandas as pd
from loguru import logger
from datetime import datetime

import asyncio
from concurrent.futures import ThreadPoolExecutor

from typing import Union, Any, Type, Tuple

from .Vladimir_parsers import vladimir_sk, nmarket, legenda, aviator, glorax


ParserInitDef = Union[
    Any,
    Tuple[Type, list, dict]
]


class BaseManager:
    def __init__(self, module_name: str, batch_size: int = 4):
        self.module_name = module_name
        self.batch_size = batch_size

    def to_exel(self, mass: list[dict]) -> str:
        df = pd.DataFrame(mass)
        df.to_excel(f"all_exel/{datetime.now().date()}_{self.module_name}.xlsx")

        logger.success(f'<-- Success created MODULE_file (name -> {self.module_name})')

        return f"all_exel/{datetime.now().date()}_{self.module_name}.xlsx"

    @staticmethod
    def chunks(lst, n):
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    async def __run_all_parsers(self, parser_definitions):
        loop = asyncio.get_running_loop()
        self.executor = getattr(self, "executor", ThreadPoolExecutor())

        results: list = []

        for batch in self.chunks(parser_definitions, self.batch_size):
            try:
                tasks = []

                for item in batch:
                    if isinstance(item, tuple) and len(item) == 3:
                        klass, args, kwargs = item
                        parser = klass(*args, **kwargs)
                    else:
                        parser = item

                    run_method = getattr(parser, 'run', None)
                    if not run_method:
                        continue

                    if inspect.iscoroutinefunction(run_method):
                        tasks.append(run_method())
                    else:
                        tasks.append(loop.run_in_executor(
                            self.executor,
                            lambda meth=run_method: meth(),
                            )
                        )

                raw_results = await asyncio.gather(*tasks)

                for result in raw_results:

                    if isinstance(result, list) and isinstance(result[0], list):
                        results.extend(result[0])
                    elif isinstance(result, list):
                        results.extend(result)
                    elif isinstance(result, dict):
                        results.append(result)
            except Exception as ex:
                logger.error(f'Fatal ERROR Vladimir_MANAGER ->\n{ex}\n\n')

        return results



class IvanovoManager(BaseManager):
    def __init__(self, batch_size: int = 3):
        super().__init__(
            module_name='Ivanovo',
            batch_size=batch_size
        )

    async def run_ivanovo_module(self):
        parsers = [
            # (vladimir_sk.VladimirParser, (), {'err_name': 'vladimir'}),
            # (legenda.LegendaParser, (), {'err_name': 'vladimir'}),
            # (aviator.AviatorParser, (), {'err_name': 'vladimir'}),
            # (nmarket.NmarketParser, (), {'headless': False, 'err_name': 'vladimir'}),
        ]

        results: list[dict] = await self.__run_all_parsers(parsers)

        return self.to_exel(results)

class VladimirManager(BaseManager):
    def __init__(self, batch_size: int = 4):
        super().__init__(
            module_name='Vladimir',
            batch_size=batch_size
        )

    async def run_vladimir_module(self) -> str:
        parsers = [
            (vladimir_sk.VladimirParser, (), {'err_name': ['vladimir', 'VladimirSK']}),
            (legenda.LegendaParser, (), {'err_name': ['vladimir', 'Legenda']}),
            (aviator.AviatorParser, (), {'err_name': ['vladimir', 'Aviator']}),
            (glorax.GloraxParser, (), {'err_name': ['vladimir', 'Glorax']}),
            # (nmarket.NmarketParser, (), {'headless': False, 'err_name': ['vladimir', 'Nmarket']}),
        ]

        results: list[dict] = await self.__run_all_parsers(parsers)

        return self.to_exel(results)

if __name__ == '__main__':
    per = VladimirManager()
    asyncio.run(per.run_vladimir_module())

