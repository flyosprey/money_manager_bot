import enum
import inspect
import sys


class Category(str, enum.Enum):
    FOOD = "Food & Beverages"
    SHOPPING = "Shopping"
    HOUSING = "Housing"
    TRANSPORTATION = "Transportation"
    VEHICLE = "Vehicle"
    LIFE_AND_ENTERTAINMENT = "Life & Entertainment"
    COMMUNICATION_PC = "Communication, PC"
    FINANCIAL_EXPENSES = "Financial expenses"
    INVESTMENTS = "Investments"
    INCOME = "Income"
    OTHERS = "Others"


class SubCategoryIncome(str, enum.Enum):
    INCOME = "Income"
    CHECKS = "Checks, coupons"
    CHILD_SUPPORT = "Child Support"
    GRANTS = "Dues & grants"
    DIVIDENDS = "Interests, dividends"
    RENTING = "Lending, renting"
    GAMBLING = "Lottery, gambling"
    REFUNDS = "Refunds (tax, purchase)"
    RENTAL_INCOME = "Rental income"
    SALE = "Sale"
    INVOICES = "Wage, invoices"


class SubCategoryInvestments(str, enum.Enum):
    INVESTMENTS = "Investments"
    COLLECTIONS = "Collections"
    FINANCIAL_INVESTMENTS = "Financial investments"
    REALTY = "Realty"
    SAVINGS = "Savings"
    VEHICLES_AND_CHATTELS = "Vehicles, chattels"


class SubCategoryLifeAndEntertainment(str, enum.Enum):
    LIFE_AND_ENTERTAINMENT = "Life & Entertainment"
    SPORT = "Active sport, fitness"
    ALCOHOL_TOBACCO = "Alcohol, tobacco"
    SUBSCRIPTIONS = "Books, audio, subscriptions"
    CHARITY = "Charity, gifts"
    EVENTS = "Culture, sport events"
    EDUCATION = "Education, development"
    HEALTH = "Health care, doctor"
    TRIPS = "Holiday, trips, hotels"
    LIFE_EVENTS = "Life events"
    GAMBLING = "Lottery, gambling"
    STREAMING = "TV, Streaming"
    BEAUTY = "Wellness, beauty"


class SubCategoryTransportation(str, enum.Enum):
    TRANSPORTATION = "Transportation"
    BUSINESS_TRIPS = "Business trips"
    LONG_DISTANCE = "Long distance"
    PUBLIC = "Public transport"
    TAXI = "Taxi"


class SubCategoryHousing(str, enum.Enum):
    HOUSING = "Housing"
    ENERGY_UTILITIES = "Energy, utilities"
    MAINTENANCE = "Maintenance, repairs"
    MORTGAGE = "Mortgage"
    PROPERTY_INSURANCE = "Property insurance"
    RENT = "Rent"
    SERVICES = "Services"


class SubCategoryShopping(str, enum.Enum):
    SHOPPING = "Shopping"
    CLOTHES_AND_FOOTWEAR = "Clothes & Footwear"
    CHEMIST = "Drug-store, chemist"
    ELECTRONICS = "Electronics, accessories"
    GIFTS = "Gifts, joy"
    BEAUTY = "Health and beauty"
    HOME_AND_GARDEN = "Home, garden"
    JEWELS = "Jewels, accessories"
    KIDS = "Kids"
    LEISURE_TIME = "Leisure time"
    PETS = "Pets, animals"
    TOOLS = "Stationery, tools"


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
    INTERNET = "Internet"
    POSTAL_SERVICES = "Postal services"
    SOFTWARE_APPS_GAMES = "Software, apps, games"
    TELEPHONY_MOBILE_PHONE = "Telephony, mobile phone"


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


class SubCategoryFood(str, enum.Enum):
    FOOD = "Food & Beverages"
    BAR_CAFE = "Bar, cafe"
    GROCERIES = "Groceries"
    RESTAURANT_FAST_FOOD = "Restaurant, fast-food"


class RecordType(str, enum.Enum):
    EXPENSE = "Expense"
    INCOME = "Income"
    TRANSFER = "Transfer"


def map_categories_to_subcategories():
    category_map = {}

    current_module = sys.modules[__name__]

    for name, cls in inspect.getmembers(current_module, inspect.isclass):
        if name.startswith("SubCategory") and issubclass(cls, enum.Enum):
            for member in cls:
                for category in Category:
                    if member.value == category.value:
                        category_map[category] = list(cls)
                        break
    return category_map


CATEGORY_SUBCATEGORY_MAP = map_categories_to_subcategories()
