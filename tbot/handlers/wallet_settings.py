from telebot.types import CallbackQuery, Message

from money_manager.config import config
from tbot.decorators import exception_handler
from tbot.dependencies.redis import RedisWrapper
from tbot.dispatchers.wallet_settings import (
    handle_add_label,
    handle_awaiting_add_label,
    handle_wallet_settings,
)
from tbot.dto.walletapp_api.type import SettingsStates
from tbot_base.bot import tbot as bot


@bot.message_handler(func=lambda message: "Налаштування гаманця обліку" in message.text)
@exception_handler()
def wallet_settings_handler(message: Message):
    handle_wallet_settings(message=message)


@bot.callback_query_handler(
    func=lambda call: int(call.data) == SettingsStates.AWAITING_LABEL.value
)
@exception_handler()
def awaiting_add_label_handler(
    call: CallbackQuery, redis: RedisWrapper = RedisWrapper(dsn=config.redis.url)
):
    handle_awaiting_add_label(call=call, redis=redis)


@bot.message_handler(
    func=lambda message: RedisWrapper(dsn=config.redis.url).get_settings_status(
        message.from_user.id
    )
    == SettingsStates.ADD_LABEL
)
@exception_handler()
def add_label_handler(message: Message):
    handle_add_label(message=message)
