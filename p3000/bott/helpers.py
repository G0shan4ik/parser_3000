import aiofiles
import json
from typing import Literal, Union

from aiogram.utils.markdown import hbold


PARSING_LIST_TEXT = f'''
{hbold("-ALL PARSERS-")}

\t\t# Vladimir parsers (5 parsers) 
1) {hbold("Aviator")}   -_-   (📘 sync parser)
2) {hbold("Glorax")}   -_-   (📗 async parser)
3) {hbold("Legenda")}   -_-   (📙 selenium parser)
4) {hbold("Nmarket")}   -_-   (📙 selenium parser)
5) {hbold("VladimirSK")}   -_-   (📗 async parser)


\t\t# Vladimir parsers (8 parsers)
1) {hbold("EuropeyStile")}   -_-   (📘 sync parser)
2) {hbold("Olimp")}   -_-   (📗 async parser)
3) {hbold("Vidniy")}   -_-   (📘 sync parser)
4) {hbold("CSY")}   -_-   (📘 sync parser)
5) {hbold("DefaultKvartal")}   -_-   (📘 sysync parser)
6) {hbold("Levitan")}   -_-   (📙 selenium parser)
7) {hbold("KSK_Holding")}   -_-   (📙 selenium parser)
8) {hbold("Fenix")}   -_-   (📙 selenium parser)
'''


FlagKey = Literal[
    "ivan", "vladimir", "all_pars",   # Main group

    "Aviator", "Glorax", "Legenda", "Nmarket", "VladimirSK",    # Vladimir parsers names

    "EuropeyStile", "Olimp", "Vidniy", "CSY", "DefaultKvartal", "Levitan", "KSK_Holding", "Fenix"   # Ivanovo parsers names
]

StateValue = Literal["disabled", "in process", "completed!"]    # States name
SubKey = Literal["bool", "minutes", "seconds", "state", "errors", "parser_name"]    # SubKeys name (file -> __flags.json)


all_parsers_names = {
    'ivan': [''],
    'vladimir': ['aviator', 'legenda', 'nmarket', 'vladimir_sk'],
    'single': [
        'aviator', 'legenda', 'nmarket', 'vladimir_sk',
    ]
}


__vladimir_parsers_names = [
    "Aviator", "Glorax", "Legenda", "Nmarket", "VladimirSK"
]
__ivanovo_parsers_names = [
    "EuropeyStile", "Olimp", "Vidniy", "CSY", "DefaultKvartal",
    "Levitan", "KSK_Holding", "Fenix"
]


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


class FlagsManager:
    def __init__(self, filepath: str = '__flags.json'):
        self.filepath = filepath

    async def read_all_flags(self) -> dict:
        async with aiofiles.open(self.filepath, mode='r') as f:
            content = await f.read()
            return json.loads(content)

    async def _write_all_flags(self, data: dict) -> None:
        async with aiofiles.open(self.filepath, mode='w') as f:
            await f.write(json.dumps(data, indent=4))

    async def read_flag_value(self,
                              key: FlagKey,
                              subkey: SubKey
                              ) -> Union[bool, int, str, list, dict, None]:
        data = await self.read_all_flags()
        return data.get(key, {}).get(subkey)

    async def update_flag_value(self,
                                key: FlagKey,
                                subkey: SubKey,
                                value: Union[bool, int, str, list, dict]
                                ) -> bool:
        try:
            data = await self.read_all_flags()

            if key not in data:
                return False
            data[key][subkey] = value

            await self._write_all_flags(data)
            return True
        except Exception:
            return False

    async def get_full_flag(self, key: FlagKey) -> Union[dict, None]:
        data = await self.read_all_flags()
        return data.get(key)

    async def update_full_flag(self, key: FlagKey, new_data: dict) -> bool:
        try:
            data = await self.read_all_flags()
            if key not in data:
                return False

            data[key].update(new_data)
            await self._write_all_flags(data)
            return True
        except Exception:
            return False

    async def delete_flag(self, key: FlagKey) -> bool:
        try:
            data = await self.read_all_flags()
            if key not in data:
                return False
            del data[key]
            await self._write_all_flags(data)
            return True
        except Exception:
            return False

    async def add_flag(self, key: FlagKey) -> bool:
        try:
            data = await self.read_all_flags()
            if key in data:
                return False  # уже существует

            data[key] = {
                "parser_name": key,
                "bool": False,
                "minutes": 0,
                "seconds": 0,
                "state": "disabled",
                "errors": {}
            }
            await self._write_all_flags(data)
            return True
        except Exception:
            return False



def get_error_info(error_json: dict) -> str:
    __cnt = 0

    if not error_json:
        return hbold('There are no errors')
    res_txt = ''
    for key, value in error_json.items():
        __cnt += 1
        res_txt += f'\n{hbold(str(__cnt) + ")")} Parser name: {hbold(value[0])};\n    Error: {hbold(value[-1])}'
    return res_txt

async def formatted_info_text(fl: FlagsManager) -> str:
    res_txt: list[str] = []
    flags_json: dict = await fl.read_all_flags()
    for key, value in flags_json.items():
        if value['bool'] or value['state'] in ['completed!', 'in process'] or value['errors'] != {}:
            txt = '------------------------------------------\n'
            txt += f'• {hbold("Name")}: {"Ivanovo" if key == "ivan" else key.capitalize()},   {hbold("State")}: {value["state"]}\n'
            txt += f'{hbold("Time")}:  {value["minutes"] if value["minutes"] != 0 else "-"} minutes;   {value["seconds"] if value["seconds"] != 0 else "-"} seconds\n'
            txt += f'{hbold("Errors:")}  {get_error_info(error_json=value["errors"])}\n'
            res_txt.append(txt)
    if res_txt:
        return '\n'.join(res_txt)
    return "There's nothing here 😱"


async def del_unnecessary_info(fl: FlagsManager) -> str:
    res_txt: list[str] = []
    flags_json: dict = await fl.read_all_flags()
    for key, value in flags_json.items():
        txt = ''
        if value['bool'] and value['state'] == 'in process':
            txt = '------------------------------------------\n'
            txt += f'• {hbold("Name")}: {"Ivanovo" if key == "ivan" else key.capitalize()},   {hbold("State")}: {value["state"]}\n'
            txt += f'{hbold("Time")}:  {value["minutes"] if value["minutes"] != 0 else "-"} minutes;   {value["seconds"] if value["seconds"] != 0 else "-"} seconds\n'
            txt += f'{hbold("Errors:")}  {get_error_info(error_json=value["errors"])}\n'
            res_txt.append(txt)
        elif key not in ["ivan", "vladimir", "all_pars"] and value['state'] in ['completed!', 'disabled']:
            await fl.delete_flag(key=key)
        elif value['state'] in ['completed!', 'disabled']:
            await fl.update_full_flag(
                key=key,
                new_data={
                    "bool": False,
                    "minutes": 0,
                    "seconds": 0,
                    "state": "disabled",
                    "errors": {}
                }
            )
    if res_txt:
        return '\n'.join(res_txt)
    return "There's nothing here 😱"
