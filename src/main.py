"""Main entry point for the bot."""

import asyncio
import logging
import os
import signal
import sys

from src.bot import TheComradeMajorBot
from src.config import settings


def setup_logging() -> None:
    """Set up logging configuration."""
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=getattr(logging, settings.log_level.upper()),
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("logs/bot.log", encoding="utf-8"),
        ],
    )

    # Reduce noise from some libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.INFO)


async def main() -> None:
    """Main function."""
    setup_logging()
    logger = logging.getLogger(__name__)

    # Validate required settings
    if not settings.telegram_bot_token:
        logger.error("TELEGRAM_BOT_TOKEN is required")
        sys.exit(1)

    if not settings.gigachat_client_id or not settings.gigachat_client_secret:
        logger.error("GigaChat credentials are required")
        sys.exit(1)

    bot = TheComradeMajorBot()
    shutdown_event = asyncio.Event()

    # Set up signal handlers for graceful shutdown
    def signal_handler(signum: int, frame) -> None:  # type: ignore
        logger.info(f"Received signal {signum}, shutting down...")
        shutdown_event.set()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        await bot.start()
        logger.info("Bot started successfully. Press Ctrl+C to stop.")
        
        # Wait for shutdown signal
        await shutdown_event.wait()
        logger.info("Shutdown signal received, stopping bot...")
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        await bot.stop()


if __name__ == "__main__":
    asyncio.run(main())
