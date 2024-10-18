from requests.exceptions import RequestException
from telebot.types import Message

from money_manager.config import config
from tbot.clients.walletapp.client import WalletAppClient
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
    "https://apps\\.apple\\.com/us/app/wallet\\-daily\\-budget\\-profit/id1032467659"
)
ANDROID_WALLETAPP_URL = (
    "https://play\\.google\\.com/store/apps/details?id\\=com\\.droid4you\\.application\\.wallet"
    "&referrer\\=utm_source\\%\\3\\Dhome_page"
)
WEB_WALLETAPP_URL = "https://budgetbakers\\.com/"
MONOBANK_URL = "https://api\\.monobank\\.ua/index\\.html"


def handle_integration(message: Message, redis: RedisWrapper):
    if (
        UserIntegrationRepository.select(user_id=message.from_user.id, first=True)
        and message.text != "/add_token"
    ):
        bot.send_message(
            chat_id=message.chat.id, text="Інтеграцію вже було активовано.✅"
        )
        return

    bot.send_message(
        chat_id=message.chat.id,
        text="🏦*Введіть ваш токен Monobank:*\n"
        f"||Його можна знайти за посиланням відсканувавши або натиснувши на QR👉 {MONOBANK_URL}||",
        parse_mode="MarkdownV2",
    )
    user_state = (
        UserStates.AWAITING_ADDITIONAL_MONOTOKEN
        if "add_token" in message.text
        else UserStates.AWAITING_MONOTOKEN
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
    ):
        bot.send_message(chat_id=message.chat.id, text="🏦Невірний токен Monobank!🔴")
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
            text="🏦Додатковий токен Monobank додано!✅",
        )
        return

    handle_walletapp_login(message=message, redis=redis)


def handle_walletapp_login(message: Message, redis: RedisWrapper):
    bot.send_message(
        chat_id=message.chat.id,
        text="*Введіть ваш логін WalletApp:*\n"
             "||Створити аккаунт можна за посиланнями:👇👇\n"
             f"\\- iOS \\-\\> {IOS_WALLETAPP_URL}\n"
             f"\\- Android \\-\\> {ANDROID_WALLETAPP_URL}\n"
             f"\\- Веб\\-сайт \\-\\> {WEB_WALLETAPP_URL}||",
        parse_mode="MarkdownV2",
    )
    redis.set_user_state(
        user_id=message.from_user.id, state=UserStates.AWAITING_WALLETAPP_USERNAME
    )


def handle_walletapp_username(message: Message, redis: RedisWrapper):
    UserIntegrationRepository.update(
        where={"user_id": message.from_user.id},
        update={
            "wallet_app_login": EncryptManager(
                secret_key=config.secret_key
            ).encrypt_key(normalize_credential(credential=message.text))
        },
    )
    delete_message(message)
    bot.send_message(
        chat_id=message.chat.id,
        text="*Введіть ваш пароль для WalletApp:*👇",
        parse_mode="MarkdownV2",
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
        user_id=message.from_user.id,
        redis=redis,
    )

    repository.update(
        where={"user_id": message.from_user.id},
        update={"wallet_app_password": encrypt_manager.encrypt_key(walletapp_password)},
    )
    bot.send_message(chat_id=message.chat.id, text="Успішно інтегровано!✅")


def handle_ask_reset(message: Message, redis: RedisWrapper):
    command = message.text
    credential_type_msg = (
        "токен Monobank" if "reset_token" in command else "пароль до WalletApp"
    )

    bot.send_message(
        chat_id=message.chat.id,
        text=f"Введіть новий {credential_type_msg}*👇",
        parse_mode="MarkdownV2",
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
            chat_id=message.chat.id, text="Інтеграцію ще не було активовано🤷‍♂️"
        )
        return

    credential = normalize_credential(credential=message.text)
    delete_message(message)

    encrypt_manager = EncryptManager(secret_key=config.secret_key)

    reset_handler = (
        handle_monobank_handler
        if redis.get_user_state(message.from_user.id) == UserStates.RESET_MONOTOKEN
        else handle_walletapp_reset
    )

    reset_handler(message, credential, encrypt_manager, dsn=dsn)

    redis.set_user_state(user_id=message.from_user.id, state=UserStates.IDLE)


def handle_walletapp_reset(
    message: Message, password: str, encrypt_manager: EncryptManager, **kwargs
):
    integration = UserIntegrationRepository.select(
        user_id=message.from_user.id,
        wallet_app_password__isnull=False,
        wallet_app_login__isnull=False,
        first=True,
    )[0]

    try:
        WalletAppClient().login(
            username=encrypt_manager.decrypt_key(integration.wallet_app_login),
            password=password,
        )
    except RequestException:
        bot.send_message(
            chat_id=message.from_user.id, text="Невірний пароль для WalletApp!🔴"
        )
        return

    UserIntegrationRepository.upsert(
        user_id=message.from_user.id,
        wallet_app_password=encrypt_manager.encrypt_key(password),
    )

    bot.send_message(
        chat_id=message.from_user.id,
        text="Пароль до WalletApp оновлено✅",
    )


def handle_monobank_handler(
    message: Message,
    mono_token: str,
    encrypt_manager: EncryptManager,
    dsn: str,
    **kwargs,
):
    if not check_monobank(
        dsn=dsn,
        mono_token=mono_token,
        encrypted_user_id=encrypt_manager.encrypt_key(str(message.from_user.id)),
    ):
        bot.send_message(chat_id=message.chat.id, text="🏦Невірний токен Monobank!🔴")
        return

    UserIntegrationRepository.upsert(
        user_id=message.from_user.id,
        monobank_token=encrypt_manager.encrypt_key(mono_token),
    )

    bot.send_message(
        chat_id=message.chat.id,
        text="🏦Токен Monobank оновлено✅",
    )
