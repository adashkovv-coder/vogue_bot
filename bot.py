#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config import BOT_TOKEN
from database import Database

# Импортируем роутеры из папки handlers
from handlers import start, order, status, admin

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Подключаем роутеры
dp.include_router(start.router)
dp.include_router(order.router)
dp.include_router(status.router)
dp.include_router(admin.router)

# Инициализация базы данных (создаст файл vogue_bot.db)
db = Database()

async def on_startup():
    logger.info("Бот запущен!")

async def on_shutdown():
    logger.info("Бот остановлен.")

async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())