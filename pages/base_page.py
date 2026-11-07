from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.timeout = 10

    def safe_text(self, locator):
        """Texto do elemento, tolerante a elementos obsoletos durante navegações/AJAX."""
        try:
            return self.driver.find_element(*locator).text
        except (NoSuchElementException, StaleElementReferenceException):
            return ""

    def find_element(self, locator):
        """Aguarda e retorna um elemento visível."""
        return WebDriverWait(self.driver, self.timeout).until(
            EC.visibility_of_element_located(locator)
        )

    def click(self, locator):
        """Clica em um elemento após garantir que é clicável."""
        element = WebDriverWait(self.driver, self.timeout).until(
            EC.element_to_be_clickable(locator)
        )
        element.click()

    def type_text(self, locator, text):
        """Preenche um campo de texto de forma segura."""
        element = self.find_element(locator)
        element.clear()
        element.send_keys(text)

    def get_element_text(self, locator):
        """Retorna o texto de um elemento."""
        return self.find_element(locator).text