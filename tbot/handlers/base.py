from telebot.types import Message

from tbot.dispatchers.base import (
    handle_help,
    handle_start,
)
from tbot.dto.transactions.payload import SimpleTransaction
from tbot.keyboards import transaction_menu
from tbot.utils import TRANSACTION_DATA, get_unix_time
from tbot_base.bot import tbot as bot


@bot.message_handler(commands=["start"])
def start_handler(message: Message):
    handle_start(message=message)


@bot.message_handler(commands=["help"])
def help_handler(message: Message):
    handle_help(message=message)


@bot.message_handler(commands=["test"])
def test_handler(message: Message):
    TRANSACTION_DATA[message.from_user.id] = SimpleTransaction(
                    mcc=5411,
                    amount=15000,
                    note="Weekly grocery shopping",
                    time=get_unix_time(),
                    contractor="ATБ"
                )
    bot.send_message(
        chat_id=message.chat.id,
        text="TESTING TRANS KEYWORD AND CALLBACK",
        reply_markup=transaction_menu(),
    )
