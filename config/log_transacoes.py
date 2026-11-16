"""
Log das transações executadas nos testes de transferência.

Cada transação (válida ou inválida) é registrada em "docs/log_transacoes.txt"
com todos os dados da operação: data/hora, cenário BDD, step, usuário, contas de
origem e destino, valor solicitado, classificação, situação, a mensagem
devolvida pelo sistema e um comentário.

O comentário é "N/A" nas transações concluídas e, nas recusadas, descreve em
linguagem amigável o problema ocorrido, as possíveis causas e as sugestões de
solução.

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


def _diagnostico(valor):
    """Devolve (problema, causas prováveis, soluções possíveis) para o valor recusado."""
    if not valor:
        return (
            "o valor da transferência foi enviado em branco, então o sistema não "
            "tinha quantia para movimentar e devolveu um erro interno genérico.",
            "o campo de valor é obrigatório, mas o formulário aceita o envio sem "
            "preenchimento (falta de validação antes do envio).",
            "preencher um valor numérico maior que zero antes de clicar em Transfer; "
            "a correção definitiva é validar o campo no servidor e exibir uma mensagem "
            "clara, como \"Informe o valor da transferência\".",
        )

    if "," in valor:
        return (
            f"o valor \"{valor}\" usa vírgula como separador decimal, formato habitual "
            "no Brasil, mas o sistema só reconhece o ponto.",
            "o valor digitado não é normalizado para o formato numérico esperado "
            "(ponto decimal) e o campo não tem máscara nem validação de formato.",
            "informar o valor no formato 25.00; a correção recomendada é converter "
            "vírgula em ponto ou avisar \"Use ponto como separador decimal\".",
        )

    try:
        float(valor)
    except ValueError:
        return (
            f"o valor \"{valor}\" não é um número, então o sistema não conseguiu "
            "interpretar a quantia informada.",
            "o campo aceita texto livre e não há validação de tipo antes do envio.",
            "informar apenas dígitos; recomenda-se restringir a digitação a números "
            "e avisar \"O valor deve ser numérico\".",
        )

    return (
        f"o valor \"{valor}\" foi recusado pela instituição e a transferência não foi "
        "concluída.",
        "valor igual a zero, negativo ou acima do saldo disponível na conta de origem.",
        "usar um valor positivo e dentro do saldo disponível; a mensagem do sistema "
        "deveria detalhar o motivo da recusa.",
    )


# Recuo das linhas extras do campo Comentários (alinhado ao valor dos demais campos)
_RECUO_COMENTARIO = "\n" + " " * 8


def _comentario(valor, sucesso):
    """N/A nas transações concluídas; nas recusadas, um texto amigável e explicativo."""
    if sucesso:
        return "N/A"

    problema, causas, solucoes = _diagnostico(_texto(valor))
    return (
        f"{_RECUO_COMENTARIO}- Problema: {problema}"
        f"{_RECUO_COMENTARIO}- Causas prováveis: {causas}"
        f"{_RECUO_COMENTARIO}- Soluções possíveis: {solucoes}"
    )


def registrar(
    usuario, conta_origem, conta_destino, valor, tipo, sucesso, mensagem,
    cenario="", step="",
):
    """Acrescenta uma transação ao log e devolve o texto gravado.

    usuario.........: usuário autenticado que fez a transferência
    conta_origem....: número da conta de origem
    conta_destino...: número da conta de destino
    valor...........: valor solicitado (vazio nos casos inválidos sem valor)
    tipo............: "VALIDA" ou "INVALIDA"
    sucesso.........: True quando o sistema concluiu a transferência
    mensagem........: texto exibido pelo sistema após o envio
    cenario.........: nome do cenário BDD que originou a transação
    step............: nome do step BDD em execução
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
        # O comentário das transações recusadas é multilinha e já começa com quebra de linha
        comentario = _comentario(valor, sucesso)
        campo_comentario = (
            f"    Comentários.....{comentario}" if comentario.startswith("\n")
            else f"    Comentários.....: {comentario}"
        )

        bloco = (
            f"\n[{_numero_transacao}] {agora} - TRANSAÇÃO {classificacao}\n"
            f"    Cenário BDD.....: {_texto(cenario) or '(não informado)'}\n"
            f"    Step............: {_texto(step) or '(não informado)'}\n"
            f"    Usuário.........: {_texto(usuario)}\n"
            f"    Conta origem....: {_texto(conta_origem)}\n"
            f"    Conta destino...: {_texto(conta_destino)}\n"
            f"    Valor solicitado: {valor_exibido}\n"
            f"    Situação........: {'CONCLUÍDA' if sucesso else 'RECUSADA'}\n"
            f"    Mensagem........: {' '.join(_texto(mensagem).split())}\n"
            f"{campo_comentario}\n"
        )
        arquivo.write(bloco)

    return bloco
