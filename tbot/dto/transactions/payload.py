from pydantic import BaseModel


class SimpleTransaction(BaseModel):
    amount: int
    mcc: int
    note: str | None = None
    time: int
    contractor: str
    type: str
