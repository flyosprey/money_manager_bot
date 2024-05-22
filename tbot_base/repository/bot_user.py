from django.db import IntegrityError

from tbot_base.models import BotUsers
from tbot_base.repository.base import Repository


class BotUserRepository(Repository):
    @classmethod
    def select(cls, first: bool, **kwargs) -> list[BotUsers] | None:
        if first:
            return [BotUsers.objects.filter(**kwargs).first()]

        return BotUsers.objects.filter(**kwargs).all()

    @classmethod
    def upsert(cls, commit: bool = False, **kwargs) -> BotUsers:
        try:
            return BotUsers.objects.create(**kwargs)
        except IntegrityError:
            return BotUsers.objects.update(**kwargs)

    @classmethod
    def delete(cls, **kwargs) -> tuple[bool, int] | None:
        return BotUsers.objects.filter(**kwargs).delete()
