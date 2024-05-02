from abc import ABC, abstractmethod

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from tbot.clients.walletapp.enums.mcc_codes import MCCTransactionCategoryT


class MoneyManagerBase(ABC):
    def __init__(self, username: str, password: str, base_url: str):
        self.base_url = base_url
        self.driver = None
        self.options = self.__set_options()
        self.username, self.password = username, password

    @staticmethod
    def __set_options() -> Options:
        options = Options()
        # options.add_argument('--headless')
        return options

    def __enter__(self):
        self.driver = webdriver.Firefox(options=self.options)
        self.login()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.driver is not None:
            self.driver.quit()

    def create_transaction(self, amount: float, category: MCCTransactionCategoryT, note: str):
        self.press_create_record()
        self.fill_transaction(amount=amount, note=note, category=category)
        self.press_add_record()

    def fill_transaction(self, amount: float, category: MCCTransactionCategoryT, note: str):
        self.set_amount(amount=amount)
        self.set_category(category=category)
        self.set_note(note=note)

    @abstractmethod
    def set_category(self, category: MCCTransactionCategoryT):
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
