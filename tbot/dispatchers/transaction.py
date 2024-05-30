from telebot.types import CallbackQuery

from money_manager.config import Config
from tbot.controllers.transaction import add_transaction, get_transaction_from_message
from tbot.keyboards import transaction_menu
from tbot.utils import edit_message


def handle_accept_transaction(call: CallbackQuery, config: Config):
    transaction = get_transaction_from_message(call.message.text)

    add_transaction(
        user_id=call.from_user.id,
        base_url=config.walletapp.base_url,
        secret_key=config.secret_key,
        transaction=transaction,
    )

    edit_message(
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        text=f"{call.message.text}\n\nЗаписано ✅",
        reply_markup=transaction_menu(),
    )


def handle_reject_transaction(call: CallbackQuery):
    edit_message(
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        text=f"{call.message.text}\n\nВідхилено 🚫",
        reply_markup=transaction_menu(),
    )
