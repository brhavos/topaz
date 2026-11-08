import os
import random
import time

from behave import given, when, then

from config.leitor import parametros
from config.log_transacoes import CAMINHO_LOG_TRANSACOES
from config.log_transacoes import registrar as registrar_transacao
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
    context.test_username, context.test_password = username, password

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

# ------------------------------------------------------- massa de usuários
@when('registro todos os usuários válidos da planilha de parâmetros')
def step_impl(context):
    context.register_page = RegisterPage(context.driver)
    usuarios = parametros.usuarios("VALIDO")
    assert usuarios, "Nenhum usuário do tipo VALIDO com ativo = S encontrado na aba DADOS_CADASTRO."

    cadastrados = 0
    falhas = []
    for indice, dados in enumerate(usuarios, start=1):
        rotulo = f"{dados['perfil']} ({dados['first']} {dados['last']})"
        try:
            username = parametros.novo_usuario(dados.get("prefixo_usuario"))
            context.register_page.open()
            context.register_page.fill_register_form(
                **parametros.formulario(dados["perfil"], username)
            )
            context.register_page.submit_register()
            mensagem = context.register_page.get_success_message()
            assert parametros.texto("mensagem_boas_vindas") in mensagem, f"mensagem inesperada: {mensagem!r}"
            cadastrados += 1
            print(f"[Cadastro] {indice}/{len(usuarios)} - {rotulo}: OK ({username})")
        except Exception as erro:  # noqa: BLE001 - acumula as falhas da massa
            falhas.append(f"{rotulo}: {erro}")
            print(f"[Cadastro] {indice}/{len(usuarios)} - {rotulo}: FALHOU ({erro})")
        finally:
            # Encerra a sessão para o próximo cadastro começar do zero.
            context.driver.get(parametros.texto("url_logout"))

    context.usuarios_validos_cadastrados = cadastrados
    assert not falhas, "Usuários válidos não cadastrados:\n" + "\n".join(falhas)

@when('tento registrar todos os usuários inválidos da planilha de parâmetros')
def step_impl(context):
    context.register_page = RegisterPage(context.driver)
    usuarios = parametros.usuarios("INVALIDO")
    assert usuarios, "Nenhum usuário do tipo INVALIDO com ativo = S encontrado na aba DADOS_CADASTRO."

    recusados = 0
    falhas = []
    for indice, dados in enumerate(usuarios, start=1):
        rotulo = f"{dados['perfil']} ({dados['first']} {dados['last']})"
        esperado = (dados.get("erro_esperado") or "").strip()
        try:
            assert esperado, "O campo erro_esperado está vazio para um usuário inválido."
            username = parametros.novo_usuario(dados.get("prefixo_usuario"))
            context.register_page.open()
            # gerar_ssn=False preserva campos vazios (é o defeito que está sendo validado).
            context.register_page.fill_register_form(
                **parametros.formulario(dados["perfil"], username, gerar_ssn=False)
            )
            context.register_page.submit_register()

            limite = time.time() + parametros.decimal("tempo_espera_padrao")
            erros = context.register_page.get_form_errors()
            while not erros and time.time() < limite:
                time.sleep(0.2)
                erros = context.register_page.get_form_errors()

            assert erros, "O cadastro inválido não exibiu mensagem de erro."
            assert any(esperado.lower() in erro.lower() for erro in erros), (
                f"mensagem esperada {esperado!r}; exibidas: {erros}"
            )
            recusados += 1
            print(f"[Cadastro inválido] {indice}/{len(usuarios)} - {rotulo}: recusado ({esperado})")
        except Exception as erro:  # noqa: BLE001 - acumula as falhas da massa
            falhas.append(f"{rotulo}: {erro}")
            print(f"[Cadastro inválido] {indice}/{len(usuarios)} - {rotulo}: FALHOU ({erro})")

    context.usuarios_invalidos_recusados = recusados
    assert not falhas, "Usuários inválidos não recusados como esperado:\n" + "\n".join(falhas)

@then('todos os usuários válidos devem ser registrados com sucesso')
def step_impl(context):
    esperado = len(parametros.usuarios("VALIDO"))
    assert context.usuarios_validos_cadastrados == esperado, (
        f"{context.usuarios_validos_cadastrados} de {esperado} usuários válidos cadastrados."
    )

@then('todos os usuários inválidos devem ser recusados com a mensagem esperada')
def step_impl(context):
    esperado = len(parametros.usuarios("INVALIDO"))
    assert context.usuarios_invalidos_recusados == esperado, (
        f"{context.usuarios_invalidos_recusados} de {esperado} usuários inválidos recusados."
    )


