from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from markdown_it.rules_core import inline

from .helpers import chunks, __vladimir_parsers_names, __ivanovo_parsers_names

def main_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Vladimir 👾',
                                     callback_data=f'vladimir'),
                InlineKeyboardButton(text='Ivanovo 👾',
                                     callback_data=f'ivan')
            ],
            [InlineKeyboardButton(text='Full pars 🔢', callback_data=f'pars_all')],
            [InlineKeyboardButton(text='Pars a single site 1️⃣', callback_data=f'single')],
            [InlineKeyboardButton(text='PARSING INFO 📃', callback_data=f'info')],
            [InlineKeyboardButton(text='Parsing List 📝', callback_data=f'list')]
        ]
    )

def info_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Reload page 🔄', callback_data=f'info')],
            [InlineKeyboardButton(text='Clear 🚮', callback_data=f'clear')],
            [InlineKeyboardButton(text='Back Main menu', callback_data=f'go_back')]
        ]
    )

def single_parsers_kb():
    mass = [
        InlineKeyboardButton(text=item, callback_data=f'_single#{item}')
        for item in __vladimir_parsers_names + __ivanovo_parsers_names
    ]
    inline_kb = [item for item in chunks(mass, 3)]
    inline_kb += [[InlineKeyboardButton(text='Back Main menu', callback_data=f'go_back')]]
    return InlineKeyboardMarkup(
        inline_keyboard=inline_kb
    )

def cancel_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Back Main menu', callback_data=f'go_back')]
        ]
    )