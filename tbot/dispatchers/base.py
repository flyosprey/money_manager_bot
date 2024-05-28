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
        text="Привіт!👋\nЩоб розпочати натисніть /integrate",
        parse_mode="HTML",
        reply_markup=menu(bot),
    )


def handle_help(message: Message):
    bot.send_message(
        chat_id=message.chat.id,
        text="""Доступні команди:
         /start - Розпочати бота.
         /integrate - Розпочати інтеграцію.
         /additional_monobank_token - Додати трекінг додаткового аккаунту Monobank.
         /reset_password - Замінити пароль WalletApp.
         /reset_token - Замінити токен Monobank.
         /help - Подивитися всі доступні команди.
         """,
    )
