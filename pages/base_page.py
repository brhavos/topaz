import os
import sys
import time
from contextlib import contextmanager

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
    WebDriverException,
)

from config.leitor import parametros


# Pasta onde o diagnóstico das pausas é registrado
PASTA_DOCS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs")


# Textos que aparecem na tela de verificação anti-bot do Cloudflare
SINAIS_VERIFICACAO_HUMANA = (
    "verificação de segurança",
    "verificando se você é humano",
    "confirme que é humano",
    "verifique se você é humano",
    "verifying you are human",
    "verify you are human",
    "checking your browser",
    "just a moment",
    "executando verificação",
    "um momento",
)

# Títulos de página usados pelo Cloudflare nos desafios anti-bot
TITULOS_VERIFICACAO_HUMANA = (
    "just a moment",
    "um momento",
    "atencão necessária",
    "attention required",
)

# Tempo (em segundos) que o teste espera, após o pedido de verificação de humanidade,
# a página ser liberada. Passado esse prazo sem liberar, o teste falha.
# Configurável na planilha (config/parametros.xlsx), chave "espera_verificacao_humana".
ESPERA_VERIFICACAO_HUMANA = parametros.decimal("espera_verificacao_humana")

# Tempo de pausa quando a página só não respondeu como esperado (sem sinal de Cloudflare)
ESPERA_PAUSA_GENERICA = 60

# Intervalo (em segundos) entre as verificações da página durante a espera
INTERVALO_VERIFICACAO = 1


class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.timeout = parametros.decimal("tempo_espera_padrao")

    def abrir(self, url):
        """Navega para a URL e, se o Cloudflare pedir verificação, aguarda a confirmação humana."""
        self.driver.get(url)
        self.aguardar_verificacao_humana()
        self.aguardar_pagina_carregada()

    def _avisar(self, mensagem):
        """Escreve no console real, fora da captura de saída dos steps do behave.

        Durante cada step o behave substitui o sys.stdout por um buffer e só mostra
        o conteúdo no fim (ou quando o step falha). Escrever no sys.__stdout__ faz a
        mensagem aparecer na hora, que é o objetivo da pausa assistida.
        """
        destino = sys.__stdout__ or sys.stdout
        try:
            print(mensagem, file=destino, flush=True)
        except (OSError, ValueError):
            print(mensagem, flush=True)

    @contextmanager
    def _sem_espera_implicita(self):
        """Zera a espera implicita durante uma leitura rápida da página.

        A espera implicita vale para cada busca, inclusive quando se espera que o
        elemento NÃO exista. Como as sondas abaixo fazem várias buscas que voltam
        vazias, cada sonda custaria vários segundos e deixaria o teste arrastado.
        A configuração original é restaurada ao final.

        Pode ser usada dentro de si mesma: só a camada mais externa liga e desliga.
        """
        profundidade = getattr(self, "_sem_espera_profundidade", 0)
        self._sem_espera_profundidade = profundidade + 1
        try:
            if profundidade == 0:
                try:
                    self.driver.implicitly_wait(0)
                except WebDriverException:
                    pass
            yield
        finally:
            self._sem_espera_profundidade = profundidade
            if profundidade == 0:
                try:
                    self.driver.implicitly_wait(parametros.decimal("espera_implicita"))
                except WebDriverException:
                    pass

    def _verificacao_humana_pendente(self):
        """True quando alguma janela do navegador está no desafio anti-bot do Cloudflare."""
        try:
            original = self.driver.current_window_handle
            janelas = list(self.driver.window_handles)
        except WebDriverException:
            return False

        with self._sem_espera_implicita():
            if len(janelas) == 1:
                return self._janela_com_desafio()

            # O desafio pode ser aberto numa aba/janela nova: olha todas.
            try:
                for janela in janelas:
                    try:
                        self.driver.switch_to.window(janela)
                    except WebDriverException:
                        continue
                    if self._janela_com_desafio():
                        return True
                return False
            finally:
                try:
                    self.driver.switch_to.window(original)
                except WebDriverException:
                    pass

    def _janela_com_desafio(self):
        """Sinais do desafio do Cloudflare na janela atualmente em foco."""
        try:
            if self.driver.find_elements(By.CSS_SELECTOR, "iframe[src*='challenges.cloudflare.com']"):
                return True
            if self.driver.find_elements(By.CSS_SELECTOR, "script[src*='cdn-cgi/challenge-platform']"):
                return True
            for seletor in ("#challenge-form", "#cf-challenge-running", ".cf-browser-verification"):
                if self.driver.find_elements(By.CSS_SELECTOR, seletor):
                    return True
            titulo = (self.driver.title or "").lower()
            if any(sinal in titulo for sinal in TITULOS_VERIFICACAO_HUMANA):
                return True
            # A página de desafio do Cloudflare sempre define este objeto global.
            if self.driver.execute_script("return typeof window._cf_chl_opt !== 'undefined'"):
                return True
            texto = self.driver.execute_script(
                "return document.body ? document.body.innerText : ''"
            ) or ""
        except WebDriverException:
            return False
        return any(sinal in texto.lower() for sinal in SINAIS_VERIFICACAO_HUMANA)

    def _diagnostico_pagina(self):
        """Resumo da tela atual (URL, título, iframes e texto) para orientar a validação."""
        with self._sem_espera_implicita():
            return self._diagnostico_pagina_sem_espera()

    def _diagnostico_pagina_sem_espera(self):
        """Leitura da tela sem a espera implicita (ver _diagnostico_pagina)."""
        try:
            url = self.driver.current_url
            titulo = self.driver.title
            janelas = len(self.driver.window_handles)
            iframes = [
                (elemento.get_attribute("src") or "(sem src)")
                for elemento in self.driver.find_elements(By.CSS_SELECTOR, "iframe")
            ]
            texto = self.driver.execute_script(
                "return document.body ? document.body.innerText : ''"
            ) or ""
        except WebDriverException as erro:
            return f"não foi possível ler a página ({type(erro).__name__})"
        texto = " ".join(texto.split())[:160]
        return (
            f"url={url} | titulo={titulo!r} | janelas={janelas} | "
            f"iframes={iframes} | texto={texto!r}"
        )

    def _registrar_diagnostico(self, descricao):
        """Grava o diagnóstico da tela no console e em "docs/diagnostico_pausa.txt"."""
        detalhe = self._diagnostico_pagina()
        self._avisar(f"  Diagnostico: {detalhe}")
        try:
            caminho = os.path.join(PASTA_DOCS, "diagnostico_pausa.txt")
            os.makedirs(PASTA_DOCS, exist_ok=True)
            with open(caminho, "a", encoding="utf-8") as arquivo:
                arquivo.write(
                    f"{time.strftime('%Y-%m-%d %H:%M:%S')} | pausa por: {descricao} | {detalhe}\n"
                )
        except OSError:
            pass

    def _condicao_atendida(self, condicao):
        """Avalia uma condição do Selenium sem deixar a exceção escapar.

        A espera implicita é zerada porque quem espera aqui é o laço de polling:
        mantê-la faria cada verificação bloquear por vários segundos.
        """
        with self._sem_espera_implicita():
            try:
                return bool(condicao(self.driver))
            except (WebDriverException, TypeError):
                return False

    def _pausa_assistida(self, condicao, descricao="", prazo=None, seguir_no_limite=False):
        """Espera alguns segundos a página liberar, avisando no console.

        Não existe confirmação manual: quando o Cloudflare pede verificação, o teste
        apenas aguarda ESPERA_VERIFICACAO_HUMANA segundos. Se a página não liberar
        nesse prazo, o teste falha (ou devolve False, quando quem chamou pediu para
        seguir em frente). Devolve True quando a condição foi atendida.
        """
        if self._condicao_atendida(condicao):
            return True

        cloudflare = self._verificacao_humana_pendente()
        if prazo is None:
            prazo = ESPERA_VERIFICACAO_HUMANA if cloudflare else ESPERA_PAUSA_GENERICA
        barra = "=" * 78
        self._avisar("")
        self._avisar(barra)
        if cloudflare:
            self._avisar("  CLOUDFLARE PEDIU VERIFICAÇÃO DE HUMANIDADE")
            self._avisar(
                "  Valide na janela do navegador. O teste aguarda "
                f"{prazo}s e falha se a página não liberar."
            )
        else:
            self._avisar("  O TESTE ESTÁ AGUARDANDO A PÁGINA RESPONDER")
            if descricao:
                self._avisar(f"  Aguardando: {descricao}")
            self._avisar(f"  Se o navegador pedir confirmação de humanidade, valide agora ({prazo}s).")
        self._avisar(barra)
        self._registrar_diagnostico(descricao or "desafio do Cloudflare")

        inicio = time.time()
        limite = inicio + prazo
        while time.time() < limite:
            time.sleep(INTERVALO_VERIFICACAO)
            if self._condicao_atendida(condicao):
                # Confirma numa segunda leitura: o navegador pode estar a recarregar
                # a página nesse instante e a primeira leitura ser enganosa.
                time.sleep(0.3)
                if self._condicao_atendida(condicao):
                    decorrido = round(time.time() - inicio, 1)
                    self._avisar("")
                    self._avisar(
                        f"[Pausa assistida] Página liberada em {decorrido}s. "
                        "Prosseguindo com o teste."
                    )
                    self._avisar("")
                    return True
            if not cloudflare and self._verificacao_humana_pendente():
                # O desafio apareceu durante a espera: passa a usar o prazo curto.
                cloudflare = True
                limite = time.time() + ESPERA_VERIFICACAO_HUMANA
                prazo = ESPERA_VERIFICACAO_HUMANA
                self._avisar("")
                self._avisar(barra)
                self._avisar("  CLOUDFLARE PEDIU VERIFICAÇÃO DE HUMANIDADE")
                self._avisar(
                    "  Valide na janela do navegador. O teste aguarda "
                    f"{prazo}s e falha se a página não liberar."
                )
                self._avisar(barra)

        if seguir_no_limite:
            self._avisar(
                f"[Pausa assistida] A página não liberou em {prazo}s. "
                "Prosseguindo automaticamente."
            )
            return False
        raise AssertionError(
            "A página não liberou dentro de "
            f"{prazo}s ({descricao or 'desafio do Cloudflare'}). "
            "Se o navegador estava pedindo verificação de humanidade, ela não foi "
            "concluída a tempo."
        )

    def aguardar_verificacao_humana(self):
        """Espera alguns segundos a verificação anti-bot ser liberada, se ela aparecer.

        Devolve True quando houve espera (e a página foi liberada) e False quando não
        havia desafio na tela. Se o desafio não liberar no prazo, o teste falha.
        """
        if not self._verificacao_humana_pendente():
            return False
        self._pausa_assistida(
            lambda _driver: not self._verificacao_humana_pendente(),
            "desafio do Cloudflare",
        )
        return True

    def aguardar_pagina_carregada(self):
        """Segura o teste enquanto a página estiver vazia (tela branca ou em branco)."""
        if self._pagina_vazia():
            self._pausa_assistida(
                lambda _driver: not self._pagina_vazia(),
                "página carregando o conteúdo esperado",
            )

    def _pagina_vazia(self):
        """True quando o documento não tem conteúdo visível (tela em branco)."""
        with self._sem_espera_implicita():
            try:
                texto = self.driver.execute_script(
                    "return document.body ? document.body.innerText.trim() : ''"
                ) or ""
                tem_formulario = self.driver.find_elements(By.CSS_SELECTOR, "form, input")
            except WebDriverException:
                return False
        return not texto and not tem_formulario

    def safe_text(self, locator):
        """Texto do elemento, tolerante a elementos obsoletos durante navegações/AJAX."""
        try:
            return self.driver.find_element(*locator).text
        except (NoSuchElementException, StaleElementReferenceException):
            return ""

    def _aguardar_com_pausa(self, condicao, timeout=None):
        """Aguarda a condição checando, a cada segundo, se o Cloudflare pediu verificação.

        Quando o desafio aparece no meio da espera, o teste pausa, espera a confirmação
        humana e renova o prazo, em vez de deixar o tempo correr enquanto o humano valida.
        Devolve o valor da condição ou False se o tempo estourar.
        """
        prazo = self.timeout if timeout is None else timeout
        limite = time.time() + prazo
        proxima_checagem = 0
        while True:
            resultado = self._condicao_atendida(condicao)
            if resultado:
                return resultado
            if time.time() >= proxima_checagem:
                proxima_checagem = time.time() + 1
                if self._verificacao_humana_pendente():
                    self.aguardar_verificacao_humana()
                    limite = time.time() + prazo
                    continue
            if time.time() >= limite:
                return False
            time.sleep(0.3)

    def _esperar(self, condicao, descricao=""):
        """Espera uma condição do Selenium; se ela estourar, dá chance à validação humana."""
        if self._aguardar_com_pausa(condicao):
            return condicao(self.driver)
        self._pausa_assistida(condicao, descricao)
        if self._aguardar_com_pausa(condicao, timeout=min(self.timeout, 10)):
            return condicao(self.driver)
        raise TimeoutException(f"Elemento não apareceu mesmo após a pausa assistida: {descricao}")

    def find_element(self, locator):
        """Aguarda e retorna um elemento visível."""
        return self._esperar(
            EC.visibility_of_element_located(locator),
            f"elemento visível {locator}",
        )

    def click(self, locator):
        """Clica em um elemento após garantir que é clicável."""
        element = self._esperar(
            EC.element_to_be_clickable(locator),
            f"elemento clicável {locator}",
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

    def aguardar(self, condicao):
        """Aguarda uma condição; devolve True se ela ocorreu e False se estourou o tempo."""
        return bool(self._aguardar_com_pausa(condicao))