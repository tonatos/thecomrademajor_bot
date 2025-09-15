"""Telegram bot implementation."""

import logging
from typing import Optional

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from src.config import settings
from src.gigachat_client import GigaChatClient

logger = logging.getLogger(__name__)


class TheComradeMajorBot:
    """Main bot class."""

    def __init__(self) -> None:
        """Initialize the bot."""
        self.gigachat_client = GigaChatClient()

        # Create application with explicit configuration
        try:
            builder = Application.builder()
            builder.token(settings.telegram_bot_token)

            # Configure for basic bot functionality
            builder.concurrent_updates(True)

            self.application = builder.build()
        except Exception as e:
            print(f"❌ Ошибка создания приложения Telegram: {e}")
            print("💡 Проверьте корректность TELEGRAM_BOT_TOKEN в .env файле")
            raise
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Set up message handlers."""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self._start_command))
        self.application.add_handler(CommandHandler("help", self._help_command))

        # Message handlers for mentions and replies
        self.application.add_handler(
            MessageHandler(
                filters.TEXT & filters.REPLY,
                self._handle_mention_or_reply,
            )
        )

        # Separate handler for mentions
        self.application.add_handler(
            MessageHandler(
                filters.TEXT,
                self._handle_mention_only,
            )
        )

    def _mention_filter(self, update: Update) -> bool:
        """Filter for messages that mention the bot."""
        if not update.message or not update.message.text:
            return False

        # Check if bot is mentioned
        bot_username = f"@{settings.bot_username}"
        return bot_username.lower() in update.message.text.lower()

    async def _start_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /start command."""
        if not update.message:
            return

        welcome_text = (
            "🚔 ВНИМАНИЕ! Майор полиции на связи!\n\n"
            "Я слежу за соблюдением законности в этом чате. "
            "Упомяните меня (@thecomrademajor_bot) при ответе на сообщение, "
            "и я проведу проверку на предмет нарушения законодательства РФ!\n\n"
            "Используйте /help для получения дополнительной информации."
        )

        await update.message.reply_text(welcome_text)

    async def _help_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /help command."""
        if not update.message:
            return

        help_text = (
            "🚔 ИНСТРУКЦИЯ ПО ИСПОЛЬЗОВАНИЮ БОТА:\n\n"
            "1️⃣ Ответьте на любое сообщение в чате\n"
            "2️⃣ Упомяните меня (@thecomrademajor_bot) в своем ответе\n"
            "3️⃣ Я проанализирую исходное сообщение на предмет нарушений\n\n"
            "⚠️ ВНИМАНИЕ: Бот создан в развлекательных целях!"
        )

        await update.message.reply_text(help_text)

    async def _handle_mention_only(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle mentions without replies."""
        if not update.message or not self._mention_filter(update):
            return

        await update.message.reply_text(
            "🚔 ГРАЖДАНЕ! Ответьте на сообщение и упомяните меня "
            "для проведения проверки!"
        )

    async def _handle_mention_or_reply(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle replies with mentions to messages."""
        if not update.message:
            return

        # Only process if bot is mentioned in a reply
        if not self._mention_filter(update):
            return

        try:
            # Get the replied message
            replied_message: Optional[str] = None

            if (
                update.message.reply_to_message
                and update.message.reply_to_message.text
            ):
                replied_message = update.message.reply_to_message.text

            if not replied_message:
                await update.message.reply_text(
                    "🚔 ГРАЖДАНЕ! Ответьте на сообщение и упомяните меня "
                    "для проведения проверки!"
                )
                return

            # Remove bot mention from the message to analyze
            bot_username = f"@{settings.bot_username}"
            clean_message = replied_message.replace(bot_username, "").strip()

            if not clean_message:
                await update.message.reply_text(
                    "🚔 ВНИМАНИЕ! Пустое сообщение также может "
                    "рассматриваться как нарушение общественного порядка!"
                )
                return

            # Show typing indicator
            if update.effective_chat:
                await context.bot.send_chat_action(
                    chat_id=update.effective_chat.id, action="typing"
                )

            # Generate response using GigaChat
            response = await self.gigachat_client.generate_response(clean_message)

            # Send the response
            await update.message.reply_text(response)

            chat_id = (
                update.effective_chat.id if update.effective_chat else "unknown"
            )
            user_id = update.effective_user.id if update.effective_user else "unknown"
            logger.info(f"Processed message in chat {chat_id} from user {user_id}")

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await update.message.reply_text(
                "🚔 ТЕХНИЧЕСКИЕ НЕПОЛАДКИ! Но это не освобождает вас от "
                "ответственности перед законом!"
            )

    async def start(self) -> None:
        """Start the bot."""
        logger.info("Starting TheComradeMajor bot...")
        await self.application.initialize()
        await self.application.start()
        if self.application.updater:
            await self.application.updater.start_polling()
        logger.info("Bot is running and polling for updates")

    async def stop(self) -> None:
        """Stop the bot."""
        logger.info("Stopping TheComradeMajor bot...")
        
        # Stop updater if it's running
        try:
            if hasattr(self.application, 'updater') and self.application.updater:
                if self.application.updater.running:
                    logger.info("Stopping updater...")
                    await self.application.updater.stop()
                else:
                    logger.debug("Updater is not running")
            else:
                logger.debug("No updater to stop")
        except Exception as e:
            logger.warning(f"Error stopping updater: {e}")

        # Stop and shutdown application
        try:
            if hasattr(self.application, 'running') and self.application.running:
                logger.info("Stopping application...")
                await self.application.stop()
            else:
                logger.debug("Application is not running")
                
            logger.info("Shutting down application...")
            await self.application.shutdown()
        except Exception as e:
            logger.warning(f"Error stopping/shutting down application: {e}")

        # Close GigaChat client
        try:
            await self.gigachat_client.close()
        except Exception as e:
            logger.warning(f"Error closing GigaChat client: {e}")

        logger.info("Bot stopped successfully")