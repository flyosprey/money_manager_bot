from loguru import logger
from telebot import TeleBot, types

from money_manager.config import config


class TBot(TeleBot):
    """ Base Telegram bot config """

    def __init__(self):
        try:
            from .models import BotConfig

            self.config = BotConfig.objects.get(is_active=True)
            self.token = self.config.token

        except Exception as e:
            logger.error(e)

            self.token = config.bot_conf.default_token

        super().__init__(self.token, parse_mode="HTML", threaded=False)

    @staticmethod
    def update(json_data):
        return types.Update.de_json(json_data)


tbot = TBot()
