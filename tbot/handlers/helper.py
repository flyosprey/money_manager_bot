from telebot.types import Message

from money_manager.config import config
from tbot.dispatchers.helper import (
    handle_refresh_monobank,
)
from tbot.errors import exception_handler
from tbot_base.bot import tbot as bot


@bot.message_handler(
    func=lambda message: "Оновити звʼязок з Monobank" in message.text or "refresh_monobank" in message.text
)
@exception_handler()
def refresh_monobank_handler(message: Message):
    handle_refresh_monobank(message=message, dsn=config.dsn)
