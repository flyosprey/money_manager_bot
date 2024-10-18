from telebot import types

from tbot.dto.transactions.type import TransactionStatus
from tbot.dto.walletapp.mcc_codes import MCCTransactionCategoryPagination


########################################### KEYBOARDS ##################################################################


def menu(bot):
    keyboard = types.ReplyKeyboardMarkup(
        row_width=1, resize_keyboard=True, one_time_keyboard=False
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
        ]
    )
    return keyboard


def transaction_menu() -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup()
    set_default_transaction_keyboard(keyboard=keyboard)

    select_category = types.InlineKeyboardButton(
        "📌Вибрати категорію", callback_data=TransactionStatus.SELECT_CATEGORY
    )

    keyboard.add(select_category)

    return keyboard


def set_default_transaction_keyboard(keyboard: types.InlineKeyboardMarkup) -> types.InlineKeyboardMarkup:
    add_transaction = types.InlineKeyboardButton(
        "✍️Записати", callback_data=TransactionStatus.ACCEPTED
    )
    reject_transaction = types.InlineKeyboardButton(
        "🚫Відхилити", callback_data=TransactionStatus.REJECTED
    )
    keyboard.add(add_transaction)
    keyboard.add(reject_transaction)

    return keyboard


def transaction_categories_menu(page: int = 1) -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup()
    set_default_transaction_keyboard(keyboard=keyboard)
    generate_categories_keyboard(page=page, keyboard=keyboard)

    return keyboard


def generate_categories_keyboard(page: int, keyboard: types.InlineKeyboardMarkup) -> types.InlineKeyboardMarkup:
    for category in MCCTransactionCategoryPagination[page]:
        keyboard.add(types.InlineKeyboardButton(
            category["name"], callback_data=f"{category['name']}_{category['code']}"
        ))

    if page > 1:
        keyboard.add(types.InlineKeyboardButton("Previous", callback_data=f"page_{page-1}"))
    if page < len(MCCTransactionCategoryPagination):
        keyboard.add(types.InlineKeyboardButton("Next", callback_data=f"page_{page+1}"))

    return keyboard
