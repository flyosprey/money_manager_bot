import re
from contextlib import suppress
from functools import wraps

import structlog
from telebot.apihelper import ApiTelegramException
from telebot.types import CallbackQuery

from tbot.controllers.transaction import get_transaction_from_message
from tbot.dto.walletapp.mcc_codes import MCCTransactionCategoryName
from tbot.errors import IncorrectMCCCodeError, InvalidCredentialsError
from tbot.utils import admin_bot_notification, edit_message
from tbot_base.bot import tbot as bot

logger = structlog.get_logger(__name__)


def exception_handler():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            chat_id, text, msg_id = get_message_info(msg=args[0])
            try:
                return func(*args, **kwargs)
            except IncorrectMCCCodeError as e:
                logger.error(e, user_id=chat_id)

                admin_bot_notification(message=str(e))

                text = text.replace(
                    "Категорія транзакції наразі не підтримується! Спробуйте пізніше.",
                    "",
                )
                edit_message(
                    chat_id=chat_id,
                    message_id=msg_id,
                    text=f"{text}\n\nКатегорія транзакції наразі не підтримується! Спробуйте пізніше.",
                )
                return
            except InvalidCredentialsError as e:
                logger.error(e, user_id=chat_id)
                bot.send_message(
                    chat_id=chat_id,
                    text="Невірні облікові дані для WalletApp!🔴",
                )
                return
            except Exception as e:
                logger.error(str(e), user_id=chat_id)
                bot.send_message(
                    chat_id=chat_id,
                    text="Щось пішло не так!🔴 Спробуйте пізніше.🕐",
                )

                admin_bot_notification(message=str(e))
                return

        return wrapper

    return decorator


def update_message_category(
    chat_id: int,
    message_id: int,
    text: str,
):
    if "невідома категорія" not in text:
        return

    transaction = get_transaction_from_message(text)
    category = MCCTransactionCategoryName[transaction.type].get(transaction.mcc)
    if not category:
        return

    text = re.sub(
        r":.+?невідома категорія.+?\)", f": {category} ({transaction.mcc})", text
    )
    with suppress(ApiTelegramException):
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text)


def get_message_info(msg) -> (str, str, str):
    if isinstance(msg, CallbackQuery):
        return (
            msg.message.chat.id,
            msg.message.text,
            msg.message.id,
        )
    return msg.chat.id, msg.text, msg.id


def unknown_category_message_handler():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            chat_id, text, msg_id = get_message_info(msg=args[0])
            try:
                return func(*args, **kwargs)
            finally:
                update_message_category(
                    chat_id=chat_id,
                    message_id=msg_id,
                    text=text,
                )
                return

        return wrapper

    return decorator
