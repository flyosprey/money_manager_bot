from pydantic import SecretStr

from tbot.clients.walletapp.dto.mcc_codes import MCCCodeCategory
from tbot.clients.walletapp.manager.manager import MoneyManager
from tbot.dto.transactions.payload import SimpleTransaction
from tbot.utils import (
    convert_datetime_to_timestamp,
    convert_money,
    convert_timestamp_to_datetime,
    get_field_value_from_text,
)
from tbot_base.models import BotUsers
from tbot_base.security.encrypting import EncryptManager


def get_transaction_from_message(text: str) -> SimpleTransaction:
    description = get_field_value_from_text(
        text=text, pattern=r"Опис - (.+?)\n", group_index=1
    )
    amount = get_field_value_from_text(
        text=text, pattern=r"Сума - .(.+?)\n", group_index=1
    )
    mcc = get_field_value_from_text(text=text, pattern=r"MCC - (.+)", group_index=1)
    comment = get_field_value_from_text(
        text=text, pattern=r"Коментар - (.+?)\n", group_index=1
    )
    time = get_field_value_from_text(
        text=text, pattern=r"Дата - (.+?)\n", group_index=1
    )
    return SimpleTransaction(
        mcc=int(mcc),
        amount=float(amount) * 100,
        note=comment if comment != "відсутній" else None,
        time=convert_datetime_to_timestamp(time_=time),
        contractor=description,
    )


def add_transaction(
    transaction: SimpleTransaction, user_id: int, base_url: str, secret_key: SecretStr
):
    user = BotUsers.objects.get(user_id=user_id)
    integration = user.integration
    with MoneyManager(
        username=integration.wallet_app_login,
        password=EncryptManager(secret_key=secret_key).decrypt_key(
            integration.wallet_app_password
        ),
        base_url=base_url,
    ) as manager:
        manager.create_transaction(
            amount=convert_money(money_in_cents=transaction.amount),
            note=transaction.note,
            category=MCCCodeCategory[transaction.mcc],
            date=convert_timestamp_to_datetime(timestamp=transaction.time),
            contractor=transaction.contractor,
        )
