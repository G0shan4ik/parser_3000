import asyncio

from loguru import logger

from p3000.bott.core import bott, dp, BOT_URL
from p3000.bott.helpers import FlagsManager


async def on_startup(dispatcher):
    logger.success(f"Bot{' ('+BOT_URL+')' if BOT_URL else ''} is running!")

async def on_shutdown(dispatcher):
    fl = FlagsManager()
    flags_json: dict = await fl.read_all_flags()
    for key, value in flags_json.items():
        await fl.update_full_flag(
            key=key,
            new_data={
                "bool": False,
                "minutes": 0,
                "seconds": 0,
                "state": "disabled"
            }
        )
    logger.success('The bot is stopped; __flags.json has been cleared!')

async def main() -> None:
    await bott.delete_webhook(drop_pending_updates=True)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    await asyncio.gather(dp.start_polling(bott))

def start_dev():
    asyncio.run(main())