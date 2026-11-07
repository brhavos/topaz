import os
from selenium import webdriver

def before_all(context):
    """Executado antes de todos os testes. Inicializa o navegador."""
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # Descomente se quiser correr em segundo plano
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    
    # Inicialização direta compatível com as versões recentes do Selenium (v4.6+)
    context.driver = webdriver.Chrome(options=options)
    context.driver.implicitly_wait(5)

def before_scenario(context, scenario):
    """Garante que cada cenário começa sem sessão autenticada (cenários independentes)."""
    if hasattr(context, 'driver'):
        context.driver.delete_all_cookies()

def after_scenario(context, scenario):
    # Verifica se o navegador (Selenium) está ativo
    if hasattr(context, 'driver'):
        # Cria uma pasta chamada 'evidencias' automaticamente se ela não existir
        os.makedirs("evidencias", exist_ok=True)
        
        # Cria um nome limpo para o arquivo baseado no nome do seu cenário
        nome_limpo = scenario.name.replace(' ', '_').replace('/', '-')
        caminho_arquivo = f"evidencias/{nome_limpo}.png"
        
        # Tira o print da tela e salva na pasta
        context.driver.save_screenshot(caminho_arquivo)
        print(f"\n[Print salvo]: {caminho_arquivo}")


def after_all(context):
    """Executado após todos os testes. Encerra o navegador."""
    if hasattr(context, 'driver'):
        context.driver.quit()