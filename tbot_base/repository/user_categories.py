from django.db import IntegrityError

from tbot_base.models import UserCategories
from tbot_base.repository.base import Repository


class UserCategoriesRepository(Repository):
    @classmethod
    def select(cls, first: bool, **kwargs) -> [UserCategories]:
        if first:
            result = UserCategories.objects.filter(**kwargs).first()
            return [result] if result else []

        return UserCategories.objects.filter(**kwargs).all()

    @classmethod
    def insert(cls, **kwargs) -> UserCategories:
        return UserCategories.objects.create(**kwargs)

    @classmethod
    def upsert(cls, **kwargs) -> UserCategories:
        try:
            return UserCategories.objects.create(**kwargs)
        except IntegrityError:
            filter_kwargs = {
                "user_id": kwargs["user_id"],
                "category_id": kwargs["category_id"],
                "category_type": kwargs.get("category_type", ""),
            }

            UserCategories.objects.filter(**filter_kwargs).update(**kwargs)

    @classmethod
    def update(cls, where: dict, update: dict) -> UserCategories:
        return UserCategories.objects.filter(**where).update(**update)

    @classmethod
    def delete(cls, **kwargs) -> tuple[bool, int] | None:
        return UserCategories.objects.filter(**kwargs).delete()
