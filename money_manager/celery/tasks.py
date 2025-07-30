import structlog
from celery import shared_task

from money_manager.config import config
from tbot.ai.gpt import LLMAssistant
from tbot.clients.walletapp_api.client import CloudWalletAppClient, WalletAppClient
from tbot.clients.walletapp_web.client import MoneyManager
from tbot.constants import MINIMUM_ALLOWED_TRANSACTION_AMOUNT
from tbot.dto.walletapp_web.type import CATEGORY_SUBCATEGORY_MAP
from tbot_base.bot import tbot as bot
from tbot_base.repository.bot_user import BotUserRepository
from tbot_base.repository.user_categories import UserCategoriesRepository
from tbot_base.repository.user_integration import UserIntegrationRepository
from tbot_base.security.encrypting import EncryptManager

logger = structlog.get_logger(__name__)


@shared_task
def setup_categories(user_id: int):
    integration = UserIntegrationRepository.select(
        user_id=user_id,
        wallet_app_password__isnull=False,
        wallet_app_login__isnull=False,
        first=True,
    )[0]

    encrypter = EncryptManager(secret_key=config.secret_key)

    category_repository = UserCategoriesRepository()
    owner_id, owner_id_token = WalletAppClient().login(
        username=encrypter.decrypt_key(integration.wallet_app_login),
        password=encrypter.decrypt_key(integration.wallet_app_password),
    )
    cloud_wallet_client = CloudWalletAppClient(
        owner_id=owner_id, owner_id_token=owner_id_token
    )

    with MoneyManager(
        username=encrypter.decrypt_key(integration.wallet_app_login),
        password=encrypter.decrypt_key(integration.wallet_app_password),
    ) as manager:
        for category in CATEGORY_SUBCATEGORY_MAP:
            for sub_category in CATEGORY_SUBCATEGORY_MAP[category]:
                category_name = f"{category.value}_{sub_category.value}"
                manager.create_transaction(
                    amount=MINIMUM_ALLOWED_TRANSACTION_AMOUNT,
                    category=category,
                    sub_category=sub_category,
                )
                logger.info("Transaction for category %s created", category_name)
                payload = manager.get_transaction_payload()

                category_id = (
                    payload["docs"][0].get("categoryId") or payload["docs"][0]["_id"]
                )
                logger.info("Category id: %s created", category_id)

                category_repository.upsert(
                    user_id=user_id,
                    category_id=category_id,
                    name=category_name,
                )
                logger.info("Category saved %s", category_name)
                cloud_wallet_client.delete_transaction(transaction_payload=payload)
                logger.info("Transaction for category %s deleted", category_name)

    bot.send_message(chat_id=user_id, text="Категорії у WalletApp налаштовані. Можна починати роботу.")


@shared_task
def ai_advice_all_users(prompt: str, title: str):
    for user in BotUserRepository.select(first=False):
        ai_advice(user=user, prompt=prompt, title=title)


def ai_advice(user, prompt: str, title: str):
    llm = LLMAssistant(user_id=user.user_id)
    response = llm.ask(query=prompt)

    if response.content and "I don’t know" not in response.content:
        bot.send_message(chat_id=user.chat_id, text=f"{title}:\n{response.content}")
