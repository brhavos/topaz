import os

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

def after_scenario(context, scenario):
    # Verifica se o navegador (Selenium) está ativo
    if hasattr(context, 'driver'):
        # Cria a pasta de evidências automaticamente se ela não existir
        pasta = parametros.texto("pasta_evidencias")
        os.makedirs(pasta, exist_ok=True)
        
        # Cria um nome limpo para o arquivo baseado no nome do seu cenário
        nome_limpo = scenario.name.replace(' ', '_').replace('/', '-')
        caminho_arquivo = os.path.join(pasta, f"{nome_limpo}.png")
        
        # Tira o print da tela e salva na pasta
        context.driver.save_screenshot(caminho_arquivo)
        print(f"\n[Print salvo]: {caminho_arquivo}")


def after_all(context):
    """Executado após todos os testes. Grava o histórico, o relatório e encerra o navegador."""
    if hasattr(context, 'driver'):
        context.driver.quit()

    # Grava a execução em docs/log.xlsx (mantém as 5 mais recentes).
    historico = getattr(context, 'historico', None)
    if historico is not None and not getattr(context.config, 'dry_run', False):
        historico.gravar()
        # Atualiza docs/docs_historico_testes.html com os dados da planilha.
        relatorio = gerar_relatorio()
        # Exibe o gráfico da execução no navegador padrão.
        if relatorio:
            abrir_relatorio(relatorio)
