from telebot.types import CallbackQuery, Message

from money_manager.config import config
from tbot.controllers.wallet_settings import add_label
from tbot.dependencies.redis import RedisWrapper
from tbot.dto.walletapp.type import SettingsStates
from tbot.keyboards import wallet_settings_menu
from tbot_base.bot import tbot as bot


def handle_wallet_settings(message: Message):
    bot.send_message(
        text="Налаштування гаманця обліку",
        chat_id=message.chat.id,
        reply_markup=wallet_settings_menu(),
    )


def handle_awaiting_add_label(call: CallbackQuery, redis: RedisWrapper):
    bot.send_message(
        text="Введіть назву мітки:",
        chat_id=call.message.chat.id,
    )
    redis.set_settings_status(
        user_id=call.from_user.id, status=SettingsStates.ADD_LABEL
    )


def handle_add_label(message: Message):
    label = message.text.strip()

    add_label(label=label, secret_key=config.secret_key, user_id=message.from_user.id)

    bot.send_message(
        text="Мітка успішно додана!✅",
        chat_id=message.chat.id,
    )
