import json
import re
import subprocess
import sys

from django.core.exceptions import PermissionDenied

from money_manager.config import TIMEZONE_KYIV
from tbot.clients.monobank.client import MonobankClient
from tbot.constants import TransactionTypes
from tbot.dto.monobank.payload import Transaction
from tbot.keyboards import transaction_menu
from tbot.utils import (
    convert_currency_number_to_code,
    convert_money,
    convert_timestamp_to_datetime,
    create_transaction_text,
    logger,
    process_amount,
)

from .bot import tbot
from .dto.github.payload import PullRequestWebhook, PushWebhook
from .exceptions import DeployError, DjangoMigrationError


def notify_user_about_transaction(user_id: str, transaction: Transaction):
    currency = convert_currency_number_to_code(transaction.currency_code)
    cashback = (
        f"{convert_money(transaction.cashback_amount):.2f}₴"
        if transaction.cashback_amount
        else "відсутній"
    )
    commission = (
        f"{convert_money(transaction.commission_rate):.2f}₴"
        if transaction.commission_rate
        else "відсутня"
    )
    date_ = convert_timestamp_to_datetime(transaction.time, TIMEZONE_KYIV).replace(
        tzinfo=None
    )
    transaction_type = TransactionTypes.from_amount(transaction.amount)
    amount = process_amount(
        amount=transaction.amount,
        currency_code=transaction.currency_code,
        transaction_type=transaction_type,
        monobank_client=MonobankClient(),
    )

    tbot.send_message(
        chat_id=user_id,
        text=create_transaction_text(
            currency=currency,
            transaction_type=transaction_type,
            date_=date_,
            commission=commission,
            cashback=cashback,
            comment=transaction.comment,
            description=transaction.description,
            mcc_code=transaction.mcc,
            amount=amount,
        ),
        reply_markup=transaction_menu(),
    )


def skip_transaction(transaction: Transaction) -> bool:
    return bool(re.search(r"Mocking", transaction.description.lower()))


def check_content_type(content_type: str) -> None:
    if content_type not in {"application/json"}:
        raise PermissionDenied("Wrong content type!")


def get_branch_from_event(event_type: str, raw_body: bytes) -> str | None:
    payload = json.loads(raw_body)
    if event_type == "push":
        webhook = PushWebhook(**payload)
        return get_branch(webhook=webhook)

    if event_type == "pull_request":
        webhook = PullRequestWebhook(**payload)
        if webhook.action not in {"closed"}:
            raise PermissionDenied("Action not permitted")
        return webhook.pull_request.base.ref

    return None


def get_branch(webhook) -> str | None:
    return webhook.ref.split("/")[-1] if webhook.ref else None


def is_prod_branch(branch: str) -> bool:
    return branch in {"main", "beta"}


def execute_django_migration(project_path: str) -> dict[str, str]:
    try:
        make_migrations = subprocess.run(
            [sys.executable, "manage.py", "makemigrations"],
            capture_output=True,
            text=True,
            cwd=project_path,
        )

        if make_migrations.returncode != 0:
            error_message = f"{make_migrations.stderr} {make_migrations.stdout}".strip()
            raise DjangoMigrationError(error_message)

        migrate = subprocess.run(
            [sys.executable, "manage.py", "migrate"],
            capture_output=True,
            text=True,
            cwd=project_path,
        )

        if migrate.returncode != 0:
            error_message = f"{migrate.stderr} {migrate.stdout}".strip()
            raise DjangoMigrationError(error_message)

        logger.info("Migrated successfully")
        return {
            "make_migrations": make_migrations.stdout,
            "migrate": migrate.stdout,
        }
    except subprocess.SubprocessError as e:
        logger.exception("Migration failed")
        raise DjangoMigrationError("Migration failed") from e


def execute_git_pull(branch: str, project_path: str) -> str:
    try:
        git_pull = subprocess.run(
            ["/usr/bin/git", "pull", "origin", branch],
            capture_output=True,
            text=True,
            cwd=project_path,
        )

        if git_pull.returncode == 0:
            logger.info("Deployed successfully")
            return git_pull.stdout

        error_message = f"{git_pull.stderr} {git_pull.stdout}".strip()
        raise DeployError(error_message)

    except subprocess.SubprocessError as e:
        logger.exception("Failed to pull the latest code")
        raise DeployError("Git pull command failed") from e
