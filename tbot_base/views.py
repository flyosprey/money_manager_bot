import json
import re

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
    convert_currency_number_to_code,
    convert_money,
    convert_timestamp_to_datetime,
)

from .bot import tbot
from .repository.bot_user import BotUserRepository
from .security.encrypting import EncryptManager

for module in settings.BOT_HANDLERS:
    __import__(module)


@method_decorator(csrf_exempt, name="dispatch")
class TelegramWebhookView(View):
    def post(self, request, *args, **kwargs):
        if request.META["CONTENT_TYPE"] != "application/json":
            raise PermissionDenied

        json_data = request.body.decode("utf-8")
        update = tbot.update(json_data)
        tbot.process_new_updates([update])

        return HttpResponse(status=200)


@method_decorator(csrf_exempt, name="dispatch")
class MonobankWebhookView(View):
    def get(self, request, encrypted_user_id: str, *args, **kwargs):
        self.check_signature(encrypted_user_id=encrypted_user_id)
        return HttpResponse(status=200)

    def post(self, request, encrypted_user_id: str, *args, **kwargs):
        user_id = self.check_signature(encrypted_user_id=encrypted_user_id)
        if request.META["CONTENT_TYPE"] != "application/json":
            raise PermissionDenied

        try:
            transaction = Transaction(
                **json.loads(request.body).get("data", {}).get("statementItem", {})
            )
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except ValidationError as e:
            return JsonResponse({"error": e.error_dict}, status=422)

        if not self.skip_transaction(transaction=transaction):
            currency = convert_currency_number_to_code(transaction.currency_code)
            cashback = (
                f"{convert_money(transaction.cashback_amount)}₴"
                if transaction.cashback_amount
                else "відсутній"
            )
            commission = (
                f"{convert_money(transaction.commission_rate)}₴"
                if transaction.commission_rate
                else "відсутня"
            )
            amount = f"{convert_money(transaction.amount)}₴"
            date_ = convert_timestamp_to_datetime(
                timestamp=transaction.time, timezone=TIMEZONE_KYIV
            ).replace(tzinfo=None)
            tbot.send_message(
                chat_id=user_id,
                text=f"💰Рахунок: {currency}\n"
                     f"🔖Опис: {transaction.description}\n"
                     f"🫰Сума: {amount}\n"
                     f"{'😔' if re.search(r'[0-1]', commission) else '😁'}Комісія: {commission}\n"
                     f"🤑Кешбек: {cashback}\n"
                     f"💬Коментар: {transaction.comment or 'відсутній'}\n"
                     f"📅Дата: {date_}\n"
                     f"❓MCC: {transaction.mcc}",
                reply_markup=transaction_menu(),
            )

        return HttpResponse(status=200)

    @staticmethod
    def check_signature(encrypted_user_id: str) -> int:
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
        return False
        return bool(re.search(r"з \w+ картки", transaction.description.lower()))
