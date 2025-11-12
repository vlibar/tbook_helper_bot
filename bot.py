import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from config import BOT_TOKEN
from handlers import start_handler, indicators_handler

# Bot setup
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Register handlers
dp.message.register(start_handler, Command("start"))
dp.message.register(indicators_handler)

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())