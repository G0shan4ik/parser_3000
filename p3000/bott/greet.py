from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold

from .core import dp, ADMIN, bott
from .keyboard import main_kb


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await bott.send_message(
        chat_id=ADMIN,
        text=f'''{hbold("I'm ready to parse apartments!")}\n\nSelect an action!  📉''',
        reply_markup=main_kb()
    )