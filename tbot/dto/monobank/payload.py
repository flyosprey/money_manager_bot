from pydantic import BaseModel, Field


class Account(BaseModel):
    id: str
    send_id: str = Field(..., alias="sendId")
    balance: int
    credit_limit: int = Field(..., alias="creditLimit")
    type: str
    currency_code: int = Field(..., alias="currencyCode")
    cashback_type: str | None = Field(None, alias="cashbackType")
    masked_pan: list[str] = Field(..., alias="maskedPan")
    iban: str


class Jar(BaseModel):
    id: str
    send_id: str = Field(..., alias="sendId")
    title: str
    description: str
    currency_code: int = Field(..., alias="currencyCode")
    balance: int
    goal: int


class ClientInfoPayload(BaseModel):
    client_id: str = Field(..., alias="clientId")
    name: str
    webhook_url: str = Field(..., alias="webHookUrl")
    permissions: str
    accounts: list[Account]
    jars: list[Jar] | None = None


class Transaction(BaseModel):
    id: str
    time: int
    description: str
    mcc: int
    original_mcc: int = Field(..., alias="originalMcc")
    hold: bool
    amount: int
    operation_amount: int = Field(..., alias="operationAmount")
    currency_code: int = Field(..., alias="currencyCode")
    commission_rate: int = Field(..., alias="commissionRate")
    cashback_amount: int = Field(..., alias="cashbackAmount")
    balance: int
    comment: str | None = None
    receipt_id: str | None = Field(None, alias="receiptId")
    invoice_id: str | None = Field(None, alias="invoiceId")
    counter_edrpou: str | None = Field(None, alias="counterEdrpou")
    counter_iban: str | None = Field(None, alias="counterIban")
    counter_name: str | None = Field(None, alias="counterName")
