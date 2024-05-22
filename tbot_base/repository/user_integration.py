from django.db import IntegrityError

from tbot_base.models import UserIntegrations
from tbot_base.repository.base import Repository


class UserIntegrationRepository(Repository):
    @classmethod
    def select(cls, **kwargs) -> UserIntegrations | None:
        return UserIntegrations.objects.filter(**kwargs).first()

    @classmethod
    def upsert(cls, **kwargs) -> UserIntegrations:
        try:
            return UserIntegrations.objects.create(**kwargs)
        except IntegrityError:
            return UserIntegrations.objects.update(**kwargs)

    @classmethod
    def delete(cls, **kwargs) -> tuple[bool, int] | None:
        return UserIntegrations.objects.filter(**kwargs).delete()
