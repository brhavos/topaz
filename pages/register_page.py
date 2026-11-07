import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from pages.base_page import BasePage

class RegisterPage(BasePage):
    URL = "https://parabank.parasoft.com/parabank/register.htm"

    FIRST_NAME_INPUT = (By.ID, "customer.firstName")
    LAST_NAME_INPUT = (By.ID, "customer.lastName")
    ADDRESS_INPUT = (By.ID, "customer.address.street")
    CITY_INPUT = (By.ID, "customer.address.city")
    STATE_INPUT = (By.ID, "customer.address.state")
    ZIP_INPUT = (By.ID, "customer.address.zipCode")
    PHONE_INPUT = (By.ID, "customer.phoneNumber")
    SSN_INPUT = (By.ID, "customer.ssn")
    USERNAME_INPUT = (By.ID, "customer.username")
    PASSWORD_INPUT = (By.ID, "customer.password")
    CONFIRM_INPUT = (By.ID, "repeatedPassword")
    REGISTER_BUTTON = (By.CSS_SELECTOR, "input[value='Register']")
    SUCCESS_MESSAGE = (By.CSS_SELECTOR, "#rightPanel h1")
    FORM_ERRORS = (By.CSS_SELECTOR, "span.error")

    def open(self):
        self.driver.get(self.URL)

    def _human_type(self, locator, text):
        """Simula a digitação humanizada caractere por caractere."""
        element = self.find_element(locator)
        element.clear()
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.12))

    def fill_register_form(self, first, last, address, city, state, zip_code, phone, ssn, username, password):
        self._human_type(self.FIRST_NAME_INPUT, first)
        self._human_type(self.LAST_NAME_INPUT, last)
        self._human_type(self.ADDRESS_INPUT, address)
        self._human_type(self.CITY_INPUT, city)
        self._human_type(self.STATE_INPUT, state)
        self._human_type(self.ZIP_INPUT, zip_code)
        self._human_type(self.PHONE_INPUT, phone)
        self._human_type(self.SSN_INPUT, ssn)
        self._human_type(self.USERNAME_INPUT, username)
        self._human_type(self.PASSWORD_INPUT, password)
        self._human_type(self.CONFIRM_INPUT, password)

    def submit_register(self):
        time.sleep(0.5)
        self.click(self.REGISTER_BUTTON)

    def get_form_errors(self):
        """Retorna as mensagens de erro de validação exibidas no formulário."""
        errors = []
        for element in self.driver.find_elements(*self.FORM_ERRORS):
            try:
                if element.text.strip():
                    errors.append(element.text.strip())
            except StaleElementReferenceException:
                continue
        return errors

    def get_success_message(self):
        """Aguarda o título de boas-vindas da página pós-registo."""
        try:
            WebDriverWait(self.driver, self.timeout).until(
                lambda _driver: "welcome" in self.safe_text(self.SUCCESS_MESSAGE).lower()
            )
        except TimeoutException:
            errors = self.get_form_errors()
            detalhe = "; ".join(errors) if errors else "nenhum erro de validação exibido"
            raise AssertionError(f"O registo não foi concluído ({detalhe}).")
        return self.get_element_text(self.SUCCESS_MESSAGE)