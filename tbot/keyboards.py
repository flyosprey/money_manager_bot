from telebot import types

from tbot.dto.transactions.type import TransactionStatus
from tbot.dto.walletapp_api.mcc_codes import MCCTransactionCategoryPagination
from tbot.dto.walletapp_api.type import SettingsStates

COlUMN_OF_CATEGORY_BUTTONS = 2
COlUMN_OF_LABEL_BUTTONS = 2

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
        types.KeyboardButton("Налаштування гаманця обліку"),
        types.KeyboardButton("Порада радника"),
        types.KeyboardButton("Налаштувати категорії"),
    )

    markup.add(
        types.KeyboardButton(
            "Оновити звʼязок з Monobank (якщо не приходять транзакції)"
        )
    )

    bot.set_my_commands(
        [
            types.BotCommand("/integrate", "Розпочати"),
            types.BotCommand("/about", "Для чого цей бот?"),
            types.BotCommand("/donate", "Підтримати донатом"),
            types.BotCommand("/setup_categories", "Налаштувати категорії"),
            types.BotCommand("/ai_advice", "Порада радника"),
            types.BotCommand("/reset_token", "Замінити токен Monobank"),
            types.BotCommand("/reset_pass", "Замінити пароль WalletApp"),
            types.BotCommand(
                "/refresh_monobank",
                "Оновити звʼязок з Monobank (якщо не приходять транзакції)",
            ),
            types.BotCommand(
                "/change_walletapp_account",
                "Змінити аккаунт WalletApp",
            ),
        ]
    )

    return markup


def transaction_menu(editable_menu: bool = True) -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup()
    set_default_transaction_keyboard(keyboard=keyboard)
    if editable_menu:
        set_editable_menu(keyboard=keyboard)

    select_category = types.InlineKeyboardButton(
        "Вибрати категорію📌", callback_data="category_page_1"
    )
    select_label = types.InlineKeyboardButton(
        "Вибрати мітку🏷", callback_data="label_page_1"
    )

    keyboard.add(select_label)
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
    separate_transaction = types.InlineKeyboardButton(
        "Розділити транзакції🖇",
        callback_data=TransactionStatus.AWAITING_SEPARATE_TRANSACTIONS,
    )
    add_comment = types.InlineKeyboardButton(
        "Додати коментар💬", callback_data=TransactionStatus.AWAITING_ADD_COMMENT
    )
    update_price = types.InlineKeyboardButton(
        "Змінити ціну🫰", callback_data=TransactionStatus.AWAITING_UPDATE_PRICE
    )
    keyboard.add(separate_transaction)
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


def transaction_labels_menu(
    labels: list[str], page: int = 1
) -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup()
    set_default_transaction_keyboard(keyboard=keyboard)
    generate_labels_keyboard(
        paginated_labels=paginate_labels(labels=labels, codes_per_page=5),
        page=page,
        keyboard=keyboard,
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
            keyboard.add(*buttons)
            buttons = []

    buttons = []
    if page > 1:
        buttons.append(
            types.InlineKeyboardButton(
                "Попередня⬅️", callback_data=f"category_page_{page-1}"
            )
        )
    if page < len(MCCTransactionCategoryPagination[transaction_type]):
        buttons.append(
            types.InlineKeyboardButton(
                "Наступна➡️", callback_data=f"category_page_{page+1}"
            )
        )

    keyboard.add(*buttons)

    return keyboard


def generate_labels_keyboard(
    paginated_labels: dict[int, list[str]],
    page: int,
    keyboard: types.InlineKeyboardMarkup,
) -> types.InlineKeyboardMarkup:
    labels = paginated_labels[page]
    buttons = []
    for idx, label in enumerate(labels):
        buttons.append(
            types.InlineKeyboardButton(label, callback_data=f"label_{label}")
        )
        if len(buttons) % COlUMN_OF_LABEL_BUTTONS == 0 or len(labels) == idx + 1:
            keyboard.add(*buttons)
            buttons = []

    buttons = []
    if page > 1:
        buttons.append(
            types.InlineKeyboardButton(
                "Попередня⬅️", callback_data=f"label_page_{page-1}"
            )
        )
    if page < len(paginated_labels):
        buttons.append(
            types.InlineKeyboardButton(
                "Наступна➡️", callback_data=f"label_page_{page+1}"
            )
        )

    keyboard.add(*buttons)

    return keyboard


def paginate_labels(labels: list[str], codes_per_page: int) -> dict[int, list[str]]:
    paginated_labels = []
    for label in labels:
        if label not in paginated_labels:
            paginated_labels.append(label)

    total_pages = (len(paginated_labels) + codes_per_page - 1) // codes_per_page
    return {
        page: paginated_labels[(page - 1) * codes_per_page : page * codes_per_page]
        for page in range(1, total_pages + 1)
    }


def wallet_settings_menu():
    keyboard = types.InlineKeyboardMarkup()
    add_label = types.InlineKeyboardButton(
        "Додати мітку📌", callback_data=SettingsStates.AWAITING_LABEL.value
    )

    keyboard.add(add_label)

    return keyboard
