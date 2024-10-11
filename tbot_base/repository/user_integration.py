from django.db import IntegrityError

from tbot_base.models import UserIntegrations
from tbot_base.repository.base import Repository


class UserIntegrationRepository(Repository):
    @classmethod
    def select(cls, first: bool, **kwargs) -> [UserIntegrations]:
        if first:
            result = UserIntegrations.objects.filter(**kwargs).first()
            return [result] if result else []

        return UserIntegrations.objects.filter(**kwargs).all()

    @classmethod
    def upsert(cls, **kwargs) -> UserIntegrations:
        try:
            return UserIntegrations.objects.create(**kwargs)
        except IntegrityError:
            return UserIntegrations.objects.update(**kwargs)

    @classmethod
    def update(cls, where: dict, update: dict) -> UserIntegrations:
        return UserIntegrations.objects.filter(**where).update(**update)

    @classmethod
    def delete(cls, **kwargs) -> tuple[bool, int] | None:
        return UserIntegrations.objects.filter(**kwargs).delete()
