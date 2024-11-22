import re

from telebot.types import CallbackQuery
from telebot.types import Message

from money_manager.config import Config
from tbot.controllers.transaction import (
    add_transaction,
    get_transaction_from_message, get_comment, get_amount,
)
from tbot.dependencies.redis import RedisWrapper
from tbot.dto.transactions.type import TransactionStatus
from tbot_base.bot import tbot as bot
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


def handle_awaiting_add_comment_transaction(call: CallbackQuery, redis: RedisWrapper):
    bot.send_message(
        chat_id=call.message.chat.id,
        text="Додайте коментар👇",
    )

    redis.set_transaction_status(
        user_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=call.message.text,
        status=TransactionStatus.ADD_COMMENT
    )


def handle_awaiting_update_price_transaction(call: CallbackQuery, redis: RedisWrapper):
    bot.send_message(
        chat_id=call.message.chat.id,
        text="Вкажіть оновлену суму👇",
    )

    redis.set_transaction_status(
        user_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=call.message.text,
        status=TransactionStatus.UPDATE_PRICE
    )


def handle_add_comment_transaction(message: Message, redis: RedisWrapper):
    transaction_data = redis.get_transaction_status(user_id=message.chat.id)
    transaction_text = transaction_data["text"]
    if get_comment(text=transaction_text) == "відсутній":
        transaction_text = re.sub(r"Коментар: відсутній", f"Коментар: {message.text}", transaction_text)
    else:
        previous_comment = re.search(r"Коментар: (.+?)\n", transaction_text)[1]
        transaction_text = transaction_text.replace(previous_comment, f"{previous_comment}. {message.text}")

    edit_message(
        chat_id=message.chat.id,
        message_id=transaction_data["message_id"],
        text=transaction_text,
        reply_markup=transaction_menu(),
    )

    redis.set_transaction_status(
        user_id=message.from_user.id,
        status=TransactionStatus.IDLE
    )

    bot.send_message(
        chat_id=message.chat.id,
        text="Коментар додано✅",
    )


def handle_update_price_transaction(message: Message, redis: RedisWrapper):
    try:
        float(message.text)
    except ValueError:
        bot.send_message(
            chat_id=message.chat.id,
            text="Неправильна сума. Має бути в форматі 00.00",
        )
        redis.set_transaction_status(
            user_id=message.from_user.id,
            status=TransactionStatus.IDLE
        )
        return

    transaction_data = redis.get_transaction_status(user_id=message.chat.id)
    transaction_text = transaction_data["text"]
    amount = get_amount(text=transaction_text)
    transaction_text = transaction_text.replace(amount, message.text)

    edit_message(
        chat_id=message.chat.id,
        message_id=transaction_data["message_id"],
        text=transaction_text,
        reply_markup=transaction_menu(),
    )

    bot.send_message(
        chat_id=message.chat.id,
        text="Суму оновлено✅",
    )

    redis.set_transaction_status(
        user_id=message.from_user.id,
        status=TransactionStatus.IDLE
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
