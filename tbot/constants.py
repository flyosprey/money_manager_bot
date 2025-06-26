from enum import Enum


class CurrencyCodes(Enum):
    UAH = 980
    USD = 840
    EUR = 978


class TransactionTypes(str, Enum):
    INCOME = "+"
    OUTCOME = "-"

    @classmethod
    def from_amount(cls, amount: float) -> "TransactionTypes":
        return cls.INCOME if amount >= 0 else cls.OUTCOME


DEFAULT_CURRENCY_CODE = CurrencyCodes.UAH.value
MINIMUM_ALLOWED_TRANSACTION_AMOUNT = 1
TOTAL_CATEGORIES_COUNT = 79

CURRENCIES_CODES_MAPPING = {
    CurrencyCodes.UAH.value: {"code": "UAH", "symbol": "₴"},
    CurrencyCodes.USD.value: {"code": "USD", "symbol": "$"},
    CurrencyCodes.EUR.value: {"code": "EUR", "symbol": "€"},
}
