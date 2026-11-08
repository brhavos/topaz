# language: pt
Funcionalidade: Massa de usuários para o cadastro
  Como analista de QA
  Quero validar os usuários cadastrados na aba DADOS_CADASTRO da planilha de parâmetros
  Para garantir que o sistema aceite dados válidos e recuse dados inválidos

  Cenário: Registrar os 10 usuários válidos da massa de dados
    Quando registro todos os usuários válidos da planilha de parâmetros
    Então todos os usuários válidos devem ser registrados com sucesso

  Cenário: Recusar os 5 usuários inválidos da massa de dados
    Quando tento registrar todos os usuários inválidos da planilha de parâmetros
    Então todos os usuários inválidos devem ser recusados com a mensagem esperada
