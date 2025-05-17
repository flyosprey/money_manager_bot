from pydantic.types import SecretStr

from tbot.clients.walletapp_api.client import CloudWalletAppClient, WalletAppClient
from tbot_base.repository.user_integration import UserIntegrationRepository
from tbot_base.repository.wallet_label import UserWalletLabelRepository
from tbot_base.security.encrypting import EncryptManager


def add_label(label: str, user_id: int, secret_key: SecretStr):
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
    label_id = CloudWalletAppClient(
        owner_id=owner_id, owner_id_token=owner_id_token
    ).add_label(label=label)
    UserWalletLabelRepository().upsert(user_id=user_id, label_id=label_id, name=label)
