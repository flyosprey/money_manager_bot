# from telebot.types import Message
#
# from tbot.dispatcher.base import (
#     handle_start,
#     handle_help,
# )
# from tbot.enums.users import UserStates
# from tbot.user_states import get_user_state
# from tbot_base.bot import tbot as bot
#
#
# @bot.message_handler(
#     func=lambda message: get_user_state(message.chat.id)
#     == UserStates.WRITE_TRANSACTION
# )
# def write_transaction(message: Message):
#     handle_walletapp_password(message=message)
