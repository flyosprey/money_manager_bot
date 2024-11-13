from telebot import types

from tbot.dto.transactions.type import TransactionStatus
from tbot.dto.walletapp.mcc_codes import MCCTransactionCategoryPagination

########################################### KEYBOARDS ##################################################################


def menu(bot):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=False)

    markup.row(types.KeyboardButton("Розпочати!!"))

    markup.row(
        types.KeyboardButton("Замінити токен Monobank"),
        types.KeyboardButton("Замінити пароль WalletApp"),
        types.KeyboardButton("Змінити аккаунт WalletApp")
    )

    markup.row(types.KeyboardButton("Оновити звʼязок з Monobank (якщо не приходять транзакції)"))

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


def transaction_menu() -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup()
    set_default_transaction_keyboard(keyboard=keyboard)

    select_category = types.InlineKeyboardButton(
        "Вибрати категорію📌", callback_data="page_1"
    )

    keyboard.add(select_category)

    return keyboard


def set_default_transaction_keyboard(
    keyboard: types.InlineKeyboardMarkup,
) -> types.InlineKeyboardMarkup:
    add_transaction = types.InlineKeyboardButton(
        "️Записати✍", callback_data=TransactionStatus.ACCEPTED
    )
    reject_transaction = types.InlineKeyboardButton(
        "Відхилити🚫", callback_data=TransactionStatus.REJECTED
    )
    keyboard.add(add_transaction)
    keyboard.add(reject_transaction)

    return keyboard


def transaction_categories_menu(
    transaction_type: str, page: int = 1
) -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup()
    set_default_transaction_keyboard(keyboard=keyboard)
    generate_categories_keyboard(
        transaction_type=transaction_type, page=page, keyboard=keyboard
    )

    return keyboard


def generate_categories_keyboard(
    transaction_type: str, page: int, keyboard: types.InlineKeyboardMarkup
) -> types.InlineKeyboardMarkup:
    for category in MCCTransactionCategoryPagination[transaction_type][page]:
        keyboard.add(
            types.InlineKeyboardButton(
                category["name"], callback_data=f"category_{category['code']}"
            )
        )

    if page > 1:
        keyboard.add(
            types.InlineKeyboardButton("Попередня⬅️", callback_data=f"page_{page-1}")
        )
    if page < len(MCCTransactionCategoryPagination[transaction_type]):
        keyboard.add(
            types.InlineKeyboardButton("Наступна➡️", callback_data=f"page_{page+1}")
        )

    return keyboard
