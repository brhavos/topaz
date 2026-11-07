"""
Leitura centralizada dos parametros de teste.

Todos os valores configuraveis do projeto ficam na planilha
"config/parametros.xlsx". Para alterar um parametro, basta editar a celula
da coluna VALOR e executar os testes normalmente (behave / executa.bat).

Estrutura da planilha:
  - Aba PARAMETROS.....: SECAO | CHAVE | VALOR | DESCRICAO
  - Aba DADOS_CADASTRO.: PERFIL | primeiro_nome | sobrenome | endereco | cidade
                         | estado | cep | telefone | ssn | senha | prefixo_usuario
"""

import os
import random
import uuid

from openpyxl import load_workbook

DIRETORIO = os.path.dirname(os.path.abspath(__file__))
CAMINHO_PLANILHA = os.path.join(DIRETORIO, "parametros.xlsx")

ABA_PARAMETROS = "PARAMETROS"
ABA_DADOS_CADASTRO = "DADOS_CADASTRO"

COLUNA_CHAVE = 2
COLUNA_VALOR = 3
PRIMEIRA_LINHA_DADOS = 2

VERDADEIROS = {"true", "1", "sim", "s", "yes", "verdadeiro"}

# Nome da coluna na aba DADOS_CADASTRO -> chave usada internamente
COLUNAS_CADASTRO = {
    "perfil": "perfil",
    "primeiro_nome": "first",
    "sobrenome": "last",
    "endereco": "address",
    "cidade": "city",
    "estado": "state",
    "cep": "zip_code",
    "telefone": "phone",
    "ssn": "ssn",
    "senha": "senha",
    "prefixo_usuario": "prefixo_usuario",
}


def _para_texto(valor):
    """Converte o conteudo de uma celula em texto (vazio quando a celula esta vazia)."""
    if valor is None:
        return ""
    if isinstance(valor, bool):
        return "True" if valor else "False"
    if isinstance(valor, float) and valor.is_integer():
        return str(int(valor))
    return str(valor).strip()


class Parametros:
    """Acesso aos parametros da planilha (lida uma unica vez e mantida em cache)."""

    def __init__(self, caminho=CAMINHO_PLANILHA):
        self.caminho = caminho
        self._valores = {}
        self._cadastro = {}
        self._carregar()

    # ------------------------------------------------------------------ leitura
    def _carregar(self):
        if not os.path.exists(self.caminho):
            raise FileNotFoundError(
                f"Planilha de parametros nao encontrada em '{self.caminho}'. "
                "Execute 'python config/gerar_planilha.py' para cria-la."
            )

        planilha = load_workbook(self.caminho, data_only=True)
        self._ler_parametros(planilha)
        self._ler_dados_cadastro(planilha)

    def _ler_parametros(self, planilha):
        if ABA_PARAMETROS not in planilha.sheetnames:
            raise KeyError(
                f"A aba '{ABA_PARAMETROS}' nao existe na planilha '{self.caminho}'."
            )

        for linha in planilha[ABA_PARAMETROS].iter_rows(
            min_row=PRIMEIRA_LINHA_DADOS, values_only=True
        ):
            if len(linha) < COLUNA_VALOR:
                continue
            chave = _para_texto(linha[COLUNA_CHAVE - 1])
            if not chave:
                continue
            self._valores[chave] = linha[COLUNA_VALOR - 1]

    def _ler_dados_cadastro(self, planilha):
        if ABA_DADOS_CADASTRO not in planilha.sheetnames:
            raise KeyError(
                f"A aba '{ABA_DADOS_CADASTRO}' nao existe na planilha '{self.caminho}'."
            )

        aba = planilha[ABA_DADOS_CADASTRO]
        cabecalho = next(aba.iter_rows(max_row=1, values_only=True), ())

        for linha in aba.iter_rows(min_row=PRIMEIRA_LINHA_DADOS, values_only=True):
            registro = {}
            for indice, coluna in enumerate(cabecalho):
                chave = COLUNAS_CADASTRO.get(_para_texto(coluna).lower())
                if chave:
                    registro[chave] = linha[indice] if indice < len(linha) else None

            perfil = _para_texto(registro.get("perfil")).upper()
            if perfil:
                self._cadastro[perfil] = registro

    # --------------------------------------------------------------- acessores
    def obter(self, chave):
        """Valor bruto da chave informada na aba PARAMETROS."""
        chave = str(chave).strip()
        if chave not in self._valores:
            raise KeyError(
                f"Parametro '{chave}' nao encontrado na aba '{ABA_PARAMETROS}' "
                f"da planilha '{self.caminho}'."
            )
        return self._valores[chave]

    def texto(self, chave):
        return _para_texto(self.obter(chave))

    def inteiro(self, chave):
        return int(float(self.texto(chave).replace(",", ".")))

    def decimal(self, chave):
        return float(self.texto(chave).replace(",", "."))

    def booleano(self, chave):
        valor = self.obter(chave)
        if isinstance(valor, bool):
            return valor
        return _para_texto(valor).lower() in VERDADEIROS

    def lista(self, chave, separador=";"):
        """Lista de valores separados por ';' (usada para mensagens esperadas)."""
        return [item for item in (parte.strip() for parte in self.texto(chave).split(separador)) if item]

    # ----------------------------------------------------------- dados de teste
    def dados_cadastro(self, perfil):
        """Dados cadastrais do perfil informado (aba DADOS_CADASTRO)."""
        perfil = str(perfil).strip().upper()
        if perfil not in self._cadastro:
            raise KeyError(
                f"Perfil '{perfil}' nao encontrado na aba '{ABA_DADOS_CADASTRO}' "
                f"da planilha '{self.caminho}'."
            )
        return dict(self._cadastro[perfil])

    def novo_usuario(self, prefixo=""):
        """Usuario exclusivo: prefixo do perfil + sufixo aleatorio de tamanho configuravel."""
        tamanho = self.inteiro("tamanho_sufixo_usuario")
        return f"{_para_texto(prefixo)}{uuid.uuid4().hex[:tamanho]}"

    def gerar_ssn(self):
        """SSN exclusivo (o ParaBank recusa SSN ja cadastrado)."""
        return str(random.randint(self.inteiro("ssn_minimo"), self.inteiro("ssn_maximo")))

    def credenciais(self, perfil):
        """Devolve (usuario exclusivo, senha) do perfil informado."""
        dados = self.dados_cadastro(perfil)
        return self.novo_usuario(dados.get("prefixo_usuario")), _para_texto(dados.get("senha"))

    def formulario(self, perfil, username):
        """Argumentos nomeados esperados por RegisterPage.fill_register_form."""
        dados = self.dados_cadastro(perfil)
        return {
            "first": _para_texto(dados.get("first")),
            "last": _para_texto(dados.get("last")),
            "address": _para_texto(dados.get("address")),
            "city": _para_texto(dados.get("city")),
            "state": _para_texto(dados.get("state")),
            "zip_code": _para_texto(dados.get("zip_code")),
            "phone": _para_texto(dados.get("phone")),
            "ssn": _para_texto(dados.get("ssn")) or self.gerar_ssn(),
            "username": username,
            "password": _para_texto(dados.get("senha")),
        }


parametros = Parametros()
