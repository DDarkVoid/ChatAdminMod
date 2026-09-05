"""Bot entry point."""

import asyncio
import logging

from app.bot import bot, dp

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
)


async def main() -> None:
    """Start bot polling."""
    logger.info('Bot is starting polling...')
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
