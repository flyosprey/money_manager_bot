from requests import RequestException
from telebot.types import Message

from money_manager.config import settings
from tbot.clients.walletapp.manager.manager import InvalidCredentialsError
from tbot.controller.integrity import (
    check_mono_token,
    check_walletapp_credentials,
    save_all_credentials,
)
from tbot.enums.users import UserStates
from tbot.user_states import set_user_state, CREDENTIALS

from tbot_base.bot import tbot as bot


def delete_credential_message(message: Message):
    bot.delete_message(
        chat_id=message.chat.id,
        message_id=message.message_id,
    )


def normalize_credential(credential: str):
    return credential.strip()


def handle_integration(message: Message):
    # if is_integration_exist(user_id=message.from_user.id):
    #     bot.send_message(chat_id=message.chat.id, text="Integration is already exist.")
    #     return # TODO uncomment

    bot.send_message(chat_id=message.chat.id, text="Введіть ваш токен Monobank:")
    set_user_state(message.from_user.id, state=UserStates.AWAITING_MONOTOKEN)


def handle_mono_token(message: Message):
    mono_token = normalize_credential(credential=message.text)
    delete_credential_message(message)
    try:
        check_mono_token(
            mono_token=mono_token,
            base_url=settings.monobank.base_url,
        )
    except RequestException:
        bot.send_message(chat_id=message.chat.id, text="Невірний токен Monobank!")
        set_user_state(user_id=message.chat.id, state=UserStates.IDLE)
        return

    CREDENTIALS[message.from_user.id]["mono_token"] = mono_token

    bot.send_message(
        chat_id=message.chat.id, text="Введіть ваш юзернейм для WalletApp:"
    )
    set_user_state(
        user_id=message.chat.id, state=UserStates.AWAITING_WALLETAPP_USERNAME
    )


def handle_walletapp_username(message: Message):
    CREDENTIALS[message.from_user.id]["walletapp_username"] = normalize_credential(
        credential=message.text
    )
    delete_credential_message(message)
    bot.send_message(
        chat_id=message.chat.id, text="Введіть ваш пароль для WalletApp:"
    )
    set_user_state(
        user_id=message.chat.id, state=UserStates.AWAITING_WALLETAPP_PASSWORD
    )


def handle_walletapp_password(message: Message):
    CREDENTIALS[message.from_user.id]["walletapp_password"] = normalize_credential(
        credential=message.text
    )
    delete_credential_message(message)
    try:
        check_walletapp_credentials(
            username=CREDENTIALS[message.from_user.id]["walletapp_username"],
            password=CREDENTIALS[message.from_user.id]["walletapp_password"],
            base_url=settings.walletapp.base_url,
            user_id=message.from_user.id,
        )
    except InvalidCredentialsError:
        bot.send_message(chat_id=message.chat.id, text="Невірні облікові дані для WalletApp!")
        return

    save_all_credentials(
        user_id=message.from_user.id,
        mono_token=CREDENTIALS[message.from_user.id]["mono_token"],
        walletapp_password=CREDENTIALS[message.from_user.id]["walletapp_password"],
        walletapp_username=CREDENTIALS[message.from_user.id]["walletapp_username"],
    )
    del CREDENTIALS[message.from_user.id]
    bot.send_message(chat_id=message.chat.id, text="Успішно інтегровано!")
