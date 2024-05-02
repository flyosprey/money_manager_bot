from tbot_base.models import BotUsers


def register_user(message):
    if BotUsers.objects.filter(user_id=message.from_user.id).exists():
        return
    user_id, user_name, first_name = (
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
    )
    last_name, is_bot = message.from_user.last_name, message.from_user.is_bot
    first_name = "" if first_name is None else first_name
    last_name = "" if last_name is None else last_name
    user_name = "" if user_name is None else user_name
    BotUsers(user_id, user_name, first_name, last_name, is_bot).save()
