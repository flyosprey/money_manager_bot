import json
import tempfile
import time
from abc import ABC, abstractmethod

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from seleniumwire import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from tbot.dto.walletapp_web.type import Category, RecordType


class MoneyManagerBase(ABC):
    base_url = "https://web.budgetbakers.com/"

    def __init__(self, username: str, password: str):
        self.driver = None
        self.username, self.password = username, password
        self.start_requests_index = 0

    @staticmethod
    def __set_options() -> Options:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")

        temp_profile = tempfile.mkdtemp()
        options.add_argument(f"--user-data-dir={temp_profile}")

        return options

    @staticmethod
    def __set_service() -> Service:
        return Service(executable_path=ChromeDriverManager().install())

    def __enter__(self):
        self.driver = webdriver.Chrome(
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
        category: Category,
        sub_category: Category,
    ):
        self.press_create_record()
        self.fill_transaction(
            amount=amount,
            category=category,
            sub_category=sub_category,
        )
        self.press_add_record()

    def get_transaction_payload(self, timeout: int = 20) -> dict:
        start_time = time.time()
        while time.time() - start_time < timeout:
            for req in self.driver.requests[self.start_requests_index :]:
                if "_bulk_docs" in req.url and req.body:
                    payload = json.loads(req.body)
                    if payload.get("docs", [{}])[0].get("categoryId"):
                        return payload
            time.sleep(0.2)

        raise TimeoutError("Timed out waiting for the latest _bulk_docs request.")

    def fill_transaction(
        self,
        amount: float,
        category: Category,
        sub_category: Category,
    ):
        self.select_record_type(record_type=self.get_record_type(amount=amount))
        self.set_amount(amount=amount)
        self.set_category(category=category, sub_category=sub_category)

    @abstractmethod
    def set_category(self, category: Category, sub_category: Category):
        pass

    @abstractmethod
    def select_record_type(self, record_type: RecordType):
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

    @staticmethod
    def get_record_type(amount: float) -> RecordType:
        if amount > 0:
            return RecordType.INCOME
        return RecordType.EXPENSE

    def scroll_into_view(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
