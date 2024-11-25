from telebot.types import Message

from money_manager.config import config
from tbot.decorators import exception_handler
from tbot.dispatchers.base import (
    handle_start,
)
from tbot.keyboards import transaction_menu
from tbot_base.bot import tbot as bot


@bot.message_handler(commands=["start"])
@exception_handler()
def start_handler(message: Message):
    handle_start(message=message)


@bot.message_handler(commands=["test"])
@exception_handler()
def test_handler(message: Message):
    if config.is_test:
        space = "\u00B7"
        bot.send_message(
            chat_id=message.chat.id,
            text="💰Валюта платежу: UAH\n"
            "🔖Опис: Тестовий\n"
            "🫰Сума: 100.23₴\n"
            "😔Комісія: відсутня\n"
            "🤑Кешбек: відсутній\n"
            "💬Коментар: відсутній\n"
            "📅Дата: 2024-11-21 14:53:59\n"
            f"🗂️Категорія: Кафе та Ресторани☕ (5411)\n"
            f"{'_' * 70}",
            reply_markup=transaction_menu(),
        )
