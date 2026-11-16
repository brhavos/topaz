import time
import random
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, WebDriverException
from pages.base_page import ESPERA_VERIFICACAO_HUMANA, BasePage
from config.leitor import parametros


class RegisterPage(BasePage):
    URL = parametros.texto("url_cadastro")

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
        self.abrir(self.URL)

    def _human_type(self, locator, text):
        """Simula a digitação humanizada caractere por caractere.

        Tolera o recarregamento da página no meio da digitação (ex.: validação do
        Cloudflare), refazendo o campo em vez de derrubar o teste.
        """
        intervalo_min = parametros.decimal("digitacao_intervalo_min")
        intervalo_max = parametros.decimal("digitacao_intervalo_max")
        for tentativa in range(1, 4):
            try:
                element = self.find_element(locator)
                element.clear()
                for char in text:
                    element.send_keys(char)
                    time.sleep(random.uniform(intervalo_min, intervalo_max))
                return
            except (StaleElementReferenceException, WebDriverException):
                if tentativa == 3:
                    raise
                print(
                    "[Cadastro] A página recarregou durante a digitação; "
                    "aguardando e digitando o campo de novo...",
                    flush=True,
                )
                self.aguardar_verificacao_humana()

    def fill_register_form(self, first, last, address, city, state, zip_code, phone, ssn, username, password, confirm=None):
        """Preenche o formulario. confirm permite informar uma confirmacao diferente da senha."""
        if confirm is None:
            confirm = password
        # Guardado para reenviar o cadastro se a pagina voltar em branco.
        self._dados_formulario = {
            "first": first, "last": last, "address": address, "city": city,
            "state": state, "zip_code": zip_code, "phone": phone, "ssn": ssn,
            "username": username, "password": password, "confirm": confirm,
        }
        # Preenche o formulário todo; se a página recarregar no meio (o que apaga os
        # campos), começa de novo em vez de enviar um formulário incompleto.
        for tentativa in range(1, 4):
            self._preencher_campos(first, last, address, city, state, zip_code,
                                   phone, ssn, username, password, confirm)
            if self._formulario_preenchido():
                return
            if tentativa == 3:
                raise AssertionError(
                    "A página de cadastro recarregou repetidamente durante o preenchimento, "
                    "por isso os campos não ficaram preenchidos."
                )
            print(
                "[Cadastro] A página recarregou durante o preenchimento; "
                "preenchendo o formulário de novo...",
                flush=True,
            )
            self.aguardar_verificacao_humana()

    def _preencher_campos(self, first, last, address, city, state, zip_code,
                          phone, ssn, username, password, confirm):
        """Digita todos os campos do formulário de cadastro."""
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
        self._human_type(self.CONFIRM_INPUT, confirm)

    def _formulario_preenchido(self):
        """True quando os campos principais do formulário continuam preenchidos."""
        try:
            with self._sem_espera_implicita():
                valores = [
                    elemento.get_attribute("value") or ""
                    for elemento in (
                        self.driver.find_elements(*self.FIRST_NAME_INPUT)
                        + self.driver.find_elements(*self.USERNAME_INPUT)
                        + self.driver.find_elements(*self.PASSWORD_INPUT)
                    )
                ]
        except WebDriverException:
            return False
        return len(valores) == 3 and all(valores)

    def submit_register(self):
        time.sleep(parametros.decimal("pausa_curta"))
        self.click(self.REGISTER_BUTTON)

    def get_form_errors(self):
        """Retorna as mensagens de erro de validação exibidas no formulário."""
        errors = []
        with self._sem_espera_implicita():
            for element in self.driver.find_elements(*self.FORM_ERRORS):
                try:
                    if element.text.strip():
                        errors.append(element.text.strip())
                except StaleElementReferenceException:
                    continue
        return errors

    def _boas_vindas_exibidas(self):
        """True quando o título de boas-vindas está na tela."""
        return (
            parametros.texto("mensagem_boas_vindas").lower()
            in self.safe_text(self.SUCCESS_MESSAGE).lower()
        )

    def _resultado_chegou(self):
        """True quando o cadastro respondeu: boas-vindas exibidas ou erros de validação."""
        return self._boas_vindas_exibidas() or bool(self.get_form_errors())

    def _formulario_em_branco(self):
        """True quando a página é o formulário de cadastro e ele está vazio."""
        try:
            with self._sem_espera_implicita():
                campos = self.driver.find_elements(*self.FIRST_NAME_INPUT)
                return bool(campos) and not (campos[0].get_attribute("value") or "")
        except WebDriverException:
            return False

    def _reenviar_formulario(self):
        """Preenche e envia o cadastro de novo, quando a página voltou vazia."""
        dados = getattr(self, "_dados_formulario", None)
        if not dados:
            return False
        print("[Cadastro] Preenchendo e enviando o cadastro novamente...", flush=True)
        self.fill_register_form(**dados)
        self.submit_register()
        return True

    def get_success_message(self):
        """Aguarda o título de boas-vindas da página pós-registo.

        Se o Cloudflare interromper o envio, o teste pausa para a validação humana e,
        quando a página volta ao formulário vazio, preenche e envia o cadastro de novo.
        """
        reenvios = 0
        while True:  # envio original + até 2 reenvios, sempre aguardando a resposta
            if self.aguardar(lambda _driver: self._resultado_chegou()):
                break
            if not self._formulario_em_branco():
                # Nada apareceu na tela: pausa para a validação humana (Cloudflare).
                self._pausa_assistida(
                    lambda _driver: self._resultado_chegou(), "resposta do cadastro"
                )
                if self._resultado_chegou() or not self._formulario_em_branco():
                    break
            if reenvios >= 2:
                break
            # O Cloudflare interrompeu o envio e o site devolveu o formulário vazio.
            print(
                "[Cadastro] O Cloudflare interrompeu o envio e o formulário voltou vazio. "
                "Validando na janela do navegador antes de reenviar o cadastro.",
                flush=True,
            )
            self._pausa_assistida(
                lambda _driver: False,
                "envio do cadastro interrompido",
                prazo=ESPERA_VERIFICACAO_HUMANA,
                seguir_no_limite=True,
            )
            reenvios += 1
            self._reenviar_formulario()

        mensagem = self.safe_text(self.SUCCESS_MESSAGE)
        if not self._boas_vindas_exibidas():
            errors = self.get_form_errors()
            detalhe = "; ".join(errors) if errors else "nenhum erro de validação exibido"
            raise AssertionError(f"O registo não foi concluído ({detalhe}).")
        return mensagem