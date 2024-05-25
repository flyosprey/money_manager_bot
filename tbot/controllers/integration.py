from requests.exceptions import RequestException
from telebot.types import Message

from tbot.clients.monobank.mono_client import MonobankClient, MonoExceptionError
from tbot.clients.walletapp.manager.manager import MoneyManager
from tbot.dependencies.redis import RedisWrapper
from tbot.dto.users.type import UserStates
from tbot.utils import absolute_endpoint_path


def set_monobank_webhook(mono_token: str, base_url: str, webhook_url: str):
    client = MonobankClient(base_url=base_url)
    client.set_webhook(token=mono_token, webhook_url=webhook_url)


def check_monobank(
    dsn: str, mono_token: str, chat_id: int, encrypted_user_id: str, base_url: str
) -> bool:
    webhook_url = absolute_endpoint_path(
        dsn=dsn, view_name="handle_mono_webhook", args=[chat_id, encrypted_user_id]
    )
    try:
        set_monobank_webhook(
            mono_token=mono_token,
            base_url=base_url,
            webhook_url=webhook_url,
        )
    except (RequestException, MonoExceptionError):
        return False

    return True


def check_walletapp_credentials(
    username: str, password: str, base_url: str, user_id: int, redis: RedisWrapper
):
    if redis.get_user_state(user_id=user_id) == UserStates.AWAITING_WALLETAPP_PASSWORD:
        redis.set_user_state(user_id=user_id, state=UserStates.IDLE)
        with MoneyManager(
            username=username, password=password, base_url=base_url
        ) as manager:
            manager.login()
