"""
Cria (ou recria) a planilha "config/parametros.xlsx" com os valores padrao.

Uso:
    python config/gerar_planilha.py            -> cria a planilha se ela nao existir
    python config/gerar_planilha.py --forcar   -> sobrescreve a planilha atual

Apos gerada, a planilha deve ser editada no Excel/LibreOffice: basta alterar a
coluna VALOR e executar os testes novamente. Os testes leem esses valores
atraves de "config/leitor.py".

Na aba DADOS_CADASTRO, o campo ssn pode ficar vazio: nesse caso um SSN
exclusivo e gerado automaticamente dentro da faixa ssn_minimo/ssn_maximo.
A coluna ativo (S/N) permite desligar um registro sem apagar a linha: os
testes executam somente os registros marcados com S. Todos nascem com S.
"""

import os
import sys

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

DIRETORIO = os.path.dirname(os.path.abspath(__file__))
CAMINHO_PLANILHA = os.path.join(DIRETORIO, "parametros.xlsx")

CABECALHO_PARAMETROS = ("SECAO", "CHAVE", "VALOR", "DESCRICAO")

# (secao, chave, valor, descricao)
PARAMETROS = [
    # ---------------------------------------------------------------- AMBIENTE
    ("AMBIENTE", "url_login", "https://parabank.parasoft.com/parabank/index.htm",
     "URL da pagina inicial de login"),
    ("AMBIENTE", "url_cadastro", "https://parabank.parasoft.com/parabank/register.htm",
     "URL da pagina de cadastro de usuario"),
    ("AMBIENTE", "url_transferencia", "https://parabank.parasoft.com/parabank/transfer.htm",
     "URL da pagina de transferencia de fundos"),
    ("AMBIENTE", "url_abrir_conta", "https://parabank.parasoft.com/parabank/openaccount.htm",
     "URL da pagina de abertura de nova conta"),
    ("AMBIENTE", "url_logout", "https://parabank.parasoft.com/parabank/logout.htm",
     "URL usada para encerrar a sessao entre cenarios"),

    # --------------------------------------------------------------- NAVEGADOR
    ("NAVEGADOR", "navegador_headless", False,
     "True executa o navegador em segundo plano (sem janela)"),
    ("NAVEGADOR", "navegador_maximizado", True,
     "True abre o navegador maximizado"),
    ("NAVEGADOR", "desativar_notificacoes", True,
     "True desativa as notificacoes do navegador"),
    ("NAVEGADOR", "espera_implicita", 5,
     "Espera implicita do driver, em segundos"),
    ("NAVEGADOR", "tempo_espera_padrao", 10,
     "Espera explicita padrao dos elementos, em segundos"),
    ("NAVEGADOR", "tempo_espera_login", 5,
     "Espera maxima para confirmar que o login foi efetuado, em segundos"),

    # ------------------------------------------------------------------ TEMPOS
    ("TEMPOS", "digitacao_intervalo_min", 0.05,
     "Pausa minima (segundos) entre cada caractere digitado"),
    ("TEMPOS", "digitacao_intervalo_max", 0.12,
     "Pausa maxima (segundos) entre cada caractere digitado"),
    ("TEMPOS", "pausa_curta", 0.5,
     "Pausa curta antes de clicar/submeter uma acao, em segundos"),
    ("TEMPOS", "pausa_login", 1.0,
     "Pausa extra antes de preencher o formulario de login, em segundos"),

    # ---------------------------------------------------------------- USUARIOS
    ("USUARIOS", "tamanho_sufixo_usuario", 9,
     "Quantidade de caracteres aleatorios no final do usuario criado (maximo aceito pelo ParaBank: 20 com o prefixo)"),
    ("USUARIOS", "ssn_minimo", 100000,
     "Valor minimo do SSN gerado aleatoriamente"),
    ("USUARIOS", "ssn_maximo", 999999,
     "Valor maximo do SSN gerado aleatoriamente"),
    ("USUARIOS", "usuario_reservado_ultimo_cadastro", "standard_user",
     "Valor usado nos Exemplos da feature de login para reaproveitar o usuario criado no cenario"),
    ("USUARIOS", "usuario_fallback", "usuario_padrao",
     "Usuario usado quando o cenario de login roda sem um usuario previamente criado"),

    # ----------------------------------------------------------- TRANSFERENCIA
    ("TRANSFERENCIA", "tipo_conta_nova", "SAVINGS",
     "Tipo da conta adicional aberta para permitir a transferencia (CHECKING ou SAVINGS)"),
    ("TRANSFERENCIA", "indice_conta_origem", 0,
     "Posicao (a partir de 0) da conta de origem na lista do formulario"),
    ("TRANSFERENCIA", "indice_conta_destino", 1,
     "Posicao (a partir de 0) da conta de destino na lista do formulario"),
    ("TRANSFERENCIA", "quantidade_transferencias_validas", 10,
     "Quantidade de transferencias validas executadas pelos testes"),
    ("TRANSFERENCIA", "quantidade_transferencias_invalidas", 3,
     "Quantidade de transferencias invalidas executadas pelos testes"),
    ("TRANSFERENCIA", "valores_transferencia_validos", "10;15;20;25;30;35;40;45;50;55",
     "Valores das transferencias validas da massa de testes, separados por ';'"),
    ("TRANSFERENCIA", "valores_transferencia_invalidos", "vazio;abc;25,00",
     "Valores invalidos de transferencia, separados por ';' (use 'vazio' para o campo em branco)"),

    # --------------------------------------------------------------- MENSAGENS
    ("MENSAGENS", "mensagem_boas_vindas", "Welcome",
     "Texto esperado na pagina apos o cadastro ser concluido"),
    ("MENSAGENS", "mensagem_transferencia_concluida", "Transfer Complete",
     "Texto aguardado no painel apos confirmar a transferencia"),
    ("MENSAGENS", "mensagem_erro_transferencia", "Error",
     "Texto exibido pelo sistema quando a transferencia e recusada"),
    ("MENSAGENS", "mensagens_sucesso_transferencia", "Transfer Complete;Successfully;Amount",
     "Textos aceitos como sucesso da transferencia, separados por ';'"),

    # --------------------------------------------------------------- EVIDENCIAS
    ("EVIDENCIAS", "pasta_evidencias", "evidencias",
     "Pasta onde os prints de evidencia sao salvos a cada cenario"),
]

CABECALHO_CADASTRO = (
    "PERFIL", "tipo", "primeiro_nome", "sobrenome", "endereco", "cidade", "estado",
    "cep", "telefone", "ssn", "senha", "prefixo_usuario", "erro_esperado", "ativo",
)

# PERFIL, tipo, nome, sobrenome, endereco, cidade, estado, cep, telefone, ssn,
# senha, prefixo, erro esperado (somente para os usuarios invalidos), ativo (S/N)
DADOS_CADASTRO = [
    # Perfis usados pelos cenarios de cadastro, login e transferencia
    ("CADASTRO", "PERFIL", "Carlos Henrique", "Ciccolani", "Rua Teste, 123", "Campinas", "SP",
     "13000", "19999999999", "", "Senha123@", "qa_", "", "S"),
    ("LOGIN", "PERFIL", "Renata", "Almeida", "Rua A", "Campinas", "SP",
     "13000", "19999999999", "", "Password123", "lg_", "", "S"),
    ("TRANSFERENCIA", "PERFIL", "Marcos Vinícius", "Prado", "Rua B", "Campinas", "SP",
     "13000", "19999999999", "", "Password123", "tr_", "", "S"),

    # 10 usuarios validos: ssn vazio -> o teste gera um SSN exclusivo automaticamente
    ("USR_VALIDO_01", "VALIDO", "Ana Beatriz", "Souza", "Rua das Palmeiras, 120", "Campinas", "SP",
     "13045-100", "19991110001", "", "Senha123@", "usr_", "", "S"),
    ("USR_VALIDO_02", "VALIDO", "Bruno", "Carvalho Lima", "Av. Andrade Neves, 455", "Campinas", "SP",
     "13013-161", "19991110002", "", "Senha123@", "usr_", "", "S"),
    ("USR_VALIDO_03", "VALIDO", "Camila", "Ferreira Dias", "Rua Júlia Lopes, 89", "Valinhos", "SP",
     "13270-000", "19991110003", "", "Senha123@", "usr_", "", "S"),
    ("USR_VALIDO_04", "VALIDO", "Daniel", "Almeida Rocha", "Rua do Comércio, 32", "Jundiaí", "SP",
     "13200-000", "19991110004", "", "Senha123@", "usr_", "", "S"),
    ("USR_VALIDO_05", "VALIDO", "Eduarda", "Martins Reis", "Av. Brasil, 1500", "Campinas", "SP",
     "13010-000", "19991110005", "", "Senha123@", "usr_", "", "S"),
    ("USR_VALIDO_06", "VALIDO", "Felipe", "Nogueira Prado", "Rua Aurora, 77", "Hortolândia", "SP",
     "13184-000", "19991110006", "", "Senha123@", "usr_", "", "S"),
    ("USR_VALIDO_07", "VALIDO", "Gabriela", "Rocha Mendes", "Rua das Acácias, 210", "Campinas", "SP",
     "13045-200", "19991110007", "", "Senha123@", "usr_", "", "S"),
    ("USR_VALIDO_08", "VALIDO", "Henrique", "Barbosa Silva", "Av. das Nações, 640", "Sumaré", "SP",
     "13170-000", "19991110008", "", "Senha123@", "usr_", "", "S"),
    ("USR_VALIDO_09", "VALIDO", "Isabela", "Prado Costa", "Rua Bela Vista, 15", "Campinas", "SP",
     "13076-000", "19991110009", "", "Senha123@", "usr_", "", "S"),
    ("USR_VALIDO_10", "VALIDO", "João Pedro", "Teixeira", "Rua São João, 303", "Paulínia", "SP",
     "13140-000", "19991110010", "", "Senha123@", "usr_", "", "S"),

    # 5 usuarios invalidos: nome de pessoa normal com um campo obrigatorio vazio
    ("USR_INVALIDO_01", "INVALIDO", "Mariana", "Oliveira Santos", "", "Campinas", "SP",
     "13045-300", "19991120001", "310001", "Senha123@", "inv_", "Address is required.", "S"),
    ("USR_INVALIDO_02", "INVALIDO", "Pedro Henrique", "Alves", "Rua Ibirá, 88", "", "SP",
     "13050-000", "19991120002", "310002", "Senha123@", "inv_", "City is required.", "S"),
    ("USR_INVALIDO_03", "INVALIDO", "Larissa", "Gomes Ribeiro", "Rua das Orquídeas, 41", "Campinas", "",
     "13060-000", "19991120003", "310003", "Senha123@", "inv_", "State is required.", "S"),
    ("USR_INVALIDO_04", "INVALIDO", "Thiago", "Moreira Castro", "Av. dos Imigrantes, 512", "Valinhos", "SP",
     "", "19991120004", "310004", "Senha123@", "inv_", "Zip Code is required.", "S"),
    ("USR_INVALIDO_05", "INVALIDO", "Fernanda", "Lima Duarte", "Rua Alvorada, 76", "Campinas", "SP",
     "13070-000", "19991120005", "", "Senha123@", "inv_", "Social Security Number is required.", "S"),
]

INSTRUCOES = [
    ("COMO ALTERAR OS PARAMETROS DE TESTE", ""),
    ("", ""),
    ("1)", "Abra a aba PARAMETROS e edite a coluna VALOR das chaves que deseja alterar."),
    ("2)", "Abra a aba DADOS_CADASTRO para alterar nomes, enderecos, senhas e prefixos de usuario."),
    ("2.1)", "Tipo PERFIL: dados dos cenarios existentes. Tipo VALIDO: massa registrada nos testes (10 usuarios). Tipo INVALIDO: cadastros recusados (5 usuarios, erro_esperado obrigatorio)."),
    ("2.2)", "Coluna ativo: use S para executar o registro e N para ignora-lo sem apagar a linha (padrao S)."),
    ("3)", "Salve a planilha e execute os testes normalmente (executa.bat ou o comando behave)."),
    ("", ""),
    ("OBSERVACOES", ""),
    ("-", "Nao renomeie as abas nem as chaves da coluna CHAVE: os testes localizam os valores por esses nomes."),
    ("-", "Na aba DADOS_CADASTRO, ssn vazio faz o teste gerar um SSN exclusivo automaticamente."),
    ("-", "Somente registros com ativo = S entram na massa de usuarios; os com N sao ignorados sem precisar apagar a linha."),
    ("-", "O campo senha e o prefixo_usuario de cada perfil podem ser alterados livremente."),
    ("-", "Valores booleanos aceitam True/False (tambem Sim/Nao)."),
    ("-", "mensagens_sucesso_transferencia aceita varios textos separados por ';'."),
    ("-", "quantidade_transferencias_validas e quantidade_transferencias_invalidas definem quantas transacoes executar (padrao 10 e 3)."),
    ("-", "Se a quantidade for maior que a lista, os valores de transferencia sao repetidos ciclicamente."),
    ("-", "Cada transacao e registrada em docs/log_transacoes.txt, com usuario, contas, valor, situacao e mensagem."),
    ("-", "Para recriar esta planilha com os valores de fabrica: python config/gerar_planilha.py --forcar"),
]


def _estilizar_cabecalho(aba, colunas):
    preenchimento = PatternFill("solid", fgColor="1F4E78")
    fonte = Font(bold=True, color="FFFFFF")

    for indice, titulo in enumerate(colunas, start=1):
        celula = aba.cell(row=1, column=indice, value=titulo)
        celula.fill = preenchimento
        celula.font = fonte
        celula.alignment = Alignment(horizontal="center", vertical="center")

    aba.freeze_panes = "A2"
    aba.auto_filter.ref = f"A1:{get_column_letter(len(colunas))}1"


def _ajustar_larguras(aba, larguras):
    for indice, largura in enumerate(larguras, start=1):
        aba.column_dimensions[get_column_letter(indice)].width = largura


def gerar_planilha():
    planilha = Workbook()

    aba_parametros = planilha.active
    aba_parametros.title = "PARAMETROS"
    aba_parametros.append(CABECALHO_PARAMETROS)
    for linha in PARAMETROS:
        aba_parametros.append(linha)
    _estilizar_cabecalho(aba_parametros, CABECALHO_PARAMETROS)
    _ajustar_larguras(aba_parametros, (16, 38, 55, 70))
    for linha in aba_parametros.iter_rows(min_row=2):
        linha[3].alignment = Alignment(wrap_text=True, vertical="center")

    aba_cadastro = planilha.create_sheet("DADOS_CADASTRO")
    aba_cadastro.append(CABECALHO_CADASTRO)
    for linha in DADOS_CADASTRO:
        aba_cadastro.append(linha)
    _estilizar_cabecalho(aba_cadastro, CABECALHO_CADASTRO)
    _ajustar_larguras(aba_cadastro, (17, 10, 16, 18, 26, 14, 8, 11, 14, 12, 14, 14, 30, 8))

    aba_instrucoes = planilha.create_sheet("INSTRUCOES")
    for linha in INSTRUCOES:
        aba_instrucoes.append(linha)
    for indice, linha in enumerate(INSTRUCOES, start=1):
        if linha[0] in ("COMO ALTERAR OS PARAMETROS DE TESTE", "OBSERVACOES"):
            aba_instrucoes.cell(row=indice, column=1).font = Font(bold=True, size=12)
    _ajustar_larguras(aba_instrucoes, (6, 100))

    planilha.save(CAMINHO_PLANILHA)
    return CAMINHO_PLANILHA


if __name__ == "__main__":
    forcar = "--forcar" in sys.argv[1:]
    if os.path.exists(CAMINHO_PLANILHA) and not forcar:
        print(f"Planilha ja existente em '{CAMINHO_PLANILHA}'.")
        print("Use --forcar para sobrescrever (as alteracoes manuais serao perdidas).")
    else:
        caminho = gerar_planilha()
        print(f"Planilha gerada em: {caminho}")
