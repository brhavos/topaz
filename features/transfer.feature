# language: pt
Funcionalidade: Transferência de Fundos entre Contas
  Como um cliente autenticado no ParaBank
  Quero transferir valores monetários entre minhas contas
  Para movimentar meus saldos de forma rápida e segura

  Cenário: Realizar transferência de fundos com sucesso
    Dado que estou logado no ParaBank e possuo saldo suficiente na conta de origem
    Quando navego para a seção de transferência de fundos
    E informo um valor válido para transferência
    E seleciono a conta de origem e a conta de destino
    E confirmo a operação de transferência
    Então a transferência deve ser processada com sucesso
    E o recibo com os detalhes da transação deve ser exibido na tela