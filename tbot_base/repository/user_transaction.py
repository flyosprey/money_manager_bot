from django.db import IntegrityError

from tbot_base.models import UserTransactions
from tbot_base.repository.base import Repository


class UserTransactionsRepository(Repository):
    @classmethod
    def select(cls, first: bool, **kwargs) -> [UserTransactions]:
        if first:
            result = UserTransactions.objects.filter(**kwargs).first()
            return [result] if result else []

        return UserTransactions.objects.filter(**kwargs).all()

    @classmethod
    def insert(cls, **kwargs) -> UserTransactions:
        return UserTransactions.objects.create(**kwargs)

    @classmethod
    def upsert(cls, **kwargs) -> UserTransactions:
        try:
            return UserTransactions.objects.create(**kwargs)
        except IntegrityError:
            filter_kwargs = {
                "user_id": kwargs["user_id"],
                "transaction_id": kwargs["category_id"],
            }

            UserTransactions.objects.filter(**filter_kwargs).update(**kwargs)

    @classmethod
    def update(cls, where: dict, update: dict) -> UserTransactions:
        return UserTransactions.objects.filter(**where).update(**update)

    @classmethod
    def delete(cls, **kwargs) -> tuple[bool, int] | None:
        return UserTransactions.objects.filter(**kwargs).delete()
