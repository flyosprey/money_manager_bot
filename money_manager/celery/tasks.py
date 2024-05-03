from celery import shared_task

from money_manager.config import config
from tbot.clients.monobank.mono_client import MonobankClient
from tbot.dto.monobank.payload import Transaction
from tbot.keyboards import transaction_menu
from tbot.utils import (
    convert_currency_number_to_symbol,
    convert_money,
    convert_timestamp_to_datetime,
    get_unix_time,
)
from tbot_base.bot import tbot as bot
from tbot_base.models import BotUsers
from tbot_base.security.encrypting import EncryptManager


@shared_task
def check_monobank_users_transactions():
    for user in BotUsers.objects.select_related("integration").all():
        check_monobank_user_transactions.delay(
            user.integration.monobank_token, user.chat_id
        )


@shared_task
def check_monobank_user_transactions(monobank_token: str, chat_id: str):
    encryptor = EncryptManager(secret_key=config.secret_key)
    client = MonobankClient(
        base_url=config.monobank.base_url,
    )
    transactions: list[Transaction] = client.get_all_accounts_transactions(
        token=encryptor.decrypt_key(data=monobank_token),
        period=config.monobank.transaction_period,
    )
    if transactions:
        from_date = convert_timestamp_to_datetime(
            timestamp=get_unix_time(seconds=config.monobank.transaction_period)
        )
        to_date = convert_timestamp_to_datetime(timestamp=get_unix_time())
        bot.send_message(
            chat_id=chat_id, text=f"Транзакції за період {from_date} - {to_date}"
        )
        for transaction in transactions:
            bot.send_message(
                chat_id=chat_id,
                text=f"Опис - {transaction.description}\n"
                f"Сума - {convert_currency_number_to_symbol(transaction.currency_code)}"
                f"{convert_money(transaction.amount)}\n"
                f"Комісія - {convert_money(transaction.commission_rate) or 'відсутня'}\n"
                f"Кешбек - {transaction.cashback_amount or 'відсутній'}\n"
                f"Коментар - {transaction.comment or 'відсутній'}\b"
                f"Дата - {convert_timestamp_to_datetime(timestamp=transaction.time)}",
                reply_markup=transaction_menu(),
            )


# if __name__ == "__main__":
# from django_celery_beat.models import PeriodicTask, IntervalSchedule
# import json
#
#
# def create_periodic_task():
#     schedule, _ = IntervalSchedule.objects.get_or_create(
#         every=3600,
#         period=IntervalSchedule.SECONDS,
#     )
#
#     PeriodicTask.objects.create(
#         interval=schedule,
#         name='Send Request to Google Every Hour',
#         task='money_manager.tasks.check_monobank_users_transactions',
#         args=json.dumps([]),
#         kwargs=json.dumps({}),
#         enabled=True,
#     )
#
# create_periodic_task()
