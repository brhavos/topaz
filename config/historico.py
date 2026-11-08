"""
Histórico das execuções de teste na planilha "docs/log.xlsx".

Cada execução do behave (executa.bat ou o comando behave) grava uma única linha
com a data, hora de início e de fim e as contagens de features, cenários e
steps por status (PASSED / FAILED / SKIPPED). A planilha não tem limite de
registros: todas as execuções são mantidas, sempre ordenadas da mais recente
para a mais antiga (a quantidade de linhas é controlada manualmente).

A gravação acontece uma única vez, no hook after_all de features/environment.py.
Ela nunca interrompe os testes: se não for possível escrever na planilha (por
exemplo, com o arquivo aberto no Excel), o console exibe um aviso e a execução
termina normalmente.

A planilha não precisa existir previamente: ela é criada com o título e o
cabeçalho padrão na primeira execução.

A leitura desses registros (usada pelo relatório HTML) fica em ler_registros().
"""

import os
from datetime import datetime

from openpyxl import Workbook, load_workbook

RAIZ_PROJETO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMINHO_LOG = os.path.join(RAIZ_PROJETO, "docs", "log.xlsx")

ABA_LOG = "Plan1"

TITULO = "HISTÓRICO DE EXECUÇÃO DE TESTES"

# Ordem das colunas da planilha (A até O).
CABECALHO = (
    "DATA", "HORA INÍCIO", "HORA FIM",
    "FEATURES", "PASSED", "FAILED", "SKIPPED",
    "CENÁRIOS", "PASSED", "FAILED", "SKIPPED",
    "STEPS", "PASSED", "FAILED", "SKIPPED",
)

# Grupos contados, na ordem em que aparecem no cabeçalho.
GRUPOS = ("features", "cenarios", "steps")

CATEGORIAS = ("passed", "failed", "skipped")


def _categoria(status):
    """Converte o status do behave em passed/failed/skipped."""
    nome = getattr(status, "name", str(status)).lower()
    if nome == "passed":
        return "passed"
    if nome in ("failed", "undefined"):
        return "failed"
    return "skipped"


def _somar(contador, status):
    contador[_categoria(status)] += 1


def _texto(valor):
    return "" if valor is None else str(valor).strip().upper()


def _ordenacao(valores):
    """Data e hora de início de uma linha, usadas para ordenar a planilha."""
    data = _formatar_data(valores[0])
    hora = _formatar_hora(valores[1])
    try:
        return datetime.strptime(f"{data} {hora}", "%d/%m/%Y %H:%M:%S")
    except ValueError:
        return datetime.min


