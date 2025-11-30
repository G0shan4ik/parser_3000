import inspect

import pandas as pd
from loguru import logger
from datetime import datetime

import asyncio
from concurrent.futures import ThreadPoolExecutor

from typing import Union, Any, Type, Tuple

from .Vladimir_parsers import vladimir_sk, legenda, aviator, glorax, vt
from .Ivanovo_parsers import csy, default_kvartal, evropey_stile, fenix, ksk_holding, levitan, olimp, vidniy


class BaseManager:
    def __init__(self, module_name: str, batch_size: int = 3):
        self.module_name = module_name
        self.batch_size = batch_size

    def to_exel(self, mass: list[dict]) -> str:
        df = pd.DataFrame(mass)
        df.to_excel(f"all_exel/{datetime.now().date()}_{self.module_name}.xlsx")

        logger.success(f'<-- Success created MODULE_file (module_name -> {self.module_name})')

        return f"all_exel/{datetime.now().date()}_{self.module_name}.xlsx"

    @staticmethod
    def chunks(lst, n):
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    async def _run_all_parsers(self, parser_definitions):
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
                logger.error(f'{self.module_name}; Fatal ERROR ->\n{ex}\n\n')

        return results



class IvanovoManager(BaseManager):
    def __init__(self, batch_size: int = 3):
        super().__init__(
            module_name='Ivanovo',
            batch_size=batch_size
        )

    async def run_ivanovo_module(self):
        parsers = [
            (csy.CSYParser, (), {'err_name': ['ivan', 'CSY']}),
            (default_kvartal.DefaultKvartalParser, (), {'err_name': ['ivan', 'DefaultKvartal']}),
            (evropey_stile.EuropeyStileParser, (), {'err_name': ['ivan', 'EuropeyStile']}),
            (ksk_holding.KSKHoldingParser, (), {'err_name': ['ivan', 'KSK_Holding']}),
            (levitan.LevitanParser, (), {'err_name': ['ivan', 'Levitan']}),
            (olimp.OlimpParser, (), {'err_name': ['ivan', 'Olimp']}),
            (fenix.FenixParser, (), {'headless': False, 'err_name': ['ivan', 'Fenix']}),
            (vidniy.VidniyParser, (), {'err_name': ['ivan', 'Vidniy']}),
        ]

        results: list[dict] = await self._run_all_parsers(parsers)

        return self.to_exel(results)


class VladimirManager(BaseManager):
    def __init__(self, batch_size: int = 3):
        super().__init__(
            module_name='Vladimir',
            batch_size=batch_size
        )

    async def run_vladimir_module(self) -> str:
        parsers = [
            (vt.VTParser, (), {'headless': False, 'err_name': ['vladimir', 'VT']}),
            (vladimir_sk.VladimirParser, (), {'err_name': ['vladimir', 'VladimirSK']}),
            (glorax.GloraxParser, (), {'err_name': ['vladimir', 'Glorax']}),
            (aviator.AviatorParser, (), {'err_name': ['vladimir', 'Aviator']}),
            (legenda.LegendaParser, (), {'err_name': ['vladimir', 'Legenda']}),
        ]

        results: list[dict] = await self._run_all_parsers(parsers)

        return self.to_exel(results)


class AllParsManager(BaseManager):
    def __init__(self, batch_size: int = 4):
        super().__init__(
            module_name='all_pars',
            batch_size=batch_size
        )

    async def run_all_parsers_module(self) -> str:
        parsers = [
            (fenix.FenixParser, (), {'headless': False, 'err_name': ['all_pars', 'Fenix']}),
            (csy.CSYParser, (), {'err_name': ['all_pars', 'CSY']}),
            (default_kvartal.DefaultKvartalParser, (), {'err_name': ['all_pars', 'DefaultKvartal']}),
            (evropey_stile.EuropeyStileParser, (), {'err_name': ['all_pars', 'EuropeyStile']}),
            (ksk_holding.KSKHoldingParser, (), {'err_name': ['all_pars', 'KSK_Holding']}),
            (levitan.LevitanParser, (), {'err_name': ['all_pars', 'Levitan']}),
            (olimp.OlimpParser, (), {'err_name': ['all_pars', 'Olimp']}),
            (vidniy.VidniyParser, (), {'err_name': ['all_pars', 'Vidniy']}),

            (vladimir_sk.VladimirParser, (), {'err_name': ['all_pars', 'VladimirSK']}),
            (legenda.LegendaParser, (), {'err_name': ['all_pars', 'Legenda']}),
            (aviator.AviatorParser, (), {'err_name': ['all_pars', 'Aviator']}),
            (glorax.GloraxParser, (), {'err_name': ['all_pars', 'Glorax']}),
            (vt.VTParser, (), {'headless': False, 'err_name': ['vladimir', 'VT']}),
            # (nmarket.NmarketParser, (), {'headless': False, 'err_name': ['all_pars', 'Nmarket']}),
        ]

        results: list[dict] = await self._run_all_parsers(parsers)

        return self.to_exel(results)



if __name__ == '__main__':
    per1 = VladimirManager()
    per2 = IvanovoManager()
    asyncio.run(per1.run_vladimir_module())

