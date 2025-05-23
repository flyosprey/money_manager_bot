from telebot.types import CallbackQuery, Message

from money_manager.celery.tasks import setup_categories
from money_manager.config import config
from tbot.constants import TOTAL_CATEGORIES_COUNT
from tbot.controllers.integration import check_monobank
from tbot.dependencies.redis import RedisWrapper
from tbot.dto.walletapp_api.type import SetUpCategoriesStates
from tbot.keyboards import transaction_menu
from tbot.utils import edit_message
from tbot_base.bot import tbot as bot
from tbot_base.models import UserCategories
from tbot_base.repository.user_integration import UserIntegrationRepository
from tbot_base.security.encrypting import EncryptManager


def handle_refresh_monobank(message: Message, dsn: str):
    encrypt_manager = EncryptManager(secret_key=config.secret_key)
    for integration in UserIntegrationRepository.select(
        user_id=message.from_user.id, first=False
    ):
        if check_monobank(
            dsn=dsn,
            mono_token=encrypt_manager.decrypt_key(integration.monobank_token),
            encrypted_user_id=encrypt_manager.encrypt_key(str(message.from_user.id)),
        ):
            bot.send_message(
                chat_id=message.chat.id, text="Звʼязок з Monobank успішно оновлено!✅"
            )
            return

    bot.send_message(
        chat_id=message.chat.id, text="Не вдалося оновити звʼязок з Monobank!🔴"
    )


def handle_go_back_menu(call: CallbackQuery):
    text = call.message.text
    is_acceptable = "Записано" not in text
    is_deletable = "Відхилено" not in text

    edit_message(
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        text=call.message.text,
        reply_markup=transaction_menu(
            is_deletable=is_deletable, is_acceptable=is_acceptable
        ),
    )


def handle_setup_categories(message: Message, redis: RedisWrapper):
    if (
        len(
            UserCategories.select(
                user_id=message.from_user.id,
                first=False,
            )
        )
        == TOTAL_CATEGORIES_COUNT
    ):
        bot.send_message(chat_id=message.chat.id, text="Вже всі категорії налаштовано")
        return

    if (
        redis.get_setup_categories_state(user_id=message.from_user.id)
        == SetUpCategoriesStates.SENT_TO_SET_UP
    ):
        bot.send_message(
            chat_id=message.chat.id,
            text="Ви можете спробувати повторно налаштувати категорії, якщо впродовж години вони не були налаштовані.",
        )
        return

    bot.send_message(
        chat_id=message.chat.id, text="Категорії відправлено на налаштування"
    )
    setup_categories.delay(message.from_user.id)
