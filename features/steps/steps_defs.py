import time
import random
import uuid
from behave import given, when, then
from pages.register_page import RegisterPage
from pages.login_page import LoginPage
from pages.transfer_page import TransferPage

def human_type(element, text):
    """Simula a digitação de um ser humano, inserindo caractere por caractere com uma pausa leve."""
    element.clear()
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.12))

@given('que acesso a página de cadastro do ParaBank')
def step_impl(context):
    context.register_page = RegisterPage(context.driver)
    context.register_page.open()

@when('preencho o formulário de registro com dados válidos e exclusivos')
def step_impl(context):
    # O ParaBank limita o username a 20 caracteres, por isso usamos um valor curto e único
    context.test_username = f"qa_{uuid.uuid4().hex[:9]}"
    context.test_password = "Senha123@"
    unique_ssn = str(random.randint(100000, 999999))
    
    context.register_page.fill_register_form(
        first="Carlos",
        last="Silva",
        address="Rua Teste, 123",
        city="Campinas",
        state="SP",
        zip_code="13000",
        phone="19999999999",
        ssn=unique_ssn,
        username=context.test_username,
        password=context.test_password
    )

@when('clico no botão de registro')
def step_impl(context):
    context.register_page.submit_register()

@then('o sistema deve criar a conta com sucesso e exibir uma mensagem de boas-vindas')
def step_impl(context):
    msg = context.register_page.get_success_message()
    assert "Welcome" in msg, f"Mensagem inesperada: {msg}"

@given('que possuo um usuário ativo cadastrado no sistema')
def step_impl(context):
    context.register_page = RegisterPage(context.driver)
    context.register_page.open()
    context.test_username = f"lg_{uuid.uuid4().hex[:9]}"
    context.test_password = "Password123"
    unique_ssn = str(random.randint(100000, 999999))
    
    context.register_page.fill_register_form(
        "Teste", "QA", "Rua A", "Campinas", "SP", "13000", "19999999999", unique_ssn, context.test_username, context.test_password
    )
    context.register_page.submit_register()
    context.driver.get("https://parabank.parasoft.com/parabank/logout.htm")

@given('estou na página inicial de login do ParaBank')
@given('que estou na página inicial de login do ParaBank')
def step_impl(context):
    context.login_page = LoginPage(context.driver)
    context.login_page.open()
    time.sleep(0.5)

@when('informo meu usuário e senha válidos')
def step_impl(context):
    login = context.login_page
    time.sleep(0.5)
    human_type(login.find_element(login.USERNAME_INPUT), context.test_username)
    human_type(login.find_element(login.PASSWORD_INPUT), context.test_password)

@when('clico no botão de login')
def step_impl(context):
    time.sleep(0.5)
    context.login_page.click(context.login_page.LOGIN_BUTTON)

@then('devo ser autenticado com sucesso e redirecionado para a visão geral das contas')
def step_impl(context):
    assert context.login_page.is_logged_in(), "O login falhou, o utilizador não se encontra autenticado."

@when('informo o usuário "{usuario}" e a senha "{senha}"')
def step_impl(context, usuario, senha):
    context.login_page = LoginPage(context.driver)
    context.login_page.open()
    login = context.login_page
    target_user = getattr(context, "test_username", "usuario_padrao") if usuario == "standard_user" else usuario
    
    time.sleep(1.0) # Pausa ligeiramente maior para garantir o carregamento completo no encadeamento de cenários
    if target_user:
        human_type(login.find_element(login.USERNAME_INPUT), target_user)
    if senha:
        human_type(login.find_element(login.PASSWORD_INPUT), senha)

@when('informo o usuário "" e a senha ""')
def step_impl(context):
    context.login_page = LoginPage(context.driver)
    context.login_page.open()
    login = context.login_page
    time.sleep(1.0)
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
    username = f"tr_{uuid.uuid4().hex[:9]}"
    password = "Password123"
    unique_ssn = str(random.randint(100000, 999999))
    
    context.register_page.fill_register_form(
        "Transfer", "User", "Rua B", "Campinas", "SP", "13000", "19999999999", unique_ssn, username, password
    )
    context.register_page.submit_register()
    assert "Welcome" in context.register_page.get_success_message(), "Não foi possível registrar o usuário para a transferência."

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
    context.transfer_amount = "25"

@when('seleciono a conta de origem e a conta de destino')
def step_impl(context):
    pass

@when('confirmo a operação de transferência')
def step_impl(context):
    time.sleep(0.5)
    context.transfer_page.perform_transfer(context.transfer_amount)

@then('o recibo com os detalhes da transação deve ser exibido na tela')
@then('a transferência deve ser processada com sucesso')
def step_impl(context):
    success_text = context.transfer_page.get_success_message()
    assert "Transfer Complete" in success_text or "Successfully" in success_text or "Amount" in success_text, f"Mensagem de sucesso inesperada: {success_text}"