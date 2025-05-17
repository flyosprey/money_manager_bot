from telebot.types import Message

from tbot.decorators import exception_handler
from tbot.dispatchers.ai import handle_ai_advice
from tbot_base.bot import tbot as bot


@bot.message_handler(
    func=lambda message: message.text in ("Порада радника", "/ai_advice")
)
@exception_handler()
def ai_advice_handler(message: Message):
    handle_ai_advice(message=message)
