from telebot.types import CallbackQuery

from money_manager.config import config
from tbot.decorators import exception_handler, unknown_category_message_handler
from tbot.dispatchers.transaction import (
    handle_accept_transaction,
    handle_change_category_transaction,
    handle_reject_transaction,
    handle_select_category_transaction,
)
from tbot.dto.transactions.type import TransactionStatus
from tbot_base.bot import tbot as bot


@bot.callback_query_handler(func=lambda call: call.data == TransactionStatus.ACCEPTED)
@exception_handler()
def accept_transaction_handler(call: CallbackQuery):
    handle_accept_transaction(call=call, config=config)


@bot.callback_query_handler(func=lambda call: call.data == TransactionStatus.REJECTED)
@exception_handler()
@unknown_category_message_handler()
def reject_transaction_handler(call: CallbackQuery):
    handle_reject_transaction(call=call)


@bot.callback_query_handler(func=lambda call: "page_" in call.data)
@exception_handler()
@unknown_category_message_handler()
def select_category_transaction_handler(call: CallbackQuery):
    handle_select_category_transaction(call=call)


@bot.callback_query_handler(func=lambda call: "category_" in call.data)
@exception_handler()
@unknown_category_message_handler()
def change_category_transaction_handler(call: CallbackQuery):
    handle_change_category_transaction(call=call)
