from aiogram.fsm.storage.memory import MemoryStorage

from aiogram.client.bot import DefaultBotProperties

from aiogram.enums import ParseMode
from aiogram import Bot, Dispatcher, Router

import os
from dotenv import load_dotenv

load_dotenv()


TOKEN_API = os.getenv("TOKEN_API")
ADMIN = os.getenv("ADMIN")
BOT_URL = os.getenv("BOT_URL")

bott = Bot(
    token=TOKEN_API,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router(name="main_router")
dp.include_routers(router)