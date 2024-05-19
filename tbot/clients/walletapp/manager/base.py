from abc import ABC, abstractmethod
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

from tbot.dto.walletapp.mcc_codes import MCCTransactionCategoryT
from tbot.dto.walletapp.type import RecordType


class MoneyManagerBase(ABC):
    def __init__(self, username: str, password: str, base_url: str):
        self.base_url = base_url
        self.driver = None
        self.username, self.password = username, password

    @staticmethod
    def __set_options() -> Options:
        options = Options()
        options.add_argument("--headless")
        return options

    @staticmethod
    def __set_service() -> Service:
        return Service(executable_path=GeckoDriverManager().install())

    def __enter__(self):
        self.driver = webdriver.Firefox(
            options=self.__set_options(), service=self.__set_service()
        )
        self.login()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.driver is not None:
            self.driver.quit()

    def create_transaction(
        self,
        amount: float,
        category: MCCTransactionCategoryT,
        note: str,
        date: datetime,
        contractor: str,
        payment_type: str = "Debit card",
    ):
        self.press_create_record()
        self.fill_transaction(
            amount=amount,
            note=note,
            category=category,
            date=date,
            payment_type=payment_type,
            contractor=contractor,
        )
        self.press_add_record()

    def fill_transaction(
        self,
        amount: float,
        category: MCCTransactionCategoryT,
        note: str,
        date: datetime,
        payment_type: str,
        contractor: str,
    ):
        self.select_record_type(record_type=self.get_record_type(amount=amount))
        self.set_payment(payment_type=payment_type)
        self.set_amount(amount=amount)
        self.set_category(category=category)
        self.set_note(note=note)
        self.set_contractor(contractor=contractor)
        self.set_date(date=date)
        self.set_time(date=date)

    @abstractmethod
    def set_contractor(self, contractor: str):
        pass

    @abstractmethod
    def set_date(self, date: datetime):
        pass

    @abstractmethod
    def set_time(self, date: datetime):
        pass

    @abstractmethod
    def set_category(self, category: MCCTransactionCategoryT):
        pass

    @abstractmethod
    def set_payment(self, payment_type: str):
        pass

    @abstractmethod
    def select_record_type(self, record_type: RecordType):
        pass

    @abstractmethod
    def set_note(self, note: str | None):
        pass

    @abstractmethod
    def set_amount(self, amount: float):
        pass

    @abstractmethod
    def press_add_record(self):
        pass

    @abstractmethod
    def press_create_record(self):
        pass

    @abstractmethod
    def login(self):
        pass

    def scroll_into_view(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)

    @staticmethod
    def get_record_type(amount: float) -> RecordType:
        if amount > 0:
            return RecordType.INCOME
        return RecordType.EXPENSE
