from telebot.types import Message

from money_manager.config import config
from tbot.controllers.transaction import add_transaction
from tbot.decorators import exception_handler
from tbot.dispatchers.base import (
    handle_start,
)
from tbot.dto.transactions.payload import SimpleTransaction
from tbot.keyboards import transaction_menu
from tbot.utils import get_unix_time
from tbot_base.bot import tbot as bot


@bot.message_handler(commands=["start"])
@exception_handler()
def start_handler(message: Message):
    handle_start(message=message)


@bot.message_handler(commands=["test"])
@exception_handler()
def test_handler(message: Message):
    if config.is_test:
        bot.send_message(chat_id=message.chat.id, text=f"💰Валюта платежу: UAH\n"
                        f"🔖Опис: Тестовий\n"
                        f"🫰Сума: 100.23₴\n"
                        f"😔Комісія: відсутня\n"
                        f"🤑Кешбек: відсутній\n"
                        f"💬Коментар: відсутній\n"
                        f"📅Дата: 2024-11-21 14:53:59\n"
                        "🗂️Категорія: Кафе та Ресторани☕ (5411)",
                         reply_markup=transaction_menu(),)

        # add_transaction(
        #     user_id=message.chat.id,
        #     secret_key=config.secret_key,
        #     transaction=SimpleTransaction(
        #         mcc=5499,
        #         amount=-15000000,
        #         note="Weekly grocery shopping",
        #         time=get_unix_time(),
        #         contractor="ATБ",
        #         type="-",
        #     ),
        # )
