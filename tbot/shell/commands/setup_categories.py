import os

import click
import django

from money_manager.celery.tasks import setup_categories

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "money_manager.settings")
django.setup()

import structlog  # noqa

from money_manager.config import config  # noqa
from tbot.controllers.integration import check_monobank  # noqa
from tbot_base.repository.bot_user import BotUserRepository  # noqa
from tbot_base.security.encrypting import EncryptManager  # noqa

logger = structlog.get_logger(__name__)


@click.group("categories")
def run_setting_up_categories():
    pass


@run_setting_up_categories.command("setup")
@click.option("-u", "--user-id", type=click.INT, default=None, help="User ID.")
def run(user_id: int):
    logger.info("Start setting up categories")
    setting_up_categories(user_id=user_id)
    logger.info("Finished setting up categories")


def setting_up_categories(user_id: int) -> None:
    setup_categories(user_id=user_id)
