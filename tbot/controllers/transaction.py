from pydantic import SecretStr

from money_manager.config import TIMEZONE_KYIV
from tbot.clients.walletapp_api.client import CloudWalletAppClient, WalletAppClient
from tbot.controllers.ai import delete_from_ai_memory, save_to_ai_memory
from tbot.dto.transactions.payload import SimpleTransaction
from tbot.dto.walletapp_api.mcc_codes import MCCCodeCategory
from tbot.errors import IncorrectMCCCodeError
from tbot.utils import (
    convert_datetime_to_timestamp,
    convert_timestamp_to_datetime,
    get_field_value_from_text,
)
from tbot_base.repository.user_categories import UserCategoriesRepository
from tbot_base.repository.user_integration import UserIntegrationRepository
from tbot_base.repository.user_transaction import UserTransactionsRepository
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
        text=text,
        pattern=r"Мітка: (.+)",
        group_indexes=(1,),
        skip_error=True,
    )


def modify_date_to_new(transaction_text: str, seconds_diff: int = 1) -> str:
    date_ = get_time(text=transaction_text)
    new_time = convert_datetime_to_timestamp(time_=date_) + seconds_diff
    new_date = convert_timestamp_to_datetime(
        timestamp=new_time, timezone=TIMEZONE_KYIV
    ).replace(tzinfo=None)

    return transaction_text.replace(date_, str(new_date))


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
    transaction.category_id = get_category_id(
        mcc=transaction.mcc, category_type=transaction.type, user_id=user_id
    )
    transaction.label_id = get_label_id(
        user_id=user_id, label_name=transaction.label_name
    )

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
    transaction_id, body = CloudWalletAppClient(
        owner_id=owner_id, owner_id_token=owner_id_token
    ).add_transaction(transaction=transaction)

    UserTransactionsRepository.insert(
        user_id=user_id, id=transaction_id, doc_id=transaction.time, body=body
    )

    save_to_ai_memory(user_id, transaction)


def delete_transaction(doc_id: int, user_id: int, secret_key: SecretStr):
    transaction = UserTransactionsRepository.select(
        user_id=user_id, doc_id=doc_id, first=True
    )
    if not transaction:
        return

    transaction = transaction[0]
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
    ).delete_transaction(transaction_payload=transaction.body)

    delete_from_ai_memory(user_id, doc_id)

    UserTransactionsRepository.delete(user_id=user_id, doc_id=doc_id)


def get_category_id(mcc: int, category_type: str, user_id: int) -> str:
    category = UserCategoriesRepository.select(
        user_id=user_id,
        name=MCCCodeCategory[category_type].get(mcc, ""),
        first=True,
    )
    if not category:
        raise IncorrectMCCCodeError(
            message="MCC code is not supported yet", mcc_code=mcc
        )

    return category[0].category_id
