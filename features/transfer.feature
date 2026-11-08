# language: pt
Funcionalidade: Transferência de Fundos entre Contas
  Como um cliente autenticado no ParaBank
  Quero transferir valores monetários entre minhas contas
  Para movimentar meus saldos de forma rápida e segura

  Cenário: Realizar as transferências válidas configuradas na planilha
    Dado que estou logado no ParaBank e possuo saldo suficiente na conta de origem
    Quando realizo as transferências válidas configuradas na planilha
    Então todas as transferências válidas devem ser concluídas com sucesso
    E o log de transações deve conter os dados das transferências válidas

  Cenário: Recusar as transferências com valores inválidos
    Dado que estou logado no ParaBank e possuo saldo suficiente na conta de origem
    Quando realizo as transferências inválidas configuradas na planilha
    Então todas as transferências inválidas devem ser recusadas
    E o log de transações deve conter os dados das transferências inválidas
