from telebot import types

from tbot.dto.transactions.type import TransactionStatus
from tbot.dto.walletapp.mcc_codes import MCCTransactionCategoryPagination

COlUMN_OF_CATEGORY_BUTTONS = 2

########################################### KEYBOARDS ##################################################################


def menu(bot):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=False)

    markup.add(types.KeyboardButton("Розпочати"))

    markup.add(
        types.KeyboardButton("Замінити токен Monobank"),
        types.KeyboardButton("Замінити пароль WalletApp"),
        types.KeyboardButton("Змінити аккаунт WalletApp"),
    )

    markup.add(
        types.KeyboardButton(
            "Оновити звʼязок з Monobank (якщо не приходять транзакції)"
        )
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


def transaction_menu() -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup()
    set_default_transaction_keyboard(keyboard=keyboard)
    set_editable_menu(keyboard=keyboard)

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


def set_editable_menu(
    keyboard: types.InlineKeyboardMarkup,
) -> types.InlineKeyboardMarkup:
    add_comment = types.InlineKeyboardButton(
        "Додати коментар💬", callback_data=TransactionStatus.AWAITING_ADD_COMMENT
    )
    update_price = types.InlineKeyboardButton(
        "Змінити ціну🫰", callback_data=TransactionStatus.AWAITING_UPDATE_PRICE
    )
    keyboard.add(add_comment)
    keyboard.add(update_price)

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
    categories = MCCTransactionCategoryPagination[transaction_type][page]
    buttons = []
    for idx, category in enumerate(categories):
        buttons.append(
            types.InlineKeyboardButton(
                category["name"], callback_data=f"category_{category['code']}"
            )
        )
        if len(buttons) % COlUMN_OF_CATEGORY_BUTTONS == 0 or len(categories) == idx + 1:
            keyboard.add(*[button for button in buttons])
            buttons = []

    buttons = []
    if page > 1:
        buttons.append(
            types.InlineKeyboardButton("Попередня⬅️", callback_data=f"page_{page-1}")
        )
    if page < len(MCCTransactionCategoryPagination[transaction_type]):
        buttons.append(
            types.InlineKeyboardButton("Наступна➡️", callback_data=f"page_{page+1}")
        )

    keyboard.add(*buttons)

    return keyboard
