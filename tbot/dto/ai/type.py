import enum


class AdviceType(str, enum.Enum):
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"


ADVICE_ARGS_BY_TYPE = {
    AdviceType.WEEKLY.value: {
        "prompt": "Give me advice for my financial based on previous week transactions",
        "title": "Порада тижня",
    },
    AdviceType.MONTHLY.value: {
        "prompt": "Give me advice for my financial based on previous week transactions",
        "title": "Порада місяця",
    },
}
