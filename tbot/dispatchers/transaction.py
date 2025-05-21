import re

from telebot.types import CallbackQuery, Message

from money_manager.config import Config
from tbot.controllers.transaction import (
    add_transaction,
    delete_transaction,
    get_amount,
    get_comment,
    get_label_id,
    get_transaction_from_message,
)
from tbot.dependencies.redis import RedisWrapper
from tbot.dto.transactions.type import TransactionStatus
from tbot.dto.walletapp_api.mcc_codes import MCCTransactionCategoryName
from tbot.keyboards import (
    transaction_categories_menu,
    transaction_labels_menu,
    transaction_menu,
)
from tbot.utils import delete_message, edit_message
from tbot_base.bot import tbot as bot
from tbot_base.repository.wallet_label import UserWalletLabelRepository


def fix_accept_delete_transaction_message(text: str) -> str:
    return text.replace("\n\nВідхилено🚫", "").replace("\n\nЗаписано✅", "")


def handle_accept_transaction(call: CallbackQuery, config: Config):
    transaction = get_transaction_from_message(call.message.text)
    transaction.label_id = get_label_id(
        user_id=call.from_user.id, label_name=transaction.label_name
    )

    add_transaction(
        user_id=call.from_user.id,
        secret_key=config.secret_key,
        transaction=transaction,
    )

    text = fix_accept_delete_transaction_message(text=call.message.text)
    edit_message(
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        text=f"{text}\n\nЗаписано✅",
        reply_markup=transaction_menu(is_acceptable=False),
    )


def handle_reject_transaction(call: CallbackQuery, config: Config):
    transaction = get_transaction_from_message(call.message.text)
    delete_transaction(
        user_id=call.from_user.id,
        doc_id=transaction.time,
        secret_key=config.secret_key,
    )

    text = fix_accept_delete_transaction_message(text=call.message.text)
    edit_message(
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        text=f"{text}\n\nВідхилено🚫",
        reply_markup=transaction_menu(is_deletable=False),
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
        status=TransactionStatus.ADD_COMMENT,
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
        status=TransactionStatus.UPDATE_PRICE,
    )


def handle_add_comment_transaction(message: Message, redis: RedisWrapper):
    def send_error_message(chat_id, text):
        bot.send_message(chat_id=chat_id, text=text)
        redis.set_transaction_status(
            user_id=message.from_user.id, status=TransactionStatus.IDLE
        )

    transaction_data = redis.get_transaction_status(user_id=message.chat.id)
    transaction_text = transaction_data["text"]
    text = message.text.strip()
    if not text:
        send_error_message(message.chat.id, "Коментар не може бути пустим!")

    if get_comment(text=transaction_text) == "відсутній":
        transaction_text = re.sub(
            r"Коментар: відсутній", f"Коментар: {text}", transaction_text
        )
    else:
        previous_comment = re.search(r"Коментар: (.+?)\n", transaction_text)[1]
        transaction_text = transaction_text.replace(
            previous_comment, f"{previous_comment}. {text}"
        )

    finish_edit_transaction(
        transaction_text=transaction_text,
        transaction_message_id=transaction_data["message_id"],
        message=message,
        redis=redis,
    )


