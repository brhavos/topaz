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
    ("TRANSFERENCIA", "valor_transferencia", 25,
     "Valor transferido entre as contas"),

    # --------------------------------------------------------------- MENSAGENS
    ("MENSAGENS", "mensagem_boas_vindas", "Welcome",
     "Texto esperado na pagina apos o cadastro ser concluido"),
    ("MENSAGENS", "mensagem_transferencia_concluida", "Transfer Complete",
     "Texto aguardado no painel apos confirmar a transferencia"),
    ("MENSAGENS", "mensagens_sucesso_transferencia", "Transfer Complete;Successfully;Amount",
     "Textos aceitos como sucesso da transferencia, separados por ';'"),

    # --------------------------------------------------------------- EVIDENCIAS
    ("EVIDENCIAS", "pasta_evidencias", "evidencias",
     "Pasta onde os prints de evidencia sao salvos a cada cenario"),
]

CABECALHO_CADASTRO = (
    "PERFIL", "primeiro_nome", "sobrenome", "endereco", "cidade", "estado",
    "cep", "telefone", "ssn", "senha", "prefixo_usuario",
)

# PERFIL, nome, sobrenome, endereco, cidade, estado, cep, telefone, ssn, senha, prefixo
DADOS_CADASTRO = [
    ("CADASTRO", "Carlos", "Silva", "Rua Teste, 123", "Campinas", "SP", "13000", "19999999999", "", "Senha123@", "qa_"),
    ("LOGIN", "Teste", "QA", "Rua A", "Campinas", "SP", "13000", "19999999999", "", "Password123", "lg_"),
    ("TRANSFERENCIA", "Transfer", "User", "Rua B", "Campinas", "SP", "13000", "19999999999", "", "Password123", "tr_"),
]

INSTRUCOES = [
    ("COMO ALTERAR OS PARAMETROS DE TESTE", ""),
    ("", ""),
    ("1)", "Abra a aba PARAMETROS e edite a coluna VALOR das chaves que deseja alterar."),
    ("2)", "Abra a aba DADOS_CADASTRO para alterar nomes, enderecos, senhas e prefixos de usuario."),
    ("3)", "Salve a planilha e execute os testes normalmente (executa.bat ou o comando behave)."),
    ("", ""),
    ("OBSERVACOES", ""),
    ("-", "Nao renomeie as abas nem as chaves da coluna CHAVE: os testes localizam os valores por esses nomes."),
    ("-", "Na aba DADOS_CADASTRO, ssn vazio faz o teste gerar um SSN exclusivo automaticamente."),
    ("-", "O campo senha e o prefixo_usuario de cada perfil podem ser alterados livremente."),
    ("-", "Valores booleanos aceitam True/False (tambem Sim/Nao)."),
    ("-", "mensagens_sucesso_transferencia aceita varios textos separados por ';'."),
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
    _ajustar_larguras(aba_cadastro, (16, 15, 14, 18, 12, 8, 8, 14, 12, 16, 16))

    aba_instrucoes = planilha.create_sheet("INSTRUCOES")
    for linha in INSTRUCOES:
        aba_instrucoes.append(linha)
    aba_instrucoes["A1"].font = Font(bold=True, size=12)
    aba_instrucoes["A7"].font = Font(bold=True)
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
