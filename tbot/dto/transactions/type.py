import enum


class TransactionStatus(str, enum.Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    SELECT_CATEGORY = "SELECT_CATEGORY"
