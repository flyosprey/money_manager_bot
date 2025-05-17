from pydantic import BaseModel


class SimpleTransaction(BaseModel):
    amount: int
    mcc: int
    note: str | None = None
    time: int
    contractor: str
    type: str
    label_name: str
    label_id: str | None = None
    category_id: str | None = None
