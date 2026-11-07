from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage
from config.leitor import parametros


class LoginPage(BasePage):
    URL = parametros.texto("url_login")

    USERNAME_INPUT = (By.NAME, "username")
    PASSWORD_INPUT = (By.NAME, "password")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "input[value='Log In']")
    ERROR_MESSAGE = (By.CSS_SELECTOR, ".error")
    # Seletores flexíveis para detetar a sessão iniciada
    LOGOUT_LINK = (By.LINK_TEXT, "Log Out")
    ACCOUNT_OVERVIEW = (By.CSS_SELECTOR, "a[href*='overview.htm']")

    def open(self):
        """Acede à página inicial de login."""
        self.driver.get(self.URL)

    def login(self, username, password):
        """Preenche o utilizador e senha e clica em Log In."""
        self.find_element(self.USERNAME_INPUT).clear()
        self.type_text(self.USERNAME_INPUT, username)
        self.find_element(self.PASSWORD_INPUT).clear()
        self.type_text(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)

    def get_error_message(self):
        """Retorna o texto da mensagem de erro de login."""
        return self.get_element_text(self.ERROR_MESSAGE)

    def is_logged_in(self):
        """Verifica se o login foi bem-sucedido procurando elementos exclusivos do painel logado."""
        try:
            # Aguarda até 5 segundos para detetar o link de Log Out ou a visão geral de contas
            WebDriverWait(self.driver, parametros.decimal("tempo_espera_login")).until(
                lambda driver: len(driver.find_elements(*self.LOGOUT_LINK)) > 0 or 
                               len(driver.find_elements(*self.ACCOUNT_OVERVIEW)) > 0
            )
            return True
        except:
            return False

    def logout(self):
        """Termina a sessão atual se estiver logado."""
        try:
            if self.is_logged_in():
                self.click(self.LOGOUT_LINK)
        except:
            pass