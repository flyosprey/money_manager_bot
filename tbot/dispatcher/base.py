from telebot.types import Message

from tbot.controller.base import (
    register_user,
)

from tbot_base.bot import tbot as bot

from tbot.keyboards import menu


def handle_start(message: Message):
    register_user(message)
    bot.send_message(
        chat_id=message.chat.id,
        text="Hi there!👋\n To start run /integrate",
        parse_mode="HTML",
        reply_markup=menu(bot),
    )


def handle_help(message: Message):
    bot.send_message(
        chat_id=message.chat.id,
        text="""Here you can see all available commands:
         /start - To start bot.
         /help - To view all available commands.
         """,
    )
