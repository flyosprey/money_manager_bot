from telebot.types import CallbackQuery, Message

from money_manager.config import config
from tbot.decorators import exception_handler, unknown_category_message_handler
from tbot.dependencies.redis import RedisWrapper
from tbot.dispatchers.transaction import (
    handle_accept_transaction,
    handle_add_comment_transaction,
    handle_awaiting_add_comment_transaction,
    handle_awaiting_separate_transaction,
    handle_awaiting_update_price_transaction,
    handle_change_category_transaction,
    handle_reject_transaction,
    handle_select_category_transaction,
    handle_separate_transaction,
    handle_update_price_transaction,
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


@bot.callback_query_handler(
    func=lambda call: call.data == TransactionStatus.AWAITING_ADD_COMMENT
)
@exception_handler()
@unknown_category_message_handler()
def awaiting_add_comment_transaction_handler(
    call: CallbackQuery, redis: RedisWrapper = RedisWrapper(dsn=config.redis.url)
):
    handle_awaiting_add_comment_transaction(call=call, redis=redis)


@bot.callback_query_handler(
    func=lambda call: call.data == TransactionStatus.AWAITING_UPDATE_PRICE
)
@exception_handler()
@unknown_category_message_handler()
def awaiting_update_price_transaction_handler(
    call: CallbackQuery, redis: RedisWrapper = RedisWrapper(dsn=config.redis.url)
):
    handle_awaiting_update_price_transaction(call=call, redis=redis)


@bot.message_handler(
    func=lambda message: RedisWrapper(dsn=config.redis.url)
    .get_transaction_status(message.from_user.id)
    .get("status")
    in {TransactionStatus.ADD_COMMENT.value}
)
@exception_handler()
@unknown_category_message_handler()
def add_comment_transaction_handler(
    message: Message, redis: RedisWrapper = RedisWrapper(dsn=config.redis.url)
):
    handle_add_comment_transaction(message=message, redis=redis)


@bot.message_handler(
    func=lambda message: RedisWrapper(dsn=config.redis.url)
    .get_transaction_status(message.from_user.id)
    .get("status")
    in {TransactionStatus.UPDATE_PRICE.value}
)
@exception_handler()
@unknown_category_message_handler()
def update_price_transaction_handler(
    message: Message, redis: RedisWrapper = RedisWrapper(dsn=config.redis.url)
):
    handle_update_price_transaction(message=message, redis=redis)


@bot.callback_query_handler(
    func=lambda call: call.data == TransactionStatus.AWAITING_SEPARATE_TRANSACTIONS
)
@exception_handler()
@unknown_category_message_handler()
def awaiting_separate_transaction_handler(
    call: CallbackQuery, redis: RedisWrapper = RedisWrapper(dsn=config.redis.url)
):
    handle_awaiting_separate_transaction(call=call, redis=redis)


@bot.message_handler(
    func=lambda message: RedisWrapper(dsn=config.redis.url)
    .get_transaction_status(message.from_user.id)
    .get("status")
    in {TransactionStatus.SEPARATE_TRANSACTIONS.value}
)
@exception_handler()
@unknown_category_message_handler()
def separate_transaction_handler(
    message: Message, redis: RedisWrapper = RedisWrapper(dsn=config.redis.url)
):
    handle_separate_transaction(message=message, redis=redis)


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
