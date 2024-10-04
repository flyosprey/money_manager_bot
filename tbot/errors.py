from functools import wraps

import structlog
from telebot.types import CallbackQuery

from tbot.utils import edit_message
from tbot_base.bot import tbot as bot

logger = structlog.get_logger(__name__)


def exception_handler():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            msg = args[0]
            if isinstance(msg, CallbackQuery):
                user_id, text, msg_id = (
                    msg.message.from_user.id,
                    msg.message.text,
                    msg.message.id,
                )
            else:
                user_id, text, msg_id = msg.from_user.id, msg.text, msg.id
            try:
                return func(*args, **kwargs)
            except IncorrectMCCCodeError as e:
                logger.error(e, user_id=user_id)

                text = text.replace(
                    "Категорія транзакції наразі не підтримується! Спробуйте пізніше.",
                    "",
                )
                edit_message(
                    chat_id=user_id,
                    message_id=msg_id,
                    text=f"{text}\n\nКатегорія транзакції наразі не підтримується! Спробуйте пізніше.",
                )
                return
            except InvalidCredentialsError as e:
                logger.error(e, user_id=user_id)
                bot.send_message(
                    chat_id=user_id,
                    text="Невірні облікові дані для WalletApp!🔴",
                )
                return
            except Exception as e:
                logger.error(str(e), user_id=user_id)
                bot.send_message(
                    chat_id=user_id,
                    text="Щось пішло не так!🔴 Спробуйте пізніше.🕐",
                )
                return

        return wrapper

    return decorator


class IncorrectMCCCodeError(Exception):
    def __init__(self, mcc_code: int, message: str):
        self.mcc_code = mcc_code
        self.message = message

    def __str__(self):
        return f"{self.mcc_code}: {self.message}"


class MonoExceptionError(Exception):
    pass


class RetryExceededError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class EncryptManagerError(Exception):
    pass


class EncodeExceptionError(EncryptManagerError):
    pass


class DecodeExceptionError(EncryptManagerError):
    pass
