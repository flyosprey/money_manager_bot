import hashlib
import hmac
import json
import re
import subprocess

from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from money_manager.config import TIMEZONE_KYIV, config
from tbot.dto.monobank.payload import Transaction
from tbot.keyboards import transaction_menu
from tbot.utils import (
    admin_bot_notification,
    convert_currency_number_to_code,
    convert_money,
    convert_timestamp_to_datetime,
    logger,
    create_transaction_text,
)
from tbot_base.dto.github.payload import (
    PullRequestWebhook,
    PushWebhook,
)

from .bot import tbot
from .repository.bot_user import BotUserRepository
from .security.encrypting import EncryptManager

for module in settings.BOT_HANDLERS:
    __import__(module)


def check_content_type(content_type: str) -> None:
    if content_type not in {"application/json"}:
        raise PermissionDenied("Wrong content type!")


@method_decorator(csrf_exempt, name="dispatch")
class TelegramWebhookView(View):
    def post(self, request, *args, **kwargs):
        try:
            check_content_type(content_type=request.META["CONTENT_TYPE"])
        except PermissionDenied as e:
            logger.error(e)
            return JsonResponse({"error": "Permission denied"}, status=403)

        json_data = request.body.decode("utf-8")
        update = tbot.update(json_data)
        tbot.process_new_updates([update])

        return HttpResponse(status=200)


@method_decorator(csrf_exempt, name="dispatch")
class MonobankWebhookView(View):
    def get(self, request, encrypted_user_id: str, *args, **kwargs):
        try:
            self.verify_signature(encrypted_user_id=encrypted_user_id)
        except PermissionDenied as e:
            logger.error(e)
            return JsonResponse({"error": "Permission denied"}, status=403)
        return HttpResponse(status=200)

    def post(self, request, encrypted_user_id: str, *args, **kwargs):
        try:
            check_content_type(content_type=request.META["CONTENT_TYPE"])
            user_id = self.verify_signature(encrypted_user_id=encrypted_user_id)

            raw_body = json.loads(request.body)
            transaction = Transaction(
                **raw_body.get("data", {}).get("statementItem", {})
            )
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except PermissionDenied as e:
            logger.error(e)
            return JsonResponse({"error": "Permission denied"}, status=403)
        except ValidationError as e:
            return JsonResponse({"error": e.error_dict}, status=422)

        logger.info("Received body from monobank %s", raw_body)
        if not self.skip_transaction(transaction=transaction):
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
            date_ = convert_timestamp_to_datetime(
                timestamp=transaction.time, timezone=TIMEZONE_KYIV
            ).replace(tzinfo=None)
            transaction_type = "+" if transaction.amount > 0 else "-"
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
                    amount=convert_money(transaction.amount),
                    separator="",
                ),
                reply_markup=transaction_menu(),
            )

        return HttpResponse(status=200)

    @staticmethod
    def verify_signature(encrypted_user_id: str) -> int:
        try:
            encrypt_manager = EncryptManager(secret_key=config.secret_key)
            user_id = int(encrypt_manager.decrypt_key(encrypted_user_id))
        except Exception:
            raise PermissionDenied from None

        if not BotUserRepository.select(user_id=user_id, first=True):
            raise PermissionDenied

        return user_id

    @staticmethod
    def skip_transaction(transaction: Transaction) -> bool:
        return bool(re.search(r"з \w+ картки", transaction.description.lower()))


@method_decorator(csrf_exempt, name="dispatch")
class GithubWebhookView(View):
    def post(self, request, *args, **kwargs):
        try:
            check_content_type(content_type=request.META["CONTENT_TYPE"])
            self.verify_signature(
                payload_body=request.body,
                signature_header=request.headers.get("X-Hub-Signature-256"),
                secret_token=config.deployment.github_secret_key.get_secret_value(),
            )

            event_type = request.headers.get("X-Github-Event")
            if event_type not in {"push", "pull_request"}:
                raise PermissionDenied("Event type not permitted")

            branch = self.get_branch_from_event(
                event_type=event_type, raw_body=request.body
            )
            if not self.is_prod_branch(branch=branch):
                raise PermissionDenied("Branch not permitted")

            output = self.execute_git_pull(
                branch=branch, project_path=config.deployment.project_path
            )
            admin_bot_notification(message="New version deployed successfully!✅")

            return JsonResponse({"status": "success", "output": output}, status=200)

        except (json.JSONDecodeError, ValidationError) as e:
            return JsonResponse({"error": str(e)}, status=400)
        except PermissionDenied as e:
            logger.error(e)
            return JsonResponse({"error": "Permission denied"}, status=403)
        except DeployError as e:
            admin_bot_notification(message=f"Failed to deploy new version!🔴\n{e}")
            return JsonResponse({"status": "failure", "error": str(e)}, status=500)
        except Exception as e:
            logger.exception(e)
            return JsonResponse({"status": "failure", "error": str(e)}, status=500)

    @staticmethod
    def verify_signature(
        payload_body: bytes, secret_token: str, signature_header: str
    ) -> None:
        if not signature_header:
            raise PermissionDenied("Missing signature header")

        hash_object = hmac.new(
            secret_token.encode("utf-8"), msg=payload_body, digestmod=hashlib.sha256
        )
        if not hmac.compare_digest(
            "sha256=" + hash_object.hexdigest(), signature_header
        ):
            raise PermissionDenied("Signature verification failed")

    def get_branch_from_event(self, event_type: str, raw_body: bytes) -> str | None:
        payload = json.loads(raw_body)
        if event_type == "push":
            webhook = PushWebhook(**payload)
            return self.get_branch(webhook=webhook)

        if event_type == "pull_request":
            webhook = PullRequestWebhook(**payload)
            if webhook.action not in {"closed"}:
                raise PermissionDenied("Action not permitted")
            return webhook.pull_request.base.ref

        return

    @staticmethod
    def get_branch(webhook) -> str | None:
        return webhook.ref.split("/")[-1] if webhook.ref else None

    @staticmethod
    def is_prod_branch(branch: str) -> bool:
        return branch in {"main", "beta"}

    @staticmethod
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


class DeployError(Exception):
    pass
