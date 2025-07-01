import functools
from types import FunctionType

from tbot.utils import admin_bot_notification


def suppress_token_errors(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if "incorrect api key provided" in str(e).lower():
                admin_bot_notification(message=str(e))
                return None
            raise

    return wrapper


class SuppressTokenErrorsMixin:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        for attr_name in dir(cls):
            if attr_name.startswith("__") and attr_name.endswith("__"):
                continue

            attr = getattr(cls, attr_name, None)

            if not isinstance(attr, FunctionType):
                continue

            setattr(cls, attr_name, suppress_token_errors(attr))

        if isinstance(cls.__init__, FunctionType):
            cls.__init__ = suppress_token_errors(cls.__init__)
