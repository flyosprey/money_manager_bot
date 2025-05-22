from telebot.types import CallbackQuery, Message

from money_manager.config import config
from tbot.controllers.integration import check_monobank
from tbot.keyboards import transaction_menu
from tbot.utils import edit_message
from tbot_base.bot import tbot as bot
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
