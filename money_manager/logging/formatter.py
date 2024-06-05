import logging
from datetime import UTC, datetime
from functools import partial

from colorama import Fore, Style, init

init(autoreset=True)

LOG_COLORS = {
    "DEBUG": Fore.GREEN,
    "INFO": Fore.GREEN,
    "WARNING": Fore.YELLOW,
    "ERROR": Fore.RED,
    "CRITICAL": Fore.RED,
}


class BaseFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return self.custom_formatter(
            logger=record.name,
            name=record.name,
            event_dict={
                "timestamp": datetime.now(tz=UTC).isoformat() + "Z",
                "level": record.levelname.lower(),
                "logger": record.name,
                "event": record.getMessage(),
            },
        )

    @staticmethod
    def custom_formatter(
        logger: str | None, name: str, event_dict: dict, is_set_color: bool = True
    ) -> str:
        timestamp = event_dict.pop("timestamp", datetime.now(tz=UTC).isoformat() + "Z")
        level = event_dict.pop("level", "").strip().upper()
        logger_name = event_dict.pop("logger", "")
        event = event_dict.pop("event", "")

        if is_set_color:
            color = LOG_COLORS.get(level, Fore.WHITE)
            return (
                f"{color}{timestamp} [{level}] {event} [{logger_name}]{Style.RESET_ALL}"
            )

        return f"{timestamp} [{logger_name}] [{level}] {event}"


class ConsoleFormatter(BaseFormatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.custom_formatter = partial(self.custom_formatter, is_set_color=True)


class FileFormatter(BaseFormatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.custom_formatter = partial(self.custom_formatter, is_set_color=False)
