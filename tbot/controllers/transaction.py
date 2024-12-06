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
from tbot_base.repository.wallet_label import UserWalletLabelRepository
from tbot_base.security.encrypting import EncryptManager


def get_comment(text: str) -> str:
    return get_field_value_from_text(
        text=text, pattern=r"Коментар: (.+?)\n", group_indexes=(1,)
    )


def get_amount(text: str) -> str:
    return get_field_value_from_text(
        text=text, pattern=r"Сума: (.+?\d+(\.\d+)?)", group_indexes=(1,)
    )


def get_description(text: str) -> str:
    return get_field_value_from_text(
        text=text, pattern=r"Опис: (.+?)\n", group_indexes=(1,)
    )


def get_mcc(text: str) -> str:
    return get_field_value_from_text(
        text=text, pattern=r"Категорія:.+?\((.+?)\)|MCC: (.+)", group_indexes=(1, 2)
    )


def get_commission(text: str) -> str:
    return get_field_value_from_text(
        text=text, pattern=r"Комісія: (.+)", group_indexes=(1,)
    )


def get_cashback(text: str) -> str:
    return get_field_value_from_text(
        text=text, pattern=r"Кешбек: (.+)", group_indexes=(1,)
    )


def get_time(text: str) -> str:
    return get_field_value_from_text(
        text=text, pattern=r"Дата: (.+?)\n", group_indexes=(1,)
    )


def get_label(text: str) -> str:
    return get_field_value_from_text(
        text=text, pattern=r"Мітка: (.+)", group_indexes=(1,)
    )


def get_transaction_from_message(text: str) -> SimpleTransaction:
    comment = get_comment(text=text)
    amount = get_amount(text=text)
    description = get_description(text=text)
    mcc = get_mcc(text=text)
    commission = get_commission(text=text)
    cashback = get_cashback(text=text)
    time = get_time(text=text)
    label = get_label(text=text)

    amount = int(float(amount) * 100)

    return SimpleTransaction(
        mcc=int(mcc),
        amount=amount,
        note=f"Коментар: {comment}. Кешбек: {cashback}. Комісія: {commission}",
        time=convert_datetime_to_timestamp(time_=time),
        label_name=label,
        contractor=description,
        type="+" if amount > 0 else "-",
    )


def get_label_id(user_id: int, label_name: str) -> str:
    label = UserWalletLabelRepository.select(
        user_id=user_id,
        name=label_name,
        first=True,
    )
    return label[0].label_id if label else None


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
    CloudWalletAppClient(
        owner_id=owner_id, owner_id_token=owner_id_token
    ).add_transaction(transaction=transaction)


def validate_transaction_to_add(transaction: SimpleTransaction) -> None:
    if (
        not MCCCodeCategory[transaction.type]
        .get(transaction.mcc, "")
        .startswith("-Category_")
    ):
        raise IncorrectMCCCodeError(
            message="MCC code is not supported yet", mcc_code=transaction.mcc
        )
