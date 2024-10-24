import re
import time
from contextlib import suppress
from datetime import datetime

import dateutil.parser
import pytz
import structlog
from django.urls import reverse
from random_user_agent.params import OperatingSystem, SoftwareName
from random_user_agent.user_agent import UserAgent
from telebot.apihelper import ApiTelegramException
from telebot.types import InlineKeyboardMarkup, Message

from money_manager.config import TIMEZONE_UTC, config
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
    with suppress(ApiTelegramException):
        bot.delete_message(
            chat_id=message.chat.id,
            message_id=message.message_id,
        )


def normalize_credential(credential: str) -> str:
    return credential.strip()


def get_field_value_from_text(
    text: str, pattern: str, group_indexes: tuple = (0,)
) -> str:
    value = re.search(pattern, text)
    if value:
        for group_index in group_indexes:
            if value[group_index]:
                return value[group_index].strip()

    logger.error("Cannot to fetch date from text! Pattern %s | text %s", pattern, text)
    raise ValueError(f"Cannot to fetch date from text! Pattern {pattern} | text {text}")


def get_unix_time(seconds: int = 0) -> int:
    return int(time.time()) - seconds


def convert_money(money_in_cents: int) -> float:
    if not money_in_cents:
        return money_in_cents

    return float(money_in_cents / 100)


def convert_timestamp_to_datetime(
    timestamp: int, timezone: pytz.timezone = TIMEZONE_UTC
) -> datetime:
    datetime_ = pytz.utc.localize(datetime.fromtimestamp(timestamp))
    if datetime_:
        datetime_ = datetime_.astimezone(timezone)

    return datetime_


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


def admin_bot_notification(message: str):
    bot.send_message(
        chat_id=config.bot_admin.chat_id,
        text=message,
    )


def get_random_user_agent() -> (str, str):
    software_names = [SoftwareName.CHROME.value]
    operating_systems = [OperatingSystem.WINDOWS.value]
    user_agent_rotator = UserAgent(
        software_names=software_names, operating_systems=operating_systems, limit=100
    )
    while True:
        user_agent = user_agent_rotator.get_random_user_agent()
        chrome_version = re.search(r"Chrome/(\d+)?\.", user_agent)
        chrome_version = chrome_version[1] if chrome_version else chrome_version

        if chrome_version:
            return user_agent, chrome_version
