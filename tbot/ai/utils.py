import functools

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
            attr = getattr(cls, attr_name)
            if callable(attr):
                wrapped = suppress_token_errors(attr)
                setattr(cls, attr_name, wrapped)
