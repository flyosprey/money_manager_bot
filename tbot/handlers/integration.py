from telebot.types import Message

from money_manager.config import config
from tbot.dependencies.redis import RedisWrapper
from tbot.dispatchers.integration import (
    handle_ask_reset,
    handle_integration,
    handle_mono_token,
    handle_reset,
    handle_walletapp_password,
    handle_walletapp_username,
)
from tbot.dto.users.type import UserStates
from tbot.utils import exception_handler
from tbot_base.bot import tbot as bot


@bot.message_handler(commands=["integrate"])
def integrate_handler(
    message: Message, redis: RedisWrapper = RedisWrapper(dsn=config.redis.url)
):
    handle_integration(message=message, redis=redis)


@bot.message_handler(commands=["additional_monobank_token"])
def additional_mono_token_handler(
    message: Message, redis: RedisWrapper = RedisWrapper(dsn=config.redis.url)
):
    handle_integration(message=message, redis=redis)


@bot.message_handler(
    func=lambda message: RedisWrapper(dsn=config.redis.url).get_user_state(
        message.from_user.id
    )
    in {UserStates.AWAITING_MONOTOKEN, UserStates.AWAITING_ADDITIONAL_MONOTOKEN}
)
def mono_token_handler(
    message: Message, redis: RedisWrapper = RedisWrapper(dsn=config.redis.url)
):
    handle_mono_token(message=message, redis=redis, dsn=config.dsn)


@bot.message_handler(
    func=lambda message: RedisWrapper(dsn=config.redis.url).get_user_state(
        message.from_user.id
    )
    == UserStates.AWAITING_WALLETAPP_USERNAME
)
def walletapp_username_handler(
    message: Message, redis: RedisWrapper = RedisWrapper(dsn=config.redis.url)
):
    handle_walletapp_username(message=message, redis=redis)


@bot.message_handler(
    func=lambda message: RedisWrapper(dsn=config.redis.url).get_user_state(
        message.from_user.id
    )
    == UserStates.AWAITING_WALLETAPP_PASSWORD
)
def walletapp_password_handler(
    message: Message, redis: RedisWrapper = RedisWrapper(dsn=config.redis.url)
):
    handle_walletapp_password(message=message, redis=redis)


@bot.message_handler(commands=["reset_token", "reset_password"])
@exception_handler()
def ask_reset_handler(
    message: Message, redis: RedisWrapper = RedisWrapper(dsn=config.redis.url)
):
    handle_ask_reset(message=message, redis=redis)


@bot.message_handler(
    func=lambda message: RedisWrapper(dsn=config.redis.url).get_user_state(
        message.from_user.id
    )
    in {UserStates.RESET_WALLETAPP_PASSWORD, UserStates.RESET_MONOTOKEN}
)
@exception_handler()
def reset_handler(
    message: Message, redis: RedisWrapper = RedisWrapper(dsn=config.redis.url)
):
    handle_reset(message=message, redis=redis, dsn=config.dsn)
