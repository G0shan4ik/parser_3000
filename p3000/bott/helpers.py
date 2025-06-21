from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import aiofiles
import json
from typing import Literal


class FlagsManager:
    def __init__(self, filepath: str = '__flags.json'):
        self.filepath = filepath

    async def read_flag(self, key: Literal['ivan', 'vladimir', 'all_pars']) -> bool:
        async with aiofiles.open(self.filepath, mode='r') as f:
            content = await f.read()
            data = json.loads(content)
            return data.get(key)

    async def update_flag(self, key: Literal['ivan', 'vladimir', 'all_pars'], value: bool) -> bool:
        try:
            async with aiofiles.open(self.filepath, mode='r') as f:
                content = await f.read()
                data = json.loads(content)

            data[key] = value

            async with aiofiles.open(self.filepath, mode='w') as f:
                await f.write(json.dumps(data, indent=4))

            return True
        except:
            return False


def main_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Vladimir',
                                     callback_data=f'vladimir'),
                InlineKeyboardButton(text='Ivanovo',
                                     callback_data=f'ivan')
            ],
            [InlineKeyboardButton(text='Full pars', callback_data=f'pars_all')],
            [InlineKeyboardButton(text='PARSING INFO 📃', callback_data=f'info')]
        ]
    )