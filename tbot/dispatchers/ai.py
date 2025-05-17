from telebot.types import Message

from tbot.ai.gpt import LLMAssistant
from tbot_base.bot import tbot as bot


def handle_ai_advice(message: Message):
    llm = LLMAssistant(user_id=message.from_user.id)
    response = llm.ask(query="Give me an advice based on my transactions")
    bot.send_message(chat_id=message.chat.id, text=response.content)
