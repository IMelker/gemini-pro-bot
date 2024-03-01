import logging
import os
from telegram import Update, BotCommandScopeAllGroupChats
from telegram import BotCommand
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    Application,
    ApplicationBuilder,
)
from gemini_pro_bot.filters import AuthFilter, MessageFilter, PhotoFilter, GroupMessageFilter
from dotenv import load_dotenv
from gemini_pro_bot.handlers import (
    start,
    help_command,
    newchat_command,
    handle_message,
    handle_image,
    error_handler,
)


class GeminiTelegramBot:
    """
    Class representing a Gemini Telegram Bot.
    """

    def __init__(self):
        """
        Initializes the bot.
        """

        self.commands = [
            BotCommand(command='help', description='Get help',),
            BotCommand(command='new', description='Reset chat session')
        ]

        self.group_commands = [
            BotCommand(command='chat', description='Send a message to the bot'),
            BotCommand(command='vision', description='Describe what on photo')
        ] + self.commands

    async def post_init(self, application: Application) -> None:
        """
        Post initialization hook for the bot.
        """
        await application.bot.set_my_commands(self.group_commands, scope=BotCommandScopeAllGroupChats())
        await application.bot.set_my_commands(self.commands)

    def run(self):
        """
        Runs the bot indefinitely until the user presses Ctrl+C
        """

        """Start the bot."""
        # Create the Application and pass it your bot's token.
        application = ApplicationBuilder() \
            .token(os.getenv("BOT_TOKEN")) \
            .post_init(self.post_init) \
            .concurrent_updates(True) \
            .build()

        # on different commands - answer in Telegram
        application.add_handler(CommandHandler("start", start, filters=AuthFilter))
        application.add_handler(CommandHandler("help", help_command, filters=AuthFilter))
        application.add_handler(CommandHandler("new", newchat_command, filters=AuthFilter))

        # group chat commands
        application.add_handler(CommandHandler('chat', handle_message, filters=GroupMessageFilter))
        application.add_handler(CommandHandler('vision', handle_image, filters=GroupMessageFilter))

        # Any text message is sent to LLM to generate a response
        application.add_handler(MessageHandler(MessageFilter, handle_message))

        # Any image is sent to LLM to generate a response
        application.add_handler(MessageHandler(PhotoFilter, handle_image))

        application.add_error_handler(error_handler)

        # Run the bot until the user presses Ctrl-C
        application.run_polling(allowed_updates=Update.ALL_TYPES)


def start_bot() -> None:
    # Read .env file
    load_dotenv()

    # Setup logging
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)

    telegram_bot = GeminiTelegramBot()
    telegram_bot.run()