def handle_update_price_transaction(message: Message, redis: RedisWrapper):
    def send_error_message(chat_id, text):
        bot.send_message(chat_id=chat_id, text=text)
        redis.set_transaction_status(
            user_id=message.from_user.id, status=TransactionStatus.IDLE
        )

    try:
        amount = float(message.text.strip())
    except ValueError:
        send_error_message(
            message.chat.id, "Неправильна сума. Має бути в форматі 10.00/-10.00"
        )
        return

    if amount == 0:
        send_error_message(message.chat.id, "Сума не може бути 0")
        return

    transaction_data = redis.get_transaction_status(user_id=message.chat.id)
    transaction_text = transaction_data["text"]
    previous_amount = get_amount(text=transaction_text)
    updated_transaction_text = transaction_text.replace(
        previous_amount, f"{amount:.2f}"
    )

    finish_edit_transaction(
        transaction_text=updated_transaction_text,
        transaction_message_id=transaction_data["message_id"],
        message=message,
        redis=redis,
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


def finish_edit_transaction(
    transaction_text: str,
    transaction_message_id: int,
    message: Message,
    redis: RedisWrapper,
):
    redis.set_transaction_status(
        user_id=message.from_user.id, status=TransactionStatus.IDLE
    )

    bot.send_message(
        chat_id=message.chat.id,
        text=transaction_text,
        reply_markup=transaction_menu(),
    )

    delete_edit_transaction_messages(
        transaction_message_id=transaction_message_id, message=message
    )


def delete_edit_transaction_messages(transaction_message_id: int, message: Message):
    delete_message(
        chat_id=message.chat.id,
        message_id=transaction_message_id,
    )
    delete_message(
        chat_id=message.chat.id,
        message_id=message.message_id - 1,
    )
    delete_message(chat_id=message.from_user.id, message_id=message.message_id)


def handle_awaiting_separate_transaction(call: CallbackQuery, redis: RedisWrapper):
    bot.send_message(
        chat_id=call.message.chat.id,
        text="Вкажіть суми транзакцій через кому/пробіл👇",
    )

    redis.set_transaction_status(
        user_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=call.message.text,
        status=TransactionStatus.SEPARATE_TRANSACTIONS,
    )


def handle_separate_transaction(message: Message, redis: RedisWrapper):
    def send_error_message(chat_id, text):
        bot.send_message(chat_id=chat_id, text=text)
        redis.set_transaction_status(
            user_id=message.from_user.id, status=TransactionStatus.IDLE
        )

    amounts = []
    for amount in re.split(r"\n|\s|,", message.text.strip()):
        try:
            amounts.append(float(amount))
        except ValueError:
            send_error_message(
                message.chat.id, "Неправильна сума. Має бути в форматі 10.00/-10.00"
            )
            return

    transaction_data = redis.get_transaction_status(user_id=message.chat.id)
    transaction_text = transaction_data["text"]
    previous_amount = get_amount(text=transaction_text)
    previous_amount_float = float(previous_amount)
    sum_amounts = sum(amounts)
    if (sum_amounts > 0 > previous_amount_float) or (
        sum_amounts < 0 < previous_amount_float
    ):
        amounts = [amount * -1 for amount in amounts]
        sum_amounts = sum(amounts)

    if sum_amounts != previous_amount_float:
        send_error_message(
            message.chat.id,
            "Сума розділених транзакцій повинна дорівнювати сумі основної транзакції.",
        )
        return

    transactions = []
    for amount in amounts:
        updated_transaction_text = transaction_text.replace(
            previous_amount, f"{amount:.2f}"
        )
        transactions.append(updated_transaction_text)

    delete_edit_transaction_messages(
        transaction_message_id=transaction_data["message_id"], message=message
    )

    for transaction in transactions:
        bot.send_message(
            chat_id=message.chat.id,
            text=transaction,
            reply_markup=transaction_menu(),
        )

    redis.set_transaction_status(
        user_id=message.from_user.id, status=TransactionStatus.IDLE
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


def handle_select_label_transaction(call: CallbackQuery):
    labels = UserWalletLabelRepository.select(
        user_id=call.from_user.id,
        first=False,
    )
    labels = [label.name for label in labels]
    edit_message(
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        text=call.message.text,
        reply_markup=transaction_labels_menu(labels=labels),
    )


def handle_change_label_transaction(call: CallbackQuery):
    label = re.search(r"label_(.+)", call.data)
    if not label:
        raise Exception("call.data label error!")

    text = re.sub(
        r"Мітка:.+",
        f"Мітка: {label[1]}",
        call.message.text,
    )
    edit_message(
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        text=text,
        reply_markup=transaction_menu(),
    )
