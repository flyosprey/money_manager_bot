import enum


class Category(str, enum.Enum):
    FOOD = "Food & Beverages"


class SubCategoryFood(str, enum.Enum):
    FOOD = "Food & Beverages"
    CAFE = "Bar, cafe"
    GROCERIES = "Groceries"
    RESTAURANT = "Restaurant, fast-food"

