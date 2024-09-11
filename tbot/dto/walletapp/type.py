import enum


class Category(str, enum.Enum):
    LIFE_AND_ENTERTAINMENT = "Life & Entertainment"
    FOOD = "Food & Beverages"
    OTHERS = "Others"
    VEHICLE = "Vehicle"
    COMMUNICATION_PC = "Communication, PC"
    FINANCIAL_EXPENSES = "Financial expenses"
    TRANSPORTATION = "Transportation"
    INCOME = "Income"


class SubCategoryIncome(str, enum.Enum):
    INCOME = "Income"


class SubCategoryTransportation(str, enum.Enum):
    TRANSPORTATION = "Transportation"
    BUSINESS_TRIP = "Business trips"
    LONG_DISTANCE = "Long distance"
    PUBLIC_TRANSPORT = "Public transport"
    TAXI = "Taxi"


class SubCategoryFinancialExpenses(str, enum.Enum):
    FINANCIAL_EXPENSES = "Financial expenses"
    ADVISORY = "Advisory"
    CHARGES_FEES = "Charges, Fees"
    CHILD_SUPPORT = "Child Support"
    FINES = "Fines"
    INSURANCES = "Insurances"
    LOANS_INTERESTS = "Loans, interests"
    TAXES = "Taxes"


class SubCategoryCommunicationPC(str, enum.Enum):
    COMMUNICATION_PC = "Communication, PC"
    INTERNET = "INTERNET"
    POSTAL_SERVICES = "Postal services"
    SOFTWARE_APPS_GAMES = "Software, apps, games"
    TELEPHONY_MOBILE_PHONE = "Telephony, mobile phone"


class SubCategoryLifeAndEntertainment(str, enum.Enum):
    ALCOHOL_AND_TOBACCO = "Alcohol, tobacco"


class SubCategoryVehicle(str, enum.Enum):
    VEHICLE = "Vehicle"
    FUEL = "Fuel"
    LEASING = "Leasing"
    PARKING = "Parking"
    RENTALS = "Rentals"
    VEHICLE_INSURANCE = "Vehicle insurance"
    VEHICLE_MAINTENANCE = "Vehicle maintenance"


class SubCategoryOthers(str, enum.Enum):
    OTHERS = "Others"
    MISSING = "Missing"


class SubCategoryFood(str, enum.Enum):
    FOOD = "Food & Beverages"
    BAR_CAFE = "Bar, cafe"
    GROCERIES = "Groceries"
    RESTAURANT_FAST_FOOD = "Restaurant, fast-food"


class RecordType(str, enum.Enum):
    EXPENSE = "Expense"
    INCOME = "Income"
    TRANSFER = "Transfer"
