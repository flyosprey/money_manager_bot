import time
from collections import defaultdict
from datetime import datetime

from tbot.dto.users.type import UserStates

CURRENCY_NUMBERS = {
    980: {"code": "UAH", "symbol": "₴"},
    840: {"code": "USD", "symbol": "$"},
    978: {"code": "EUR", "symbol": "€"},
}


USERS_STATE = defaultdict(dict)
TRANSACTION_DATA = defaultdict(dict)
CREDENTIALS = defaultdict(dict)


def set_user_state(user_id: int, state: UserStates):
    USERS_STATE[user_id]["state"] = state


def get_user_state(user_id: int) -> UserStates:
    return USERS_STATE.get(user_id, {}).get("state", UserStates.IDLE)


def get_unix_time(seconds: int = 0) -> int:
    return int(time.time()) - seconds


def convert_money(money_in_cents: int) -> float:
    if not money_in_cents:
        return money_in_cents
    return float(money_in_cents / 100)


def convert_timestamp_to_datetime(timestamp: int) -> datetime:
    return datetime.fromtimestamp(timestamp)


def convert_currency_number_to_code(currency_number: int) -> str:
    return CURRENCY_NUMBERS.get(currency_number, {}).get("code", "")


def convert_currency_number_to_symbol(currency_number: int) -> str:
    return CURRENCY_NUMBERS.get(currency_number, {}).get("symbol", "")
