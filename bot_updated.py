import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from config import BOT_TOKEN
from handlers import start_handler, indicators_handler

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot setup
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Register handlers
dp.message.register(start_handler, Command("start"))
dp.message.register(indicators_handler)

async def main():
    logger.info("Starting bot...")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error running bot: {e}")
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())
