import asyncio
import logging

from app.bot import bot, dp

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")


async def main() -> None:
    print("Бот запускается, один момент!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())