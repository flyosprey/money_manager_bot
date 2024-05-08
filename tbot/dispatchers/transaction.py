from telebot.types import CallbackQuery

from money_manager.config import Config
from tbot.controllers.transaction import add_transaction
from tbot.dependencies.redis import RedisWrapper
from tbot.utils import edit_message


def handle_accept_transaction(call: CallbackQuery, config: Config, redis: RedisWrapper):
    add_transaction(
        user_id=call.from_user.id,
        base_url=config.walletapp.base_url,
        secret_key=config.secret_key,
        transaction=redis.get_transaction_details(
            chat_id=call.message.chat.id, message_id=call.message.id
        ),
    )

    edit_message(
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        text=f"{call.message.text}\n\nЗаписано ✅",
    )


def handle_reject_transaction(call: CallbackQuery, redis: RedisWrapper):
    edit_message(
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        text=f"{call.message.text}\n\nВідхилено 🚫",
    )
    redis.delete_transaction_details(
        chat_id=call.message.chat.id, message_id=call.message.id
    )
