from telebot.types import Message

from money_manager.config import config
from tbot.keyboards import menu
from tbot.utils import escape_text_markdown
from tbot_base.bot import tbot as bot


def handle_start(message: Message):
    bot.send_message(
        chat_id=message.chat.id,
        text=escape_text_markdown(
            "Привіт!👋 Я бот OspreyMoney."
            "\nЯ допоможу тобі автоматично фіксувати прибутки та витрати з твоїх кредитних карток. "
            "💳Наразі я працюю з Monobank і записую всі твої транзакції у додаток BudgetBakers. "
            "Зі мною ти завжди будеш контролювати свій бюджет швидко та зручно!"
            "\n🧾Обери опцію нижче, щоб розпочати."
            "\n\nПотрібна допомога чи є запитання? Пишіть мені у особисті: @fly\\_osprey"
            f"\n\n[Банка]({config.donate_url}), якщо бажаєте підтримати бота донатом"
        ),
        parse_mode="MarkdownV2",
        reply_markup=menu(bot),
        disable_web_page_preview=True,
    )


def handle_donate(message: Message):
    bot.send_message(
        chat_id=message.chat.id,
        text=escape_text_markdown(
            f"[Банка]({config.donate_url}), якщо бажаєте підтримати бота донатом"
        ),
        parse_mode="MarkdownV2",
    )
