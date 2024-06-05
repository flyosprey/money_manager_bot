from redis.client import Redis  # noqa
from tbot.dto.users.type import UserStates  # noqa

USER_STATE_TEMPLATE = "{user_id}_state"
USER_STATUS_TTL = 604800  # 7 days


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
