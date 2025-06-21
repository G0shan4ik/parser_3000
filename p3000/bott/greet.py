from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold

from .core import dp, ADMIN
from .keyboard import main_kb


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.bot.send_message(
        chat_id=ADMIN,
        text='👋🏿'
    )
    await message.bot.send_message(
        chat_id=ADMIN,
        text=f'{hbold("Готов парсить квартиры!")}\n\nВыберите действие!  📉',
        reply_markup=main_kb()
    )