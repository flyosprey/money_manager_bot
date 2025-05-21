from money_manager.config import TIMEZONE_KYIV
from tbot.ai.memory import UserMemoryRAG
from tbot.dto.transactions.payload import SimpleTransaction
from tbot.dto.walletapp_api.mcc_codes import MCCTransactionCategoryName
from tbot.utils import convert_money, convert_timestamp_to_datetime


def save_to_ai_memory(user_id: int, transaction: SimpleTransaction):
    memory_storage = UserMemoryRAG(user_id=user_id)
    text = construct_message_for_rag_storage(transaction=transaction)
    metadata = construct_metadata_for_rag_storage(transaction=transaction)
    memory_storage.add(texts=[text], metadatas=[metadata], ids=[str(transaction.time)])


def delete_from_ai_memory(user_id: int, doc_id: int):
    memory_storage = UserMemoryRAG(user_id=user_id)
    memory_storage.delete(doc_id=str(doc_id))


def construct_metadata_for_rag_storage(transaction: SimpleTransaction) -> dict:
    return transaction.model_dump(exclude={"label_id", "category_id"})


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
