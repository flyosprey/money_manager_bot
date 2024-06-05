import structlog
from telebot.types import Message

from money_manager.config import config
from tbot.controllers.transaction import add_transaction
from tbot.dispatchers.base import (
    handle_help,
    handle_start,
)
from tbot.dto.transactions.payload import SimpleTransaction
from tbot.utils import exception_handler, get_unix_time
from tbot_base.bot import tbot as bot

logger = structlog.get_logger()


@bot.message_handler(commands=["start"])
@exception_handler()
def start_handler(message: Message):
    handle_start(message=message)


@bot.message_handler(commands=["help"])
@exception_handler()
def help_handler(message: Message):
    handle_help(message=message)


@bot.message_handler(commands=["test"])
@exception_handler()
def test_handler(message: Message):
    if config.is_test:
        add_transaction(
            user_id=message.chat.id,
            base_url=config.walletapp.base_url,
            secret_key=config.secret_key,
            transaction=SimpleTransaction(
                mcc=5411,
                amount=15000,
                note="Weekly grocery shopping",
                time=get_unix_time(),
                contractor="ATБ",
            ),
        )
