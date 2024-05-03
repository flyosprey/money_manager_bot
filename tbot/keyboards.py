from telebot import types

from tbot.dto.transactions.type import TransactionStatus

########################################### KEYBOARDS ##################################################################

# ASK_LINK = "🔗 Cut Link Now 🔗"


def menu(bot):
    keyboard = types.ReplyKeyboardMarkup(
        row_width=1, resize_keyboard=True, one_time_keyboard=False
    )
    bot.set_my_commands(
        [
            types.BotCommand("/start", "start"),
            types.BotCommand("/help", "help"),
        ]
    )
    return keyboard


def transaction_menu(
    accepted_data: TransactionStatus = TransactionStatus.ACCEPTED,
    rejected_data: TransactionStatus = TransactionStatus.REJECTED,
):
    add_transaction = types.InlineKeyboardButton(
        "Записати", callback_data=accepted_data
    )
    reject_transaction = types.InlineKeyboardButton(
        "Відхилити", callback_data=rejected_data
    )

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(add_transaction)
    keyboard.add(reject_transaction)

    return keyboard
