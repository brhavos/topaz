from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from pages.base_page import BasePage

class TransferPage(BasePage):
    URL = "https://parabank.parasoft.com/parabank/transfer.htm"
    OPEN_ACCOUNT_URL = "https://parabank.parasoft.com/parabank/openaccount.htm"

    AMOUNT_INPUT = (By.ID, "amount")
    FROM_ACCOUNT_SELECT = (By.ID, "fromAccountId")
    TO_ACCOUNT_SELECT = (By.ID, "toAccountId")
    TRANSFER_BUTTON = (By.CSS_SELECTOR, "input[value='Transfer']")
    # Seletor genérico para o painel de sucesso após transferência
    SUCCESS_MESSAGE = (By.CSS_SELECTOR, "#rightPanel")

    ACCOUNT_TYPE_SELECT = (By.ID, "type")
    OPEN_ACCOUNT_BUTTON = (By.CSS_SELECTOR, "input[value='Open New Account']")
    NEW_ACCOUNT_ID = (By.ID, "newAccountId")
    FROM_ACCOUNT_OPTIONS = (By.CSS_SELECTOR, "#fromAccountId option")
    TO_ACCOUNT_OPTIONS = (By.CSS_SELECTOR, "#toAccountId option")

    def open(self):
        self.driver.get(self.URL)

    def _new_account_number(self):
        """Número da conta recém-criada, ou None enquanto ainda não estiver disponível."""
        for element in self.driver.find_elements(*self.NEW_ACCOUNT_ID):
            try:
                if element.is_displayed() and element.text.strip():
                    return element.text.strip()
            except StaleElementReferenceException:
                return None
        return None

    def _wait_for_accounts(self):
        """As contas são carregadas via AJAX; aguarda até os selects estarem preenchidos."""
        WebDriverWait(self.driver, self.timeout).until(
            lambda driver: len(driver.find_elements(*self.FROM_ACCOUNT_OPTIONS)) > 0
            and len(driver.find_elements(*self.TO_ACCOUNT_OPTIONS)) > 0
        )

    def open_new_account(self, account_type="SAVINGS"):
        """Abre uma conta adicional para o cliente logado (necessária para transferir entre contas)."""
        self.driver.get(self.OPEN_ACCOUNT_URL)
        # O botão só submete depois de o AJAX preencher o select de contas de origem
        WebDriverWait(self.driver, self.timeout).until(
            lambda driver: len(driver.find_elements(*self.FROM_ACCOUNT_OPTIONS)) > 0
        )
        Select(self.find_element(self.ACCOUNT_TYPE_SELECT)).select_by_visible_text(account_type)
        self.click(self.OPEN_ACCOUNT_BUTTON)
        # #newAccountId já existe (vazio e oculto) no formulário, por isso esperamos pelo número preenchido
        try:
            WebDriverWait(self.driver, self.timeout).until(
                lambda _driver: self._new_account_number() is not None
            )
        except TimeoutException:
            raise AssertionError(
                f"Falha ao abrir a conta {account_type}. Conteúdo do painel: {self.safe_text(self.SUCCESS_MESSAGE).strip()!r}"
            )
        return self._new_account_number()

    def perform_transfer(self, amount):
        self._wait_for_accounts()
        self.type_text(self.AMOUNT_INPUT, amount)

        from_dropdown = Select(self.find_element(self.FROM_ACCOUNT_SELECT))
        to_dropdown = Select(self.find_element(self.TO_ACCOUNT_SELECT))
        if len(from_dropdown.options) < 2:
            raise AssertionError("São necessárias pelo menos duas contas para transferir entre contas distintas.")

        from_dropdown.select_by_index(0)
        to_dropdown.select_by_index(1)

        self.click(self.TRANSFER_BUTTON)

    def get_success_message(self):
        """Aguarda e retorna o texto do painel direito após a transferência."""
        try:
            WebDriverWait(self.driver, self.timeout).until(
                lambda _driver: "transfer complete" in self.safe_text(self.SUCCESS_MESSAGE).lower()
            )
        except TimeoutException:
            pass
        return self.get_element_text(self.SUCCESS_MESSAGE)