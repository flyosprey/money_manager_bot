from redis.client import Redis
from tbot.dto.users.type import CredentialType, UserStates

TRANSACTION_TTL = 432000  # 5 days
TRANSACTION_DETAILS_TEMPLATE = "{chat_id}_{message_id}_transaction"
USER_STATE_TEMPLATE = "{user_id}_state"
USER_STATUS_TTL = 432000  # 5 days
MONO_TOKEN_TEMPLATE = "{user_id}_mono_token"  # NOQA
WALLETAPP_USERNAME_TEMPLATE = "{user_id}_walletapp_username"
WALLETAPP_PASSWORD_TEMPLATE = "{user_id}_walletapp_password"  # NOQA
CREDENTIALS_TTL = 60 * 30  # 30 minutes


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
        state = self.redis.get(
            name=USER_STATE_TEMPLATE.format(user_id=user_id)
        ).decode()

        if not state:
            return UserStates.IDLE

        return UserStates(int(state))

    def set_credential(
        self,
        credential_type: CredentialType,
        value: str,
        user_id: int,
        ex: int = CREDENTIALS_TTL,
    ):
        self.redis.set(
            name=self.get_credential_template(credential_type=credential_type).format(
                user_id=user_id
            ),
            value=value,
            ex=ex,
        )

    def get_credential(self, credential_type: CredentialType, user_id: int) -> str:
        return self.redis.get(
            name=self.get_credential_template(credential_type=credential_type).format(
                user_id=user_id
            )
        ).decode()

    def delete_credential(self, credential_type: CredentialType, user_id: int):
        self.redis.delete(
            self.get_credential_template(credential_type=credential_type).format(
                user_id=user_id
            )
        )

    @staticmethod
    def get_credential_template(credential_type: CredentialType) -> str:
        if credential_type == CredentialType.MONO_TOKEN:
            return MONO_TOKEN_TEMPLATE

        if credential_type == CredentialType.WALLETAPP_USERNAME:
            return WALLETAPP_USERNAME_TEMPLATE

        return WALLETAPP_PASSWORD_TEMPLATE
