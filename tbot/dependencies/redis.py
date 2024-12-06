import json

from redis.client import Redis  # noqa

from tbot.dto.transactions.type import TransactionStatus
from tbot.dto.users.type import UserStates
from tbot.dto.walletapp.type import SettingsStates

USER_STATE_TEMPLATE = "{user_id}_state"
USER_STATUS_TTL = 60 * 60 * 24  # 1 day
TRANSACTION_STATE_TEMPLATE = "{user_id}_transaction_state"
TRANSACTION_STATUS_TTL = 60 * 60 * 24  # 1 day
SETTING_STATE_TEMPLATE = "{user_id}_settings_state"
SETTING_STATUS_TTL = 60 * 60 * 24  # 1 day


class RedisWrapper:
    def __init__(self, dsn: str):
        self.redis: Redis = Redis.from_url(url=dsn)

    def set_user_state(self, user_id: int, state: UserStates):
        self.redis.set(
            name=USER_STATE_TEMPLATE.format(user_id=user_id),
            value=state.value,
            ex=USER_STATUS_TTL,
        )

    def get_user_state(self, user_id: int) -> UserStates:
        state = self.redis.get(name=USER_STATE_TEMPLATE.format(user_id=user_id))

        if not state:
            return UserStates.IDLE

        return UserStates(int(state.decode()))

    def set_transaction_status(
        self,
        user_id: int,
        status: TransactionStatus,
        text: str | None = None,
        message_id: int | None = None,
    ):
        self.redis.set(
            name=TRANSACTION_STATE_TEMPLATE.format(user_id=user_id),
            value=json.dumps(
                {"status": status.value, "message_id": message_id, "text": text}
            ),
            ex=TRANSACTION_STATUS_TTL,
        )

    def get_transaction_status(self, user_id: int) -> dict:
        status = self.redis.get(name=TRANSACTION_STATE_TEMPLATE.format(user_id=user_id))

        if not status:
            return {}

        return json.loads(status)

    def set_settings_status(
        self,
        user_id: int,
        status: SettingsStates,
    ):
        self.redis.set(
            name=SETTING_STATE_TEMPLATE.format(user_id=user_id),
            value=status.value,
            ex=TRANSACTION_STATUS_TTL,
        )

    def get_settings_status(self, user_id: int) -> SettingsStates:
        status = self.redis.get(name=SETTING_STATE_TEMPLATE.format(user_id=user_id))

        if not status:
            return SettingsStates.IDLE

        return SettingsStates(int(status.decode()))
