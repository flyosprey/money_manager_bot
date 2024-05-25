import re
import time
from datetime import datetime

import pytz
import structlog
from django.urls import reverse
from telebot.apihelper import ApiTelegramException
from telebot.types import InlineKeyboardMarkup, Message

from money_manager.config import TIMEZONE_UTC
from tbot_base.bot import tbot as bot

logger = structlog.get_logger()


CURRENCY_NUMBERS = {
    980: {"code": "UAH", "symbol": "₴"},
    840: {"code": "USD", "symbol": "$"},
    978: {"code": "EUR", "symbol": "€"},
}


def absolute_endpoint_path(dsn: str, view_name: str, args: list) -> str:
    return f"{dsn}{reverse(view_name, args=args)}"


def delete_message(message: Message):
    try:
        bot.delete_message(
            chat_id=message.chat.id,
            message_id=message.message_id,
        )
    except ApiTelegramException as e:
        if (
            e.result.status_code == 400
            and "message to delete not found" in e.result.text
        ):
            logger.debug("Attempted to delete not founded message.")


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


def convert_datetime_to_timestamp(
    time_: str | datetime, format_: str = "%Y-%m-%d %H:%M:%S"
) -> int:
    converted = (
        datetime.strptime(time_, format_).timestamp()
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
    try:
        bot.edit_message_text(
            chat_id=chat_id, message_id=message_id, text=text, reply_markup=reply_markup
        )
    except ApiTelegramException as e:
        if e.result.status_code == 400 and "message is not modified" in e.result.text:
            logger.debug("Attempted to edit message with no changes.")
