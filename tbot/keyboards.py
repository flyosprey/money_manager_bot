from telebot import types

from tbot.dto.transactions.type import TransactionStatus

########################################### KEYBOARDS ##################################################################


def menu(bot):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        types.KeyboardButton("Розпочати"),
        types.KeyboardButton("Замінити токен Monobank"),
        types.KeyboardButton("Замінити пароль WalletApp"),
        types.KeyboardButton("Оновити звʼязок з Monobank (якщо не приходять транзакції)"),
        types.KeyboardButton("Змінити аккаунт WalletApp"),
    )

    bot.set_my_commands(
        [
            types.BotCommand("/start", "Розпочати бота"),
            types.BotCommand("/integrate", "Розпочати інтеграцію"),
            types.BotCommand(
                "/add_token",
                "Додати трекінг додаткового аккаунту Monobank",
            ),
            types.BotCommand("/reset_token", "Замінити токен Monobank"),
            types.BotCommand("/reset_pass", "Замінити пароль WalletApp"),
            types.BotCommand(
                "/refresh_monobank",
                "Оновити звʼязок з Monobank (на випадок, якщо не надходять "
                "повідомлення про оплату)",
            ),
            types.BotCommand(
                "/change_walletapp_account",
                "Змінити аккаунт WalletApp",
            ),
        ]
    )

    return markup


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
