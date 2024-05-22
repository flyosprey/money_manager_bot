from tbot_base.repository.bot_user import BotUserRepository


def register_user(message):
    if BotUserRepository.select(user_id=message.from_user.id, first=True):
        return

    user_id, user_name, first_name = (
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
    )
    chat_id = message.chat.id
    last_name, is_bot = message.from_user.last_name, message.from_user.is_bot
    first_name = "" if first_name is None else first_name
    last_name = "" if last_name is None else last_name
    user_name = "" if user_name is None else user_name

    BotUserRepository.upsert(
        user_id=user_id,
        chat_id=chat_id,
        user_name=user_name,
        first_name=first_name,
        last_name=last_name,
        is_bot=is_bot,
    ).save()
