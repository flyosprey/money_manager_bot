from requests import RequestException

from tbot.clients.monobank.client import MonobankClient
from tbot.clients.walletapp.client import WalletAppClient
from tbot.dependencies.redis import RedisWrapper
from tbot.dto.users.type import UserStates
from tbot.utils import absolute_endpoint_path


def set_monobank_webhook(mono_token: str, webhook_url: str):
    client = MonobankClient(credentials={"X-Token": mono_token})
    client.set_webhook(webhook_url=webhook_url)


def check_monobank(
    dsn: str,
    mono_token: str,
    encrypted_user_id: str,
) -> bool:
    webhook_url = absolute_endpoint_path(
        dsn=dsn, view_name="handle_mono_webhook", args=[encrypted_user_id]
    )
    try:
        set_monobank_webhook(
            mono_token=mono_token,
            webhook_url=webhook_url,
        )
    except RequestException:
        return False

    return True


def check_walletapp_credentials(
    username: str, password: str, user_id: int, redis: RedisWrapper
):
    if redis.get_user_state(user_id=user_id) == UserStates.AWAITING_WALLETAPP_PASSWORD:
        redis.set_user_state(user_id=user_id, state=UserStates.IDLE)
        WalletAppClient().login(username=username, password=password)
