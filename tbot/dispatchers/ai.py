from telebot.types import Message

from money_manager.config import TIMEZONE_KYIV
from tbot.ai.gpt import LLMAssistant
from tbot.ai.memory import UserMemoryRAG
from tbot.dto.transactions.payload import SimpleTransaction
from tbot.dto.walletapp_api.mcc_codes import MCCTransactionCategoryName
from tbot.utils import convert_money, convert_timestamp_to_datetime
from tbot_base.bot import tbot as bot


def handle_ai_advice(message: Message):
    llm = LLMAssistant(user_id=message.from_user.id)
    response = llm.ask(query="Give me an advice based on my transactions")
    bot.send_message(chat_id=message.chat.id, text=response.content)


def save_to_ai_memory(user_id: int, transaction: SimpleTransaction):
    memory_storage = UserMemoryRAG(user_id=user_id)
    text = construct_message_for_rag_storage(transaction=transaction)
    metadata = construct_metadata_for_rag_storage(transaction=transaction)
    memory_storage.add(texts=[text], metadatas=[metadata])


def delete_from_ai_memory(user_id: int, doc_id: int):
    memory_storage = UserMemoryRAG(user_id=user_id)
    memory_storage.delete(doc_id=str(doc_id))


def construct_metadata_for_rag_storage(transaction: SimpleTransaction) -> dict:
    return {
        **transaction.model_dump(exclude={"label_id", "category_id"}),
        "doc_id": str(transaction.time),
    }


def construct_message_for_rag_storage(transaction: SimpleTransaction) -> str:
    label = f"- {transaction.label_name}" if transaction.label_name else ""
    date_ = convert_timestamp_to_datetime(
        timestamp=transaction.time, timezone=TIMEZONE_KYIV
    ).replace(tzinfo=None)
    amount = convert_money(transaction.amount)
    return (
        f"[{date_}] {transaction.type}{amount}₴ for "
        f"{MCCTransactionCategoryName[transaction.type][transaction.mcc]} {label}."
        f"Additional_info: {transaction.note}."
    )
