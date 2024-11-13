from pydantic import SecretStr

from tbot.clients.walletapp.client import CloudWalletAppClient, WalletAppClient
from tbot.dto.transactions.payload import SimpleTransaction
from tbot.dto.walletapp.mcc_codes import MCCCodeCategory
from tbot.errors import IncorrectMCCCodeError
from tbot.utils import (
    convert_datetime_to_timestamp,
    get_field_value_from_text,
)
from tbot_base.repository.user_integration import UserIntegrationRepository
from tbot_base.security.encrypting import EncryptManager


def get_transaction_from_message(text: str) -> SimpleTransaction:
    description = get_field_value_from_text(
        text=text, pattern=r"Опис: (.+?)\n", group_indexes=(1,)
    )
    amount = get_field_value_from_text(
        text=text, pattern=r"Сума: (.+?\d+?\.(\d+)?)", group_indexes=(1,)
    )
    mcc = get_field_value_from_text(
        text=text, pattern=r"Категорія:.+?\((.+?)\)|MCC: (.+)", group_indexes=(1, 2)
    )
    comment = get_field_value_from_text(
        text=text, pattern=r"Коментар: (.+?)\n", group_indexes=(1,)
    )
    commission = get_field_value_from_text(
        text=text, pattern=r"Комісія: (.+)", group_indexes=(1,)
    )
    cashback = get_field_value_from_text(
        text=text, pattern=r"Кешбек: (.+)", group_indexes=(1,)
    )
    time = get_field_value_from_text(
        text=text, pattern=r"Дата: (.+?)\n", group_indexes=(1,)
    )

    amount = int(float(amount) * 100)

    return SimpleTransaction(
        mcc=int(mcc),
        amount=amount,
        note=f"Коментар: {comment}. Кешбек: {cashback}. Комісія: {commission}",
        time=convert_datetime_to_timestamp(time_=time),
        contractor=description,
        type="+" if amount > 0 else "-",
    )


def add_transaction(
    transaction: SimpleTransaction, user_id: int, secret_key: SecretStr
):
    validate_transaction_to_add(transaction=transaction)
    integration = UserIntegrationRepository.select(
        user_id=user_id,
        wallet_app_password__isnull=False,
        wallet_app_login__isnull=False,
        first=True,
    )[0]
    encrypter = EncryptManager(secret_key=secret_key)

    owner_id, owner_id_token = WalletAppClient().login(
        username=encrypter.decrypt_key(integration.wallet_app_login),
        password=encrypter.decrypt_key(integration.wallet_app_password),
    )
    CloudWalletAppClient(owner_id=owner_id, owner_id_token=owner_id_token).add_record(
        transaction=transaction
    )


def validate_transaction_to_add(transaction: SimpleTransaction) -> None:
    if not MCCCodeCategory[transaction.type][transaction.mcc].startswith("-Category_"):
        raise IncorrectMCCCodeError(
            message="MCC code is not supported yet", mcc_code=transaction.mcc
        )
