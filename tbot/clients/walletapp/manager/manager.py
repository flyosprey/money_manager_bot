import time

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tbot.clients.walletapp.enums.categories import Category, SubCategoryFood
from tbot.clients.walletapp.enums.mcc_codes import MCCTransactionCategoryT
from tbot.clients.walletapp.manager.base import MoneyManagerBase


class MoneyManager(MoneyManagerBase):
    def login_request(self):
        self.driver.get(self.base_url + "login")

    def login(self) -> None:
        self.login_request()
        email_element = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.XPATH, ".//input[@name='email']"))
        )
        email_element.send_keys(self.username)

        password_element = self.driver.find_element(
            By.XPATH, ".//input[@name='password']"
        )
        password_element.send_keys(self.password)

        login_button = self.driver.find_element(By.XPATH, ".//button[@type='submit']")
        login_button.click()

        try:
            self.driver.find_element(By.XPATH, ".//div[@class='ui error message error-message']")
        except NoSuchElementException:
            pass
        else:
            raise InvalidCredentialsError("Username or password are invalid")

    def press_create_record(self) -> None:
        record_button = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, ".//button[@class='ui blue mini circular compact button']")
            )
        )
        self.scroll_into_view(record_button)
        record_button.click()

    def set_amount(self, amount: float) -> None:
        amount_input = self.driver.find_element(By.XPATH, ".//input[@name='amount']")
        self.scroll_into_view(amount_input)
        amount_input.send_keys(str(amount))

    def set_category(self, category: MCCTransactionCategoryT) -> None:
        category_input = self.driver.find_element(
            By.XPATH, ".//div[@class='ui fluid selection dropdown']"
        )
        self.scroll_into_view(category_input)
        category_input.click()
        self.select_category(category=category[0])
        self.select_category(category=category[1])

    def set_note(self, note: str) -> None:
        if not note:
            return

        note_input = self.driver.find_element(By.XPATH, ".//textarea[@name='note']")
        self.scroll_into_view(note_input)
        note_input.send_keys("Testing note")

    def press_add_record(self) -> None:
        add_record = self.driver.find_element(
            By.XPATH, ".//button[@class='ui circular fluid primary button']"
        )
        self.scroll_into_view(add_record)
        add_record.click()
        time.sleep(1)

    def select_category(self, category: Category | type[SubCategoryFood] | None) -> None:
        if category is None:
            return

        category_category = self.driver.find_element(
            By.XPATH,
            f".//div[@class='icon-option category-option']//div[contains(text(), '{category.value}')]",
        )
        self.scroll_into_view(category_category)
        category_category.click()


class InvalidCredentialsError(Exception):
    pass

