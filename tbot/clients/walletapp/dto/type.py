import enum


class Category(str, enum.Enum):
    FOOD = "Food & Beverages"
    OTHERS = "Others"


class SubCategoryOthers(str, enum.Enum):
    OTHERS = "Others"
    MISSING = "Missing"


class SubCategoryFood(str, enum.Enum):
    FOOD = "Food & Beverages"
    CAFE = "Bar, cafe"
    GROCERIES = "Groceries"
    RESTAURANT = "Restaurant, fast-food"


class RecordType(str, enum.Enum):
    EXPENSE = "Expense"
    INCOME = "Income"
    TRANSFER = "Transfer"
