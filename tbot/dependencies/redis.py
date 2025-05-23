import json

from redis.client import Redis
from tbot.dto.transactions.type import TransactionStates
from tbot.dto.users.type import UserStates
from tbot.dto.walletapp_api.type import SettingsStates, SetUpCategoriesStates

USER_STATE_TEMPLATE = "{user_id}_state"
USER_STATUS_TTL = 60 * 60 * 24  # 1 day
TRANSACTION_STATE_TEMPLATE = "{user_id}_transaction_state"
TRANSACTION_STATE_TTL = 60 * 60 * 24  # 1 day
SETTING_STATE_TEMPLATE = "{user_id}_settings_state"
SETTING_STATE_TTL = 60 * 60 * 24  # 1 day
SETUP_CATEGORIES_TEMPLATE = "{user_id}_setup_categories_state"
SETUP_CATEGORIES_TTL = 60 * 60 * 1  # 1 hour


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

    def set_transaction_state(
        self,
        user_id: int,
        state: TransactionStates,
        text: str | None = None,
        message_id: int | None = None,
    ):
        self.redis.set(
            name=TRANSACTION_STATE_TEMPLATE.format(user_id=user_id),
            value=json.dumps(
                {"state": state.value, "message_id": message_id, "text": text}
            ),
            ex=TRANSACTION_STATE_TTL,
        )

    def get_transaction_state(self, user_id: int) -> dict:
        data = self.redis.get(name=TRANSACTION_STATE_TEMPLATE.format(user_id=user_id))

        if not data:
            return {}

        data = json.loads(data)
        data["state"] = TransactionStates(data["state"])

        return data

    def set_settings_state(
        self,
        user_id: int,
        state: SettingsStates,
    ):
        self.redis.set(
            name=SETTING_STATE_TEMPLATE.format(user_id=user_id),
            value=state.value,
            ex=SETTING_STATE_TTL,
        )

    def get_settings_state(self, user_id: int) -> SettingsStates:
        state = self.redis.get(name=SETTING_STATE_TEMPLATE.format(user_id=user_id))

        if not state:
            return SettingsStates.IDLE

        return SettingsStates(int(state.decode()))

    def set_setup_categories_state(
        self,
        user_id: int,
        state: SetUpCategoriesStates,
    ):
        # SENT_TO_SET_UP
        self.redis.set(
            name=SETUP_CATEGORIES_TEMPLATE.format(user_id=user_id),
            value=state.value,
            ex=SETUP_CATEGORIES_TTL,
        )

    def get_setup_categories_state(self, user_id: int) -> SetUpCategoriesStates:
        status = self.redis.get(name=SETUP_CATEGORIES_TEMPLATE.format(user_id=user_id))

        if not status:
            return SetUpCategoriesStates.IDLE

        return SetUpCategoriesStates(int(status.decode()))
