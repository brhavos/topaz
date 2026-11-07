"""
Relatório HTML do histórico de testes ("docs/docs_historico_testes.html").

O relatório é atualizado automaticamente no fim de cada execução: os dados são
lidos de "docs/log.xlsx" (as MAX_HISTORICOS execuções mais recentes) e embutidos
no próprio HTML, dentro dos marcadores DADOS-INICIO / DADOS-FIM.

Embutir os dados (em vez de o navegador abrir a planilha) faz o relatório
funcionar com duplo clique no arquivo: navegadores bloqueiam a leitura de
arquivos locais via fetch/javascript quando a página é aberta com file://.

O restante do HTML é preservado: só o bloco entre os marcadores é reescrito,
então o layout pode ser editado à vontade no arquivo.

Assim como a gravação do histórico, a geração nunca interrompe os testes: em
caso de erro o console exibe um aviso e a execução termina normalmente.
"""

import json
import os
import webbrowser
from pathlib import Path

from config.historico import CAMINHO_LOG, GRUPOS, ler_registros

RAIZ_PROJETO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMINHO_HTML = os.path.join(RAIZ_PROJETO, "docs", "docs_historico_testes.html")

MARCADOR_INICIO = "/* DADOS-INICIO */"
MARCADOR_FIM = "/* DADOS-FIM */"


def _status(total, failed):
    """Status geral de uma execução: passed, failed ou skipped."""
    if failed:
        return "failed"
    return "passed" if total else "skipped"


def _dados_da_execucao(registro):
    """Acrescenta totais, taxa de sucesso e status ao registro da planilha."""
    dados = dict(registro)

    features = registro["features"]
    cenarios = registro["cenarios"]
    steps = registro["steps"]

    # Falha em qualquer nível reprova a execução (um step que falha derruba o
    # cenário e, por consequência, a feature).
    falhas = steps["failed"] + cenarios["failed"] + features["failed"]
    total = sum(sum(registro[grupo][categoria] for categoria in ("passed", "failed", "skipped")) for grupo in GRUPOS)

    dados["chave"] = f"{registro['data']} {registro['inicio']}".strip()
    dados["total"] = total
    dados["falhas"] = falhas
    dados["taxa"] = round((steps["passed"] / steps["total"]) * 100, 1) if steps["total"] else 0.0
    dados["status"] = _status(total, falhas)

    return dados


def montar_dados(caminho_log=CAMINHO_LOG):
    """Execuções registradas, prontas para o relatório (mais antiga primeiro)."""
    return [_dados_da_execucao(registro) for registro in ler_registros(caminho_log)]


def gerar(caminho_log=CAMINHO_LOG, caminho_html=CAMINHO_HTML):
    """Reescreve o bloco de dados do relatório HTML. Nunca interrompe os testes."""
    try:
        dados = montar_dados(caminho_log)

        with open(caminho_html, encoding="utf-8") as arquivo:
            html = arquivo.read()

        inicio = html.find(MARCADOR_INICIO)
        fim = html.find(MARCADOR_FIM)
        if inicio == -1 or fim == -1 or fim < inicio:
            raise ValueError(
                f"marcadores {MARCADOR_INICIO} / {MARCADOR_FIM} não encontrados no relatório"
            )

        # Alinha as linhas do JSON com o bloco de <script> (indentação só estética).
        dados_json = json.dumps(dados, ensure_ascii=False, indent=4).replace(
            "\n", "\n            "
        )
        bloco = f"\n        const execucoes = {dados_json};\n        "
        html = html[: inicio + len(MARCADOR_INICIO)] + bloco + html[fim:]

        with open(caminho_html, "w", encoding="utf-8", newline="\n") as arquivo:
            arquivo.write(html)
    except Exception as erro:  # noqa: BLE001 - o relatório não pode derrubar a suíte
        print(f"\n[AVISO] Não foi possível atualizar o relatório '{caminho_html}': {erro}")
        return None

    print(f"[Relatório] Histórico atualizado em: {caminho_html}")
    return caminho_html


def abrir(caminho_html=CAMINHO_HTML):
    """Abre o relatório no navegador padrão para exibir o gráfico da execução.

    Usa a URI do arquivo (file:///...) para funcionar também quando o caminho
    do projeto tem espaços ou acentos. Nunca interrompe os testes.
    """
    try:
        if not os.path.isfile(caminho_html):
            raise FileNotFoundError(f"arquivo não encontrado: {caminho_html}")

        aberto = webbrowser.open(Path(caminho_html).resolve().as_uri())
        if not aberto:
            print(f"\n[AVISO] Nenhum navegador padrão disponível para abrir '{caminho_html}'.")
            return None
    except Exception as erro:  # noqa: BLE001 - a visualização não pode derrubar a suíte
        print(f"\n[AVISO] Não foi possível abrir o relatório '{caminho_html}': {erro}")
        return None

    print("[Relatório] Gráfico aberto no navegador padrão.")
    return caminho_html
