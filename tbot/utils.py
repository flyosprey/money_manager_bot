import re
import time
from contextlib import suppress
from datetime import datetime
from functools import wraps

import dateutil.parser
import pytz
import structlog
from django.urls import reverse
from selenium.common.exceptions import WebDriverException
from telebot.apihelper import ApiTelegramException
from telebot.types import CallbackQuery, InlineKeyboardMarkup, Message

from money_manager.config import TIMEZONE_UTC
from tbot.errors import IncorrectMCCCodeError, InvalidCredentialsError
from tbot_base.bot import tbot as bot

logger = structlog.get_logger()


CURRENCY_NUMBERS = {
    980: {"code": "UAH", "symbol": "₴"},
    840: {"code": "USD", "symbol": "$"},
    978: {"code": "EUR", "symbol": "€"},
}


def exception_handler():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            msg = args[0]
            if isinstance(msg, CallbackQuery):
                chat_id, user_id = msg.message.chat.id, msg.message.from_user.id
            else:
                chat_id, user_id = msg.chat.id, msg.from_user.id
            try:
                return func(*args, **kwargs)
            except IncorrectMCCCodeError as e:
                logger.error(e, user_id=user_id)
                bot.send_message(
                    chat_id=chat_id,
                    text="Категорія транзакції наразі не підтримується! Спробуйте пізніше.",
                )
                return
            except InvalidCredentialsError as e:
                logger.error(e, user_id=user_id)
                bot.send_message(
                    chat_id=chat_id,
                    text="Невірні облікові дані для WalletApp!🚫",
                )
                return
            except WebDriverException as e:
                logger.error(e.msg, user_id=user_id)
                bot.send_message(
                    chat_id=chat_id,
                    text="Виникла помилка перевірки облікових даних!🤷‍♂️ Спробуйте знову /integrate.",
                )
                return
            except Exception as e:
                logger.error(str(e), user_id=user_id)
                bot.send_message(
                    chat_id=chat_id,
                    text="Щось пішло не так! Спробуйте пізніше.",
                )
                return

        return wrapper

    return decorator


def absolute_endpoint_path(dsn: str, view_name: str, args: list) -> str:
    return f"{dsn}{reverse(view_name, args=args)}"


def delete_message(message: Message):
    with suppress(ApiTelegramException):
        bot.delete_message(
            chat_id=message.chat.id,
            message_id=message.message_id,
        )


def normalize_credential(credential: str) -> str:
    return credential.strip()


def get_field_value_from_text(
    text: str, pattern: str, group_index: int = 0
) -> str | None:
    value = re.search(pattern, text)
    if value:
        return value[group_index].strip()

    return None


def get_unix_time(seconds: int = 0) -> int:
    return int(time.time()) - seconds


def convert_money(money_in_cents: int) -> float:
    if not money_in_cents:
        return money_in_cents

    return float(money_in_cents / 100)


def convert_timestamp_to_datetime(
    timestamp: int, timezone: pytz.timezone = TIMEZONE_UTC
) -> datetime:
    return pytz.utc.localize(datetime.fromtimestamp(timestamp)).astimezone(timezone)


def convert_datetime_to_timestamp(time_: str | datetime) -> int:
    converted = (
        dateutil.parser.parse(time_).timestamp()
        if isinstance(time_, str)
        else time_.timestamp()
    )

    return int(converted)


def convert_currency_number_to_code(currency_number: int) -> str:
    return CURRENCY_NUMBERS.get(currency_number, {}).get("code", "")


def convert_currency_number_to_symbol(currency_number: int) -> str:
    return CURRENCY_NUMBERS.get(currency_number, {}).get("symbol", "")


def edit_message(
    chat_id: int,
    message_id: int,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
):
    with suppress(ApiTelegramException):
        bot.edit_message_text(
            chat_id=chat_id, message_id=message_id, text=text, reply_markup=reply_markup
        )