# ------------------------------------------------ transferências em massa
def _registrar_no_log(context, origem, destino, valor, tipo, sucesso, mensagem):
    registrar_transacao(
        usuario=context.test_username,
        conta_origem=origem,
        conta_destino=destino,
        valor=valor,
        tipo=tipo,
        sucesso=sucesso,
        mensagem=mensagem,
    )

@when('realizo as transferências válidas configuradas na planilha')
def step_impl(context):
    quantidade = parametros.inteiro("quantidade_transferencias_validas")
    valores = parametros.sequencia("valores_transferencia_validos", quantidade)
    mensagens = parametros.lista("mensagens_sucesso_transferencia")

    context.transferencias_validas = 0
    for indice, valor in enumerate(valores, start=1):
        time.sleep(parametros.decimal("pausa_curta"))
        context.transfer_page.open()
        origem, destino = context.transfer_page.perform_transfer(valor)
        mensagem = context.transfer_page.get_success_message()
        assert any(mensagem_esperada in mensagem for mensagem_esperada in mensagens), (
            f"Transferência {indice} ({valor}) não concluída: {mensagem}"
        )
        _registrar_no_log(context, origem, destino, valor, "VALIDA", True, mensagem)
        context.transferencias_validas += 1
        print(f"[Transferência válida] {indice}/{len(valores)} - {valor}: OK ({origem} -> {destino})")

@when('realizo as transferências inválidas configuradas na planilha')
def step_impl(context):
    quantidade = parametros.inteiro("quantidade_transferencias_invalidas")
    tokens = parametros.sequencia("valores_transferencia_invalidos", quantidade)
    erro_esperado = parametros.texto("mensagem_erro_transferencia")
    sucesso = parametros.texto("mensagem_transferencia_concluida")

    context.transferencias_invalidas = 0
    for indice, token in enumerate(tokens, start=1):
        valor = "" if token.strip().lower() == "vazio" else token
        time.sleep(parametros.decimal("pausa_curta"))
        context.transfer_page.open()
        origem, destino = context.transfer_page.perform_transfer(valor)
        mensagem = context.transfer_page.aguardar_resultado(erro_esperado)
        assert erro_esperado.lower() in mensagem.lower(), (
            f"Transferência inválida {indice} ({token}) não exibiu erro: {mensagem}"
        )
        assert sucesso.lower() not in mensagem.lower(), (
            f"Transferência inválida {indice} ({token}) foi concluída: {mensagem}"
        )
        _registrar_no_log(context, origem, destino, valor, "INVALIDA", False, mensagem)
        context.transferencias_invalidas += 1
        print(f"[Transferência inválida] {indice}/{len(tokens)} - {token!r}: recusada")

@then('todas as transferências válidas devem ser concluídas com sucesso')
def step_impl(context):
    esperado = parametros.inteiro("quantidade_transferencias_validas")
    assert context.transferencias_validas == esperado, (
        f"{context.transferencias_validas} de {esperado} transferências válidas concluídas."
    )

@then('todas as transferências inválidas devem ser recusadas')
def step_impl(context):
    esperado = parametros.inteiro("quantidade_transferencias_invalidas")
    assert context.transferencias_invalidas == esperado, (
        f"{context.transferencias_invalidas} de {esperado} transferências inválidas recusadas."
    )

@then('o log de transações deve conter os dados das transferências válidas')
def step_impl(context):
    _validar_log(context, "VÁLIDA", context.transferencias_validas)

@then('o log de transações deve conter os dados das transferências inválidas')
def step_impl(context):
    _validar_log(context, "INVÁLIDA", context.transferencias_invalidas)

def _validar_log(context, classificacao, quantidade):
    assert os.path.isfile(CAMINHO_LOG_TRANSACOES), (
        f"Arquivo de log não encontrado: {CAMINHO_LOG_TRANSACOES}"
    )
    with open(CAMINHO_LOG_TRANSACOES, encoding="utf-8") as arquivo:
        conteudo = arquivo.read()

    marcador = f"Usuário.........: {context.test_username}"
    assert marcador in conteudo, "O log não contém o usuário das transferências."
    registros = [bloco for bloco in conteudo.split("TRANSAÇÃO ") if marcador in bloco and classificacao in bloco.split("\n", 1)[0]]
    assert len(registros) == quantidade, (
        f"O log deveria conter {quantidade} transferências {classificacao.lower()}s do usuário, "
        f"mas contém {len(registros)}."
    )