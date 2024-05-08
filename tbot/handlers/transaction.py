from telebot.types import CallbackQuery

from money_manager.config import config
from tbot.dependencies.redis import RedisWrapper
from tbot.dispatchers.transaction import (
    handle_accept_transaction,
    handle_reject_transaction,
)
from tbot.dto.transactions.type import TransactionStatus
from tbot_base.bot import tbot as bot


@bot.callback_query_handler(func=lambda call: call.data == TransactionStatus.ACCEPTED)
def accept_transaction_handler(
    call: CallbackQuery, redis: RedisWrapper = RedisWrapper(dsn=config.redis.url)
):
    handle_accept_transaction(call=call, config=config, redis=redis)


@bot.callback_query_handler(func=lambda call: call.data == TransactionStatus.REJECTED)
def reject_transaction_handler(
    call: CallbackQuery, redis: RedisWrapper = RedisWrapper(dsn=config.redis.url)
):
    handle_reject_transaction(call=call, redis=redis)
