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
        text="Привіт!👋 Я бот OspreyMoney."
             "\nЯ допоможу тобі автоматично фіксувати прибутки та витрати з твоїх кредитних карток. "
             "💳Наразі я працюю з Monobank і записую всі твої витрати у додаток BudgetBakers. "
             "Зі мною ти завжди будеш контролювати свій бюджет швидко та зручно!"
             "\n🧾Обери опцію нижче, щоб розпочати.",
        parse_mode="HTML",
        reply_markup=menu(bot),
    )

