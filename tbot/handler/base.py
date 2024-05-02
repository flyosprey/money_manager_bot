from telebot.types import Message

from tbot.dispatcher.base import (
    handle_start,
    handle_help,
)
from tbot_base.bot import tbot as bot


@bot.message_handler(commands=["start"])
def start_handler(message: Message):
    handle_start(message=message)


@bot.message_handler(commands=["help"])
def help_handler(message: Message):
    handle_help(message=message)
