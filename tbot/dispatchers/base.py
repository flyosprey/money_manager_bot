from telebot.types import Message

from tbot.controllers.base import (
    register_user,
)
from tbot.keyboards import menu
from tbot_base.bot import tbot as bot


def handle_start(message: Message):
    register_user(message=message)
    bot.send_message(
        chat_id=message.chat.id,
        text="Привіт!👋\nОбери опцію",
        parse_mode="HTML",
        reply_markup=menu(bot),
    )

