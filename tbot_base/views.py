import hashlib
import hmac
import json

from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from money_manager.config import config
from tbot.dto.monobank.payload import Transaction
from tbot.utils import (
    admin_bot_notification,
    logger,
)

from .bot import tbot
from .controllers import (
    check_content_type,
    execute_django_migration,
    execute_git_pull,
    get_branch_from_event,
    is_prod_branch,
    notify_user_about_transaction,
)
from .exceptions import DeployError
from .repository.bot_user import BotUserRepository
from .security.encrypting import EncryptManager

for module in settings.BOT_HANDLERS:
    __import__(module)


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
        # if not self.skip_transaction(transaction=transaction):
        notify_user_about_transaction(user_id=user_id, transaction=transaction)

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

            branch = get_branch_from_event(event_type=event_type, raw_body=request.body)
            if not is_prod_branch(branch=branch):
                raise PermissionDenied("Branch not permitted")

            git_output = execute_git_pull(
                branch=branch, project_path=config.deployment.project_path
            )
            migration_output = execute_django_migration(
                project_path=config.deployment.project_path
            )
            admin_bot_notification(message="New version deployed successfully!✅")

            return JsonResponse(
                {"status": "success", "git": git_output, "migration": migration_output},
                status=200,
            )

        except (json.JSONDecodeError, ValidationError) as e:
            return JsonResponse({"error": str(e)}, status=400)
        except PermissionDenied as e:
            logger.error(e)
            return JsonResponse({"error": "Permission denied"}, status=403)
        except DeployError as e:
            logger.exception(e)
            admin_bot_notification(message=f"Failed to deploy new version!🔴\n{e}")
            return JsonResponse(
                {"status": "failure", "error": "Internal error"}, status=500
            )
        except Exception as e:
            logger.exception(e)
            return JsonResponse(
                {"status": "failure", "error": "Internal error"}, status=500
            )

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
