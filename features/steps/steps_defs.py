import random
import time

from behave import given, when, then

from config.leitor import parametros
from pages.register_page import RegisterPage
from pages.login_page import LoginPage
from pages.transfer_page import TransferPage


def human_type(element, text):
    """Simula a digitação de um ser humano, inserindo caractere por caractere com uma pausa leve."""
    element.clear()
    intervalo_min = parametros.decimal("digitacao_intervalo_min")
    intervalo_max = parametros.decimal("digitacao_intervalo_max")
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(intervalo_min, intervalo_max))

@given('que acesso a página de cadastro do ParaBank')
def step_impl(context):
    context.register_page = RegisterPage(context.driver)
    context.register_page.open()

@when('preencho o formulário de registro com dados válidos e exclusivos')
def step_impl(context):
    # Username curto e único (o ParaBank limita o username a 20 caracteres)
    context.test_username, context.test_password = parametros.credenciais("CADASTRO")
    
    context.register_page.fill_register_form(
        **parametros.formulario("CADASTRO", context.test_username)
    )

@when('clico no botão de registro')
def step_impl(context):
    context.register_page.submit_register()

@then('o sistema deve criar a conta com sucesso e exibir uma mensagem de boas-vindas')
def step_impl(context):
    msg = context.register_page.get_success_message()
    assert parametros.texto("mensagem_boas_vindas") in msg, f"Mensagem inesperada: {msg}"

@given('que possuo um usuário ativo cadastrado no sistema')
def step_impl(context):
    context.register_page = RegisterPage(context.driver)
    context.register_page.open()
    context.test_username, context.test_password = parametros.credenciais("LOGIN")
    
    context.register_page.fill_register_form(
        **parametros.formulario("LOGIN", context.test_username)
    )
    context.register_page.submit_register()
    context.driver.get(parametros.texto("url_logout"))

@given('estou na página inicial de login do ParaBank')
@given('que estou na página inicial de login do ParaBank')
def step_impl(context):
    context.login_page = LoginPage(context.driver)
    context.login_page.open()
    time.sleep(parametros.decimal("pausa_curta"))

@when('informo meu usuário e senha válidos')
def step_impl(context):
    login = context.login_page
    time.sleep(parametros.decimal("pausa_curta"))
    human_type(login.find_element(login.USERNAME_INPUT), context.test_username)
    human_type(login.find_element(login.PASSWORD_INPUT), context.test_password)

@when('clico no botão de login')
def step_impl(context):
    time.sleep(parametros.decimal("pausa_curta"))
    context.login_page.click(context.login_page.LOGIN_BUTTON)

@then('devo ser autenticado com sucesso e redirecionado para a visão geral das contas')
def step_impl(context):
    assert context.login_page.is_logged_in(), "O login falhou, o utilizador não se encontra autenticado."

@when('informo o usuário "{usuario}" e a senha "{senha}"')
def step_impl(context, usuario, senha):
    context.login_page = LoginPage(context.driver)
    context.login_page.open()
    login = context.login_page
    target_user = getattr(context, "test_username", parametros.texto("usuario_fallback")) if usuario == parametros.texto("usuario_reservado_ultimo_cadastro") else usuario
    
    time.sleep(parametros.decimal("pausa_login")) # Pausa ligeiramente maior para garantir o carregamento completo no encadeamento de cenários
    if target_user:
        human_type(login.find_element(login.USERNAME_INPUT), target_user)
    if senha:
        human_type(login.find_element(login.PASSWORD_INPUT), senha)

@when('informo o usuário "" e a senha ""')
def step_impl(context):
    context.login_page = LoginPage(context.driver)
    context.login_page.open()
    login = context.login_page
    time.sleep(parametros.decimal("pausa_login"))
    login.find_element(login.USERNAME_INPUT).clear()
    login.find_element(login.PASSWORD_INPUT).clear()

@then('o sistema deve recusar o acesso e exibir a mensagem de erro esperada')
def step_impl(context):
    error_msg = context.login_page.get_error_message()
    assert len(error_msg) > 0, "Deveria ter apresentado uma mensagem de erro para credenciais inválidas."

@given('que estou logado no ParaBank e possuo saldo suficiente na conta de origem')
def step_impl(context):
    context.register_page = RegisterPage(context.driver)
    context.register_page.open()
    username, password = parametros.credenciais("TRANSFERENCIA")
    
    context.register_page.fill_register_form(
        **parametros.formulario("TRANSFERENCIA", username)
    )
    context.register_page.submit_register()
    assert parametros.texto("mensagem_boas_vindas") in context.register_page.get_success_message(), "Não foi possível registrar o usuário para a transferência."

    # Um usuário novo tem apenas uma conta; abrimos uma segunda para poder transferir entre contas
    context.transfer_page = TransferPage(context.driver)
    context.transfer_page.open_new_account()
    
    context.login_page = LoginPage(context.driver)
    if not context.login_page.is_logged_in():
        context.login_page.open()
        human_type(context.login_page.find_element(context.login_page.USERNAME_INPUT), username)
        human_type(context.login_page.find_element(context.login_page.PASSWORD_INPUT), password)
        context.login_page.click(context.login_page.LOGIN_BUTTON)
    assert context.login_page.is_logged_in()

@when('navego para a seção de transferência de fundos')
def step_impl(context):
    context.transfer_page = TransferPage(context.driver)
    context.transfer_page.open()

@when('informo um valor válido para transferência')
def step_impl(context):
    context.transfer_amount = parametros.texto("valor_transferencia")

@when('seleciono a conta de origem e a conta de destino')
def step_impl(context):
    pass

@when('confirmo a operação de transferência')
def step_impl(context):
    time.sleep(parametros.decimal("pausa_curta"))
    context.transfer_page.perform_transfer(context.transfer_amount)

@then('o recibo com os detalhes da transação deve ser exibido na tela')
@then('a transferência deve ser processada com sucesso')
def step_impl(context):
    success_text = context.transfer_page.get_success_message()
    mensagens_esperadas = parametros.lista("mensagens_sucesso_transferencia")
    assert any(mensagem in success_text for mensagem in mensagens_esperadas), f"Mensagem de sucesso inesperada: {success_text}"