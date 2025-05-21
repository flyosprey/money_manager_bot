from telebot.types import Message

from tbot.ai.gpt import LLMAssistant
from tbot.dependencies.redis import RedisWrapper
from tbot.dto.users.type import UserStates
from tbot_base.bot import tbot as bot


def handle_awaiting_question_to_ai(message: Message, redis: RedisWrapper):
    bot.send_message(chat_id=message.chat.id, text="Напишіть питання раднику.")
    redis.set_user_state(message.from_user.id, state=UserStates.QUESTION_TO_AI)


def handle_question_to_ai(message: Message, redis: RedisWrapper):
    llm = LLMAssistant(user_id=message.from_user.id)
    response = llm.ask(query=message.text)
    bot.send_message(chat_id=message.chat.id, text=response.content)
    redis.set_user_state(message.from_user.id, state=UserStates.IDLE)


def handle_ai_advice(message: Message):
    llm = LLMAssistant(user_id=message.from_user.id)
    response = llm.ask(query="Give me an advice based on my transactions")
    bot.send_message(chat_id=message.chat.id, text=response.content)
