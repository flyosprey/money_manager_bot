import re

from telebot.types import CallbackQuery

from money_manager.config import Config
from tbot.controllers.transaction import (
    add_transaction,
    get_transaction_from_message,
)
from tbot.dto.walletapp.mcc_codes import MCCTransactionCategoryName
from tbot.keyboards import transaction_categories_menu, transaction_menu
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


def handle_select_category_transaction(call: CallbackQuery):
    page = re.search(r"page_(\d+)", call.data)
    page = int(page[1]) if page else 1

    text = call.message.text
    transaction = get_transaction_from_message(text)
    edit_message(
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        text=text,
        reply_markup=transaction_categories_menu(
            page=page, transaction_type=transaction.type
        ),
    )


def handle_change_category_transaction(call: CallbackQuery):
    mcc = re.search(r"category_(\d+)", call.data)
    if not mcc:
        raise Exception("call.data category error!")

    transaction = get_transaction_from_message(call.message.text)
    text = re.sub(
        r"Категорія:.+",
        f"Категорія: {MCCTransactionCategoryName[transaction.type][int(mcc[1])]} ({mcc[1]})",
        call.message.text,
    )
    edit_message(
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        text=text,
        reply_markup=transaction_menu(),
    )
