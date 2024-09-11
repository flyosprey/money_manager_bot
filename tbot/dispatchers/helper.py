from telebot.types import Message

from money_manager.config import config
from tbot.controllers.integration import check_monobank
from tbot_base.bot import tbot as bot
from tbot_base.repository.user_integration import UserIntegrationRepository
from tbot_base.security.encrypting import EncryptManager


def handle_refresh_monobank(message: Message, dsn: str):
    encrypt_manager = EncryptManager(secret_key=config.secret_key)
    for integration in UserIntegrationRepository.select(
        user_id=message.from_user.id, first=False
    ):
        if not check_monobank(
            dsn=dsn,
            mono_token=encrypt_manager.decrypt_key(integration.monobank_token),
            encrypted_user_id=encrypt_manager.encrypt_key(str(message.from_user.id)),
        ):
            bot.send_message(
                chat_id=message.chat.id, text="Не вдалося оновити звʼязок з Monobank!"
            )
            return

    bot.send_message(
        chat_id=message.chat.id, text="Звʼязок з Monobank успішно оновлено!"
    )
