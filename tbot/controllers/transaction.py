from pydantic import SecretStr

from tbot.clients.walletapp.manager.manager import MoneyManager
from tbot.dto.transactions.payload import SimpleTransaction
from tbot.dto.walletapp.mcc_codes import MCCCodeCategory
from tbot.errors import IncorrectMCCCodeError
from tbot.utils import (
    convert_datetime_to_timestamp,
    convert_money,
    convert_timestamp_to_datetime,
    get_field_value_from_text,
)
from tbot_base.repository.user_integration import UserIntegrationRepository
from tbot_base.security.encrypting import EncryptManager


def get_transaction_from_message(text: str) -> SimpleTransaction:
    description = get_field_value_from_text(
        text=text, pattern=r"Опис: (.+?)\n", group_index=1
    )
    amount = get_field_value_from_text(
        text=text, pattern=r"Сума: (.+?).\n", group_index=1
    )
    mcc = get_field_value_from_text(text=text, pattern=r"MCC: (.+)", group_index=1)
    comment = get_field_value_from_text(
        text=text, pattern=r"Коментар: (.+?)\n", group_index=1
    )
    commission = get_field_value_from_text(text=text, pattern=r"Комісія: (.+)", group_index=1)
    cashback = get_field_value_from_text(text=text, pattern=r"Кешбек: (.+)", group_index=1)
    time = get_field_value_from_text(text=text, pattern=r"Дата: (.+?)\n", group_index=1)

    return SimpleTransaction(
        mcc=int(mcc),
        amount=int(float(amount) * 100),
        note=f"Коментар: {comment}. Кешбек: {cashback}. Комісія: {commission}",
        time=convert_datetime_to_timestamp(time_=time),
        contractor=description,
    )


def add_transaction(
    transaction: SimpleTransaction, user_id: int, base_url: str, secret_key: SecretStr
):
    validate_transaction_to_add(transaction)
    integration = UserIntegrationRepository.select(
        user_id=user_id,
        wallet_app_password__isnull=False,
        wallet_app_login__isnull=False,
        first=True,
    )[0]
    encrypter = EncryptManager(secret_key=secret_key)
    with MoneyManager(
        username=encrypter.decrypt_key(integration.wallet_app_login),
        password=encrypter.decrypt_key(integration.wallet_app_password),
        base_url=base_url,
    ) as manager:
        manager.create_transaction(
            amount=convert_money(money_in_cents=transaction.amount),
            note=transaction.note,
            category=MCCCodeCategory[transaction.mcc],
            date_time=convert_timestamp_to_datetime(timestamp=transaction.time),
            contractor=transaction.contractor,
        )


def validate_transaction_to_add(transaction: SimpleTransaction):
    if isinstance(MCCCodeCategory[transaction.mcc], str):
        raise IncorrectMCCCodeError(
            message="MCC code is not supported yet", mcc_code=transaction.mcc
        )
