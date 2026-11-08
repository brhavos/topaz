"""
Log das transações executadas nos testes de transferência.

Cada transação (válida ou inválida) é registrada em "docs/log_transacoes.txt"
com todos os dados da operação: data/hora, usuário, contas de origem e destino,
valor solicitado, classificação, situação e a mensagem devolvida pelo sistema.

O arquivo é incremental: uma execução nunca apaga o que já foi registrado, e um
novo cabeçalho de execução é escrito a cada vez que os testes são iniciados.
"""

import os
from datetime import datetime

RAIZ_PROJETO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMINHO_LOG_TRANSACOES = os.path.join(RAIZ_PROJETO, "docs", "log_transacoes.txt")

_execucao_iniciada = False
_numero_transacao = 0


def _texto(valor):
    return "" if valor is None else str(valor).strip()


def _cabecalho_execucao():
    linha = "=" * 78
    return (
        f"{linha}\n"
        "LOG DE TRANSAÇÕES - ParaBank\n"
        f"Execução iniciada em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
        f"{linha}\n"
    )


def registrar(usuario, conta_origem, conta_destino, valor, tipo, sucesso, mensagem):
    """Acrescenta uma transação ao log e devolve o texto gravado.

    usuario.........: usuário autenticado que fez a transferência
    conta_origem....: número da conta de origem
    conta_destino...: número da conta de destino
    valor...........: valor solicitado (vazio nos casos inválidos sem valor)
    tipo............: "VALIDA" ou "INVALIDA"
    sucesso.........: True quando o sistema concluiu a transferência
    mensagem........: texto exibido pelo sistema após o envio
    """
    global _execucao_iniciada, _numero_transacao

    os.makedirs(os.path.dirname(CAMINHO_LOG_TRANSACOES), exist_ok=True)

    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    with open(CAMINHO_LOG_TRANSACOES, "a", encoding="utf-8", newline="\n") as arquivo:
        if not _execucao_iniciada:
            arquivo.write(_cabecalho_execucao())
            _execucao_iniciada = True

        _numero_transacao += 1
        classificacao = "VÁLIDA" if str(tipo).strip().upper().startswith("VALID") else "INVÁLIDA"
        valor_exibido = _texto(valor) or "(vazio)"
        bloco = (
            f"\n[{_numero_transacao}] {agora} - TRANSAÇÃO {classificacao}\n"
            f"    Usuário.........: {_texto(usuario)}\n"
            f"    Conta origem....: {_texto(conta_origem)}\n"
            f"    Conta destino...: {_texto(conta_destino)}\n"
            f"    Valor solicitado: {valor_exibido}\n"
            f"    Situação........: {'CONCLUÍDA' if sucesso else 'RECUSADA'}\n"
            f"    Mensagem........: {' '.join(_texto(mensagem).split())}\n"
        )
        arquivo.write(bloco)

    return bloco
