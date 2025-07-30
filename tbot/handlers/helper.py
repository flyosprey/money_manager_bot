from telebot.types import CallbackQuery, Message

from money_manager.config import config
from tbot.decorators import exception_handler
from tbot.dependencies.redis import RedisWrapper
from tbot.dispatchers.helper import (
    handle_go_back_menu,
    handle_refresh_monobank,
    handle_setup_categories,
)
from tbot_base.bot import tbot as bot


@bot.message_handler(
    func=lambda message: "Оновити звʼязок з Monobank" in message.text
    or "refresh_monobank" in message.text
)
@exception_handler()
def refresh_monobank_handler(message: Message):
    handle_refresh_monobank(message=message, dsn=config.dsn)


@bot.callback_query_handler(func=lambda call: call.data == "go_back_menu")
@exception_handler()
def go_back_menu_handler(call: CallbackQuery):
    handle_go_back_menu(call=call)


@bot.message_handler(
    func=lambda message: message.text in ("Налаштувати аккаунт", "/setup_categories")
)
@exception_handler()
def setup_categories_handler(
    message: Message, redis: RedisWrapper = RedisWrapper(dsn=config.redis.url)
):
    handle_setup_categories(message=message, redis=redis)
