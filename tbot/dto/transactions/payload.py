from pydantic import BaseModel

from tbot.constants import TransactionTypes


class SimpleTransaction(BaseModel):
    amount: int
    mcc: int
    note: str | None = None
    time: int
    contractor: str
    type: TransactionTypes
    label_name: str
    label_id: str | None = None
    category_id: str | None = None
