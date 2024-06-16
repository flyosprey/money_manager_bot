from telebot.types import Message

from money_manager.config import config
from tbot.controllers.integration import (
    check_monobank,
    check_walletapp_credentials,
)
from tbot.dependencies.redis import RedisWrapper
from tbot.dto.users.type import UserStates
from tbot.utils import delete_message, normalize_credential
from tbot_base.bot import tbot as bot
from tbot_base.repository.user_integration import UserIntegrationRepository
from tbot_base.security.encrypting import EncryptManager

IOS_WALLETAPP_URL = (
    "https://apps.apple.com/us/app/wallet-daily-budget-profit/id1032467659"
)
ANDROID_WALLETAPP_URL = "https://play.google.com/store/apps/details?id=com.droid4you.application.wallet&referrer=utm_source%3Dhome_page"
WEB_WALLETAPP_URL = "https://budgetbakers.com/"
MONOBANK_URL = "https://api.monobank.ua/index.html"


def handle_integration(message: Message, redis: RedisWrapper):
    if (
        UserIntegrationRepository.select(user_id=message.from_user.id, first=True)
        and message.text != "/additional_monobank_token"
    ):
        bot.send_message(
            chat_id=message.chat.id, text="Інтеграцію вже було активовано."
        )
        return

    bot.send_message(
        chat_id=message.chat.id,
        text="Введіть ваш токен Monobank.\n"
        f"Його можна знайти за посиланням відсканувавши QR {MONOBANK_URL}",
    )
    user_state = (
        UserStates.AWAITING_MONOTOKEN
        if message.text != "additional_monobank_token"
        else UserStates.AWAITING_ADDITIONAL_MONOTOKEN
    )
    redis.set_user_state(message.from_user.id, state=user_state)


def handle_mono_token(message: Message, redis: RedisWrapper, dsn: str):
    mono_token = normalize_credential(credential=message.text)
    encrypt_manager = EncryptManager(secret_key=config.secret_key)
    delete_message(message)
    if not check_monobank(
        dsn=dsn,
        mono_token=mono_token,
        encrypted_user_id=encrypt_manager.encrypt_key(str(message.from_user.id)),
        base_url=config.monobank.base_url,
    ):
        bot.send_message(chat_id=message.chat.id, text="Невірний токен Monobank!")
        redis.set_user_state(user_id=message.from_user.id, state=UserStates.IDLE)
        return

    UserIntegrationRepository.upsert(
        user_id=message.from_user.id,
        monobank_token=encrypt_manager.encrypt_key(mono_token),
    )
    if (
        redis.get_user_state(message.from_user.id)
        == UserStates.AWAITING_ADDITIONAL_MONOTOKEN
    ):
        bot.send_message(
            chat_id=message.chat.id,
            text="Додатковий токен монобанку додано!",
        )
        return

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
    UserIntegrationRepository.upsert(
        user_id=message.from_user.id,
        wallet_app_login=EncryptManager(secret_key=config.secret_key).encrypt_key(
            normalize_credential(credential=message.text)
        ),
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
    repository = UserIntegrationRepository()
    delete_message(message)
    integration = repository.select(user_id=message.from_user.id, first=True)[0]
    encrypt_manager = EncryptManager(secret_key=config.secret_key)

    check_walletapp_credentials(
        username=encrypt_manager.decrypt_key(integration.wallet_app_login),
        password=walletapp_password,
        base_url=config.walletapp.base_url,
        user_id=message.from_user.id,
        redis=redis,
    )

    UserIntegrationRepository.upsert(
        user_id=message.from_user.id,
        wallet_app_password=encrypt_manager.encrypt_key(walletapp_password),
    )
    bot.send_message(chat_id=message.chat.id, text="Успішно інтегровано! 👍")


def handle_ask_reset(message: Message, redis: RedisWrapper):
    command = message.text
    credential_type_msg = (
        "токен Монобанку" if "reset_token" in command else "пароль до WalletApp"
    )

    bot.send_message(
        chat_id=message.chat.id, text=f"Введіть новий {credential_type_msg}"
    )
    redis.set_user_state(
        user_id=message.from_user.id,
        state=(
            UserStates.RESET_MONOTOKEN
            if "reset_token" in command
            else UserStates.RESET_WALLETAPP_PASSWORD
        ),
    )


def handle_reset(message: Message, redis: RedisWrapper, dsn: str):
    if not UserIntegrationRepository.select(user_id=message.from_user.id, first=True):
        bot.send_message(
            chat_id=message.chat.id, text="Інтеграцію ще не було активовано."
        )
        return

    mono_token = normalize_credential(credential=message.text)
    delete_message(message)

    user_state = redis.get_user_state(message.from_user.id)
    encrypt_manager = EncryptManager(secret_key=config.secret_key)
    encrypted_credential = encrypt_manager.encrypt_key(mono_token)
    if user_state == UserStates.RESET_WALLETAPP_PASSWORD:
        UserIntegrationRepository.upsert(
            user_id=message.from_user.id,
            walletapp_password=encrypted_credential,
        )
    else:
        if not check_monobank(
            dsn=dsn,
            mono_token=mono_token,
            encrypted_user_id=encrypt_manager.encrypt_key(str(message.from_user.id)),
            base_url=config.monobank.base_url,
        ):
            bot.send_message(chat_id=message.chat.id, text="Невірний токен Monobank!")
            return

        UserIntegrationRepository.upsert(
            user_id=message.from_user.id,
            monobank_token=encrypted_credential,
        )

    bot.send_message(
        chat_id=message.chat.id,
        text=f"{'Токен Монобанку' if user_state == UserStates.RESET_MONOTOKEN else 'Пароль до WalletApp'} оновлено",
    )
    redis.set_user_state(user_id=message.from_user.id, state=UserStates.IDLE)
