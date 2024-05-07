from requests import RequestException
from telebot.types import Message

from money_manager.config import config
from tbot.clients.walletapp.manager.manager import InvalidCredentialsError
from tbot.controllers.integrity import (
    check_mono_token,
    check_walletapp_credentials,
    is_integration_exist,
    save_all_credentials,
)
from tbot.dto.users.type import UserStates
from tbot.utils import CREDENTIALS, set_user_state
from tbot_base.bot import tbot as bot

IOS_WALLETAPP_URL = (
    "https://apps.apple.com/us/app/wallet-daily-budget-profit/id1032467659"
)
ANDROID_WALLETAPP_URL = "https://play.google.com/store/apps/details?id=com.droid4you.application.wallet&referrer=utm_source%3Dhome_page"
WEB_WALLETAPP_URL = "https://budgetbakers.com/"
MONOBANK_URL = "https://api.monobank.ua/index.html"


def delete_credential_message(message: Message):
    bot.delete_message(
        chat_id=message.chat.id,
        message_id=message.message_id,
    )


def normalize_credential(credential: str):
    return credential.strip()


def handle_integration(message: Message):
    if is_integration_exist(user_id=message.from_user.id):
        bot.send_message(chat_id=message.chat.id, text="Integration is already exist.")
        return

    bot.send_message(
        chat_id=message.chat.id,
        text="Введіть ваш токен Monobank.\n"
        f"Його можна знайти за посиланням відсканувавши QR {MONOBANK_URL}",
    )
    set_user_state(message.from_user.id, state=UserStates.AWAITING_MONOTOKEN)


def handle_mono_token(message: Message):
    mono_token = normalize_credential(credential=message.text)
    delete_credential_message(message)
    try:
        check_mono_token(
            mono_token=mono_token,
            base_url=config.monobank.base_url,
        )
    except RequestException:
        bot.send_message(chat_id=message.chat.id, text="Невірний токен Monobank!")
        set_user_state(user_id=message.from_user.id, state=UserStates.IDLE)
        return

    CREDENTIALS[message.from_user.id]["mono_token"] = mono_token

    bot.send_message(
        chat_id=message.chat.id,
        text="Введіть ваш юзернейм для WalletApp:\n"
        "Створити аккаунт можна за посиланнями:\n"
        f"- iOS -> {IOS_WALLETAPP_URL}\n"
        f"- Android -> {ANDROID_WALLETAPP_URL}\n"
        f"- Веб-сайт -> {WEB_WALLETAPP_URL}",
    )
    set_user_state(
        user_id=message.from_user.id, state=UserStates.AWAITING_WALLETAPP_USERNAME
    )


def handle_walletapp_username(message: Message):
    CREDENTIALS[message.from_user.id]["walletapp_username"] = normalize_credential(
        credential=message.text
    )
    delete_credential_message(message)
    bot.send_message(
        chat_id=message.chat.id,
        text="Введіть ваш пароль для WalletApp.\n"
    )
    set_user_state(
        user_id=message.from_user.id, state=UserStates.AWAITING_WALLETAPP_PASSWORD
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
            base_url=config.walletapp.base_url,
            user_id=message.from_user.id,
        )
    except InvalidCredentialsError:
        bot.send_message(
            chat_id=message.chat.id, text="Невірні облікові дані для WalletApp!"
        )
        return

    save_all_credentials(
        user_id=message.from_user.id,
        mono_token=CREDENTIALS[message.from_user.id]["mono_token"],
        walletapp_password=CREDENTIALS[message.from_user.id]["walletapp_password"],
        walletapp_username=CREDENTIALS[message.from_user.id]["walletapp_username"],
        secret_key=config.secret_key,
    )
    del CREDENTIALS[message.from_user.id]
    bot.send_message(chat_id=message.chat.id, text="Успішно інтегровано!")