class HistoricoExecucao:
    """Acumula o resultado da execução atual e o registra em docs/log.xlsx."""

    def __init__(self, caminho=CAMINHO_LOG):
        self.caminho = caminho
        self.inicio = datetime.now()
        self.fim = None
        self.features = []

    # ---------------------------------------------------------------- coleta
    def registrar_feature(self, feature):
        """Guarda a feature executada (chamado no hook before_feature)."""
        self.features.append(feature)

    def _contagens(self):
        """Conta features, cenários e steps da execução por status."""
        contagens = {grupo: {categoria: 0 for categoria in CATEGORIAS} for grupo in GRUPOS}

        for feature in self.features:
            _somar(contagens["features"], feature.status)
            for cenario in feature.walk_scenarios():
                _somar(contagens["cenarios"], cenario.status)
                for step in cenario.all_steps:
                    _somar(contagens["steps"], step.status)

        return contagens

    def _linha(self):
        """Monta a linha da planilha com data, horas e as contagens."""
        fim = self.fim or datetime.now()
        valores = [
            self.inicio.strftime("%d/%m/%Y"),
            self.inicio.strftime("%H:%M:%S"),
            fim.strftime("%H:%M:%S"),
        ]

        contagens = self._contagens()
        for grupo in GRUPOS:
            contagem = contagens[grupo]
            total = sum(contagem[categoria] for categoria in CATEGORIAS)
            valores.extend([total] + [contagem[categoria] for categoria in CATEGORIAS])

        return valores

    # --------------------------------------------------------------- escrita
    def _abrir_planilha(self):
        if os.path.exists(self.caminho):
            return load_workbook(self.caminho)

        os.makedirs(os.path.dirname(self.caminho), exist_ok=True)
        planilha = Workbook()
        planilha.active.title = ABA_LOG
        return planilha

    @staticmethod
    def _localizar_cabecalho(aba):
        """Devolve a linha do cabeçalho (primeira célula igual a DATA)."""
        for linha in range(1, min(aba.max_row, 20) + 1):
            if _texto(aba.cell(row=linha, column=1).value) == "DATA":
                return linha
        return None

    @staticmethod
    def _valores_existentes(aba, linha_cabecalho):
        """Linhas já preenchidas abaixo do cabeçalho, como listas de valores."""
        registros = []
        for linha in range(linha_cabecalho + 1, aba.max_row + 1):
            valores = [
                aba.cell(row=linha, column=coluna).value
                for coluna in range(1, len(CABECALHO) + 1)
            ]
            if all(valor in (None, "") for valor in valores):
                continue
            registros.append(valores)
        return registros

    def _preparar_cabecalho(self, aba):
        """Cria título e cabeçalho quando a planilha ainda está vazia."""
        if aba.max_row == 1 and aba.cell(row=1, column=1).value is None:
            aba.cell(row=1, column=1, value=TITULO)
            for coluna, titulo in enumerate(CABECALHO, start=1):
                aba.cell(row=2, column=coluna, value=titulo)
            return 2

        raise ValueError(
            f"cabeçalho (célula 'DATA') não encontrado na aba '{aba.title}' "
            f"da planilha '{self.caminho}'"
        )

    def _gravar_na_planilha(self):
        planilha = self._abrir_planilha()
        aba = planilha[ABA_LOG] if ABA_LOG in planilha.sheetnames else planilha.active

        linha_cabecalho = self._localizar_cabecalho(aba)
        if linha_cabecalho is None:
            linha_cabecalho = self._preparar_cabecalho(aba)

        # Sem limite de registros: mantém todas as execuções, sempre da mais
        # recente para a mais antiga.
        registros = self._valores_existentes(aba, linha_cabecalho)
        registros.append(self._linha())
        registros.sort(key=_ordenacao, reverse=True)

        if aba.max_row > linha_cabecalho:
            aba.delete_rows(linha_cabecalho + 1, aba.max_row - linha_cabecalho)

        for deslocamento, valores in enumerate(registros, start=1):
            for coluna, valor in enumerate(valores, start=1):
                aba.cell(row=linha_cabecalho + deslocamento, column=coluna, value=valor)

        planilha.save(self.caminho)

    def gravar(self):
        """Registra a execução atual. Nunca interrompe os testes."""
        if not self.features:
            return None

        self.fim = datetime.now()
        try:
            self._gravar_na_planilha()
        except Exception as erro:  # noqa: BLE001 - o histórico não pode derrubar a suíte
            print(f"\n[AVISO] Não foi possível gravar o histórico em '{self.caminho}': {erro}")
            return None

        print(f"\n[Histórico] Execução registrada em: {self.caminho}")
        return self.caminho


# ------------------------------------------------------------------ leitura
def _texto_valor(valor):
    return "" if valor is None else str(valor).strip()


def _inteiro(valor):
    try:
        return int(valor)
    except (TypeError, ValueError):
        return 0


def _formatar_data(valor):
    if isinstance(valor, datetime):
        return valor.strftime("%d/%m/%Y")
    return _texto_valor(valor)


def _formatar_hora(valor):
    if isinstance(valor, datetime):
        return valor.strftime("%H:%M:%S")
    if hasattr(valor, "strftime"):
        return valor.strftime("%H:%M:%S")
    return _texto_valor(valor)


def _registro(valores):
    """Converte uma linha da planilha em um dicionário do histórico."""
    registro = {
        "data": _formatar_data(valores[0]),
        "inicio": _formatar_hora(valores[1]),
        "fim": _formatar_hora(valores[2]),
    }

    for indice, grupo in enumerate(GRUPOS):
        base = 3 + indice * 4
        registro[grupo] = {
            "total": _inteiro(valores[base]),
            "passed": _inteiro(valores[base + 1]),
            "failed": _inteiro(valores[base + 2]),
            "skipped": _inteiro(valores[base + 3]),
        }

    return registro


def ler_registros(caminho=CAMINHO_LOG):
    """Lê docs/log.xlsx e devolve as execuções registradas (mais antiga primeiro)."""
    if not os.path.exists(caminho):
        return []

    planilha = load_workbook(caminho, data_only=True)
    aba = planilha[ABA_LOG] if ABA_LOG in planilha.sheetnames else planilha.active

    linha_cabecalho = HistoricoExecucao._localizar_cabecalho(aba)
    if linha_cabecalho is None:
        return []

    registros = []
    for linha in range(linha_cabecalho + 1, aba.max_row + 1):
        valores = [
            aba.cell(row=linha, column=coluna).value
            for coluna in range(1, len(CABECALHO) + 1)
        ]
        if all(valor in (None, "") for valor in valores):
            continue
        registros.append((_ordenacao(valores), _registro(valores)))

    registros.sort(key=lambda item: item[0])
    return [registro for _, registro in registros]
