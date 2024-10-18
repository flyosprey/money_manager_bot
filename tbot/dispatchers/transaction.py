from telebot.types import CallbackQuery

from money_manager.config import Config
from tbot.controllers.transaction import (
    add_transaction,
    get_transaction_from_message,
)
from tbot.keyboards import transaction_menu, transaction_categories_menu
from tbot.utils import edit_message


def handle_accept_transaction(call: CallbackQuery, config: Config):
    transaction = get_transaction_from_message(call.message.text)

    add_transaction(
        user_id=call.from_user.id,
        secret_key=config.secret_key,
        transaction=transaction,
    )

    edit_message(
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        text=f"{call.message.text}\n\nЗаписано✅",
    )


def handle_reject_transaction(call: CallbackQuery):
    text = call.message.text.replace("\n\nВідхилено🚫", "")
    edit_message(
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        text=f"{text}\n\nВідхилено🚫",
        reply_markup=transaction_menu(),
    )


def handle_select_category_transaction(page: int, call: CallbackQuery):
    text = call.message.text
    edit_message(
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        text=text,
        reply_markup=transaction_categories_menu(page=page),
    )
