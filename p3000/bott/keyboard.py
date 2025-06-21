from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Vladimir 👾',
                                     callback_data=f'vladimir'),
                InlineKeyboardButton(text='Ivanovo 👾',
                                     callback_data=f'ivan')
            ],
            [InlineKeyboardButton(text='Full pars 🔄', callback_data=f'pars_all')],
            [InlineKeyboardButton(text='Pars a single site 1️⃣', callback_data=f'single')],
            [InlineKeyboardButton(text='PARSING INFO 📃', callback_data=f'info')]
        ]
    )