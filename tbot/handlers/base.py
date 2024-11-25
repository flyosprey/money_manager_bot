from telebot.types import Message

from money_manager.config import config
from tbot.decorators import exception_handler
from tbot.dispatchers.base import (
    handle_start,
)
from tbot.keyboards import transaction_menu
from tbot.utils import create_transaction_text
from tbot_base.bot import tbot as bot


@bot.message_handler(commands=["start"])
@exception_handler()
def start_handler(message: Message):
    handle_start(message=message)


@bot.message_handler(commands=["test"])
@exception_handler()
def test_handler(message: Message):
    if config.is_test:
        bot.send_message(
            chat_id=message.chat.id,
            text=create_transaction_text(
                currency="UAH",
                description="Тестовий",
                amount=100,
                comment="відсутній",
                cashback="відсутній",
                commission="відсутня",
                date_="2024-11-21 14:53:59",
                transaction_type="-",
                mcc_code=5411,
                separator="",
            ),
            reply_markup=transaction_menu(),
        )
