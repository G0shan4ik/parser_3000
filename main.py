import asyncio

from loguru import logger

from p3000.bott.core import bott, dp


async def on_startup(dispatcher):
    logger.success("Bot (https://t.me/new_p3000_bot) is running!")

async def main() -> None:
    await bott.delete_webhook(drop_pending_updates=True)

    dp.startup.register(on_startup)

    await asyncio.gather(dp.start_polling(bott))

def start_dev():
    asyncio.run(main())