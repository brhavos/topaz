import os
import re
import unicodedata
from datetime import datetime

from selenium import webdriver

from config.historico import HistoricoExecucao
from config.leitor import parametros
from config.relatorio import abrir as abrir_relatorio
from config.relatorio import gerar as gerar_relatorio


def before_all(context):
    """Executado antes de todos os testes. Inicializa o navegador e o histórico."""
    context.historico = HistoricoExecucao()

    options = webdriver.ChromeOptions()

    if parametros.booleano("navegador_headless"):
        options.add_argument("--headless")
    if parametros.booleano("navegador_maximizado"):
        options.add_argument("--start-maximized")
    if parametros.booleano("desativar_notificacoes"):
        options.add_argument("--disable-notifications")
    
    # Inicialização direta compatível com as versões recentes do Selenium (v4.6+)
    context.driver = webdriver.Chrome(options=options)
    context.driver.implicitly_wait(parametros.decimal("espera_implicita"))

def before_feature(context, feature):
    """Guarda a feature executada para o histórico da execução (docs/log.xlsx)."""
    if getattr(context, 'historico', None) is not None:
        context.historico.registrar_feature(feature)

def before_scenario(context, scenario):
    """Garante que cada cenário começa sem sessão autenticada (cenários independentes)."""
    if hasattr(context, 'driver'):
        context.driver.delete_all_cookies()

def _sanitizar(nome):
    """Deixa o texto seguro para nome de arquivo (sem acentos, espaços ou símbolos)."""
    nome = unicodedata.normalize("NFKD", str(nome or ""))
    nome = nome.encode("ascii", "ignore").decode("ascii")
    nome = re.sub(r"[^A-Za-z0-9]+", "_", nome)
    return nome.strip("_").lower()


def _nome_status(status):
    """Nome do status do behave, seja ele enum (Status.failed) ou texto."""
    return getattr(status, "name", str(status)).lower()


def _situacao(scenario):
    """Situação do cenário no nome da evidência: passed ou no_passed."""
    return "passed" if _nome_status(scenario.status) == "passed" else "no_passed"


def _step_evidencia(scenario):
    """Step que estava em execução: o que falhou ou, sem falha, o último executado."""
    steps = list(scenario.all_steps)
    if not steps:
        return ""

    for step in steps:
        if _nome_status(step.status) == "failed":
            return step.name

    executados = [
        step for step in steps
        if _nome_status(step.status) not in ("skipped", "untested")
    ]
    return (executados or steps)[-1].name


def _nome_evidencia(scenario, agora=None):
    """Monta aaaammdd_hhmmss-situacao-nome_do_cenario-nome_do_step."""
    agora = agora or datetime.now()
    partes = [
        agora.strftime("%Y%m%d_%H%M%S"),
        _situacao(scenario),
        _sanitizar(scenario.name),
        _sanitizar(_step_evidencia(scenario)),
    ]
    return "-".join(parte for parte in partes if parte)


def after_scenario(context, scenario):
    # Verifica se o navegador (Selenium) está ativo
    if hasattr(context, 'driver'):
        # Cria a pasta de evidências automaticamente se ela não existir
        pasta = parametros.texto("pasta_evidencias")
        os.makedirs(pasta, exist_ok=True)

        # Nome no padrão: aaaammdd_hhmmss-situacao-nome_do_cenario-nome_do_step
        caminho_arquivo = os.path.join(pasta, f"{_nome_evidencia(scenario)}.png")

        # Tira o print da tela e salva na pasta
        context.driver.save_screenshot(caminho_arquivo)
        print(f"\n[Print salvo]: {caminho_arquivo}")


def after_all(context):
    """Executado após todos os testes. Grava o histórico, o relatório e encerra o navegador."""
    if hasattr(context, 'driver'):
        context.driver.quit()

    # Grava a execução em docs/log.xlsx (sem limite, do mais recente para o mais antigo).
    historico = getattr(context, 'historico', None)
    if historico is not None and not getattr(context.config, 'dry_run', False):
        historico.gravar()
        # Atualiza docs/docs_historico_testes.html com os dados da planilha.
        relatorio = gerar_relatorio()
        # Exibe o gráfico da execução no navegador padrão.
        if relatorio:
            abrir_relatorio(relatorio)
