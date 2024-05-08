import structlog
from requests import RequestException
from selenium.common import WebDriverException
from telebot.apihelper import ApiTelegramException
from telebot.types import Message

from money_manager.config import config
from tbot.clients.walletapp.manager.manager import InvalidCredentialsError
from tbot.controllers.integrity import (
    check_mono_token,
    check_walletapp_credentials,
    is_integration_exist,
    save_all_credentials,
)
from tbot.dependencies.redis import RedisWrapper
from tbot.dto.users.type import CredentialType, UserStates
from tbot_base.bot import tbot as bot
from tbot_base.security.encrypting import EncryptManager

logger = structlog.get_logger()


IOS_WALLETAPP_URL = (
    "https://apps.apple.com/us/app/wallet-daily-budget-profit/id1032467659"
)
ANDROID_WALLETAPP_URL = "https://play.google.com/store/apps/details?id=com.droid4you.application.wallet&referrer=utm_source%3Dhome_page"
WEB_WALLETAPP_URL = "https://budgetbakers.com/"
MONOBANK_URL = "https://api.monobank.ua/index.html"


def delete_message(message: Message):
    try:
        bot.delete_message(
            chat_id=message.chat.id,
            message_id=message.message_id,
        )
    except ApiTelegramException as e:
        if (
            e.result.status_code == 400
            and "message to delete not found" in e.result.text
        ):
            logger.debug("Attempted to delete not founded message.")


def normalize_credential(credential: str):
    return credential.strip()


def handle_integration(message: Message, redis: RedisWrapper):
    if is_integration_exist(user_id=message.from_user.id):
        bot.send_message(chat_id=message.chat.id, text="Integration is already exist.")
        return

    bot.send_message(
        chat_id=message.chat.id,
        text="Введіть ваш токен Monobank.\n"
        f"Його можна знайти за посиланням відсканувавши QR {MONOBANK_URL}",
    )
    redis.set_user_state(message.from_user.id, state=UserStates.AWAITING_MONOTOKEN)


def handle_mono_token(message: Message, redis: RedisWrapper):
    mono_token = normalize_credential(credential=message.text)
    delete_message(message)
    try:
        check_mono_token(
            mono_token=mono_token,
            base_url=config.monobank.base_url,
        )
    except RequestException:
        bot.send_message(chat_id=message.chat.id, text="Невірний токен Monobank!")
        redis.set_user_state(user_id=message.from_user.id, state=UserStates.IDLE)
        return

    redis.set_credential(
        credential_type=CredentialType.MONO_TOKEN,
        value=EncryptManager(secret_key=config.secret_key).encrypt_key(mono_token),
        user_id=message.from_user.id,
    )

    bot.send_message(
        chat_id=message.chat.id,
        text="Введіть ваш юзернейм для WalletApp:\n"
        "Створити аккаунт можна за посиланнями:\n"
        f"- iOS -> {IOS_WALLETAPP_URL}\n"
        f"- Android -> {ANDROID_WALLETAPP_URL}\n"
        f"- Веб-сайт -> {WEB_WALLETAPP_URL}",
    )
    redis.set_user_state(
        user_id=message.from_user.id, state=UserStates.AWAITING_WALLETAPP_USERNAME
    )


def handle_walletapp_username(message: Message, redis: RedisWrapper):
    encryptor = EncryptManager(secret_key=config.secret_key)
    redis.set_credential(
        credential_type=CredentialType.WALLETAPP_USERNAME,
        value=encryptor.encrypt_key(
            normalize_credential(credential=message.text)
        ),
        user_id=message.from_user.id,
    )
    delete_message(message)
    bot.send_message(
        chat_id=message.chat.id, text="Введіть ваш пароль для WalletApp.\n"
    )
    redis.set_user_state(
        user_id=message.from_user.id, state=UserStates.AWAITING_WALLETAPP_PASSWORD
    )


def handle_walletapp_password(message: Message, redis: RedisWrapper):
    walletapp_password = normalize_credential(credential=message.text)
    delete_message(message)
    walletapp_username = redis.get_credential(
        credential_type=CredentialType.WALLETAPP_USERNAME,
        user_id=message.from_user.id,
    )
    encryptor = EncryptManager(secret_key=config.secret_key)
    try:
        check_walletapp_credentials(
            username=encryptor.decrypt_key(walletapp_username),
            password=walletapp_password,
            base_url=config.walletapp.base_url,
            user_id=message.from_user.id,
            redis=redis,
        )
    except InvalidCredentialsError as e:
        logger.error(e)
        bot.send_message(
            chat_id=message.chat.id, text="Невірні облікові дані для WalletApp!🚫"
        )
        return
    except WebDriverException as e:
        logger.error(e.msg)
        bot.send_message(
            chat_id=message.chat.id,
            text="Виникла помилка перевірки облікових даних!🤷‍♂️ Спробуйте знову /integrate.",
        )
        return

    save_all_credentials(
        user_id=message.from_user.id,
        mono_token=redis.get_credential(
            credential_type=CredentialType.MONO_TOKEN, user_id=message.from_user.id
        ),
        walletapp_password=encryptor.encrypt_key(walletapp_password),
        walletapp_username=walletapp_username,
    )
    bot.send_message(chat_id=message.chat.id, text="Успішно інтегровано! 👍")
