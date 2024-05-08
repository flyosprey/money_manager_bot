from tbot.clients.monobank.mono_client import MonobankClient
from tbot.clients.walletapp.manager.manager import MoneyManager
from tbot.dependencies.redis import RedisWrapper
from tbot.dto.users.type import UserStates
from tbot_base.models import UserIntegrations


def is_integration_exist(user_id: int) -> bool:
    return UserIntegrations.objects.filter(user_id=user_id).exists()


def check_mono_token(mono_token: str, base_url: str):
    client = MonobankClient(base_url=base_url)
    client.get_client_info(token=mono_token)


def check_walletapp_credentials(
    username: str, password: str, base_url: str, user_id: int, redis: RedisWrapper
):
    if redis.get_user_state(user_id=user_id) == UserStates.AWAITING_WALLETAPP_PASSWORD:
        redis.set_user_state(user_id=user_id, state=UserStates.IDLE)
        with MoneyManager(
            username=username, password=password, base_url=base_url
        ) as manager:
            manager.login()


def save_all_credentials(
    user_id: int,
    mono_token: str,
    walletapp_username: str,
    walletapp_password: str,
):
    UserIntegrations(
        user_id=user_id,
        monobank_token=mono_token,
        wallet_app_password=walletapp_password,
        wallet_app_login=walletapp_username,
    ).save()
