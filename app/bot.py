from aiogram import Bot, Dispatcher

from app.config import BOT_TOKEN
from app.handlers.business import router as business_router
from app.handlers.start import router as start_router

if BOT_TOKEN is None:
    raise ValueError("BOT_TOKEN is not configured")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

dp.include_router(start_router)
dp.include_router(business_router)
