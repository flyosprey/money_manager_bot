from telebot.types import Message

from money_manager.config import config
from tbot.decorators import exception_handler, notify_admin_about_action
from tbot.dependencies.redis import RedisWrapper
from tbot.dispatchers.ai import (
    handle_ai_advice,
    handle_awaiting_question_to_ai,
    handle_question_to_ai,
)
from tbot.dto.users.type import UserStates
from tbot_base.bot import tbot as bot


@bot.message_handler(
    func=lambda message: message.text in ("Порада радника", "/ai_advice")
)
@exception_handler()
@notify_admin_about_action(action="ai_advice")
def ai_advice_handler(message: Message):
    handle_ai_advice(message=message)


@bot.message_handler(
    func=lambda message: message.text in ("Запитання раднику", "/question_to_ai")
)
@exception_handler()
@notify_admin_about_action(action="awaiting_ai_question")
def awaiting_question_to_ai_handler(
    message: Message, redis: RedisWrapper = RedisWrapper(dsn=config.redis.url)
):
    handle_awaiting_question_to_ai(message=message, redis=redis)


@bot.message_handler(
    func=lambda message: RedisWrapper(dsn=config.redis.url).get_user_state(
        message.from_user.id
    )
    == UserStates.QUESTION_TO_AI
)
@exception_handler()
@notify_admin_about_action(action="ai_question")
def question_to_ai_handler(
    message: Message, redis: RedisWrapper = RedisWrapper(dsn=config.redis.url)
):
    handle_question_to_ai(message=message, redis=redis)
