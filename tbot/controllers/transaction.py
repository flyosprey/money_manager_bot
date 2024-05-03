from pydantic import SecretStr

from tbot.clients.walletapp.dto.mcc_codes import MCCCodeCategory
from tbot.clients.walletapp.manager.manager import MoneyManager
from tbot.dto.transactions.payload import SimpleTransaction
from tbot.utils import convert_money, convert_timestamp_to_datetime
from tbot_base.models import BotUsers
from tbot_base.security.encrypting import EncryptManager


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
            contractor=transaction.contractor
        )
