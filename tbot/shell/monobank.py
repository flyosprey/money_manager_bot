import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "money_manager.settings")
django.setup()

import structlog  # noqa

from money_manager.config import config  # noqa
from tbot.controllers.integration import check_monobank  # noqa
from tbot_base.repository.bot_user import BotUserRepository  # noqa
from tbot_base.security.encrypting import EncryptManager  # noqa

logger = structlog.get_logger(__name__)


def refresh_monobank_webhooks(dsn: str) -> None:
    encrypt_manager = EncryptManager(secret_key=config.secret_key)
    for user in BotUserRepository.select(first=False):
        for integration in user.integrations.all():
            if not check_monobank(
                dsn=dsn,
                mono_token=encrypt_manager.decrypt_key(integration.monobank_token),
                chat_id=int(user.user_id),
                encrypted_user_id=encrypt_manager.encrypt_key(str(user.user_id)),
                base_url=config.monobank.base_url,
            ):
                logger.warning(
                    "Failed to refresh monobank webhooks", user_id=user.user_id
                )


def run():
    logger.info("Start refresh_monobank_webhooks")
    refresh_monobank_webhooks(dsn=config.dsn)
    logger.info("Finished refresh_monobank_webhooks")


if __name__ == "__main__":
    run()
