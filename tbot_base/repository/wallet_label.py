from django.db import IntegrityError

from tbot_base.models import UserWalletLabel
from tbot_base.repository.base import Repository


class UserWalletLabelRepository(Repository):
    @classmethod
    def select(cls, first: bool, **kwargs) -> [UserWalletLabel]:
        if first:
            result = UserWalletLabel.objects.filter(**kwargs).first()
            return [result] if result else []

        return UserWalletLabel.objects.filter(**kwargs).all()

    @classmethod
    def upsert(cls, **kwargs) -> UserWalletLabel:
        try:
            return UserWalletLabel.objects.create(**kwargs)
        except IntegrityError:
            return UserWalletLabel.objects.update(**kwargs)

    @classmethod
    def update(cls, where: dict, update: dict) -> UserWalletLabel:
        return UserWalletLabel.objects.filter(**where).update(**update)

    @classmethod
    def delete(cls, **kwargs) -> tuple[bool, int] | None:
        return UserWalletLabel.objects.filter(**kwargs).delete()
