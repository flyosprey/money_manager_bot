from telebot.types import CallbackQuery

from money_manager.config import Config
from tbot.controllers.transaction import add_transaction
from tbot.utils import TRANSACTION_DATA
from tbot_base.bot import tbot as bot


def handle_accept_transaction(call: CallbackQuery, config: Config):
    add_transaction(
        user_id=call.from_user.id,
        base_url=config.walletapp.base_url,
        secret_key=config.secret_key,
        transaction=TRANSACTION_DATA[call.from_user.id]
    )

    edited_message = f"{call.message.text}\n\nЗаписано ✅"
    bot.edit_message_text(
        chat_id=call.message.chat.id, message_id=call.message.id, text=edited_message
    )
    del TRANSACTION_DATA[call.from_user.id]


def handle_reject_transaction(call: CallbackQuery):
    edited_message = f"{call.message.text}\n\nВідхилено 🚫"
    bot.edit_message_text(
        chat_id=call.message.chat.id, message_id=call.message.id, text=edited_message
    )
    del TRANSACTION_DATA[call.from_user.id]
