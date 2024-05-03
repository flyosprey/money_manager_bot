from telebot.types import Message

from tbot.dispatchers.integration import (
    handle_integration,
    handle_mono_token,
    handle_walletapp_password,
    handle_walletapp_username,
)
from tbot.dto.users.type import UserStates
from tbot.utils import get_user_state
from tbot_base.bot import tbot as bot


@bot.message_handler(commands=["integrate"])
def integrate_handler(message: Message):
    handle_integration(message=message)


@bot.message_handler(
    func=lambda message: get_user_state(message.chat.id)
    == UserStates.AWAITING_MONOTOKEN
)
def mono_token_handler(message: Message):
    handle_mono_token(message=message)


@bot.message_handler(
    func=lambda message: get_user_state(message.chat.id)
    == UserStates.AWAITING_WALLETAPP_USERNAME
)
def walletapp_username_handler(message: Message):
    handle_walletapp_username(message=message)


@bot.message_handler(
    func=lambda message: get_user_state(message.chat.id)
    == UserStates.AWAITING_WALLETAPP_PASSWORD
)
def walletapp_password_handler(message: Message):
    handle_walletapp_password(message=message)
