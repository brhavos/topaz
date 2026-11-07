# language: pt
Funcionalidade: Registro de Usuário no ParaBank
  Como um novo cliente
  Quero me cadastrar na plataforma do ParaBank
  Para que eu possa criar uma conta e acessar os serviços bancários

  Cenário: Registrar um novo usuário com sucesso
    Dado que acesso a página de cadastro do ParaBank
    Quando preencho o formulário de registro com dados válidos e exclusivos
    E clico no botão de registro
    Então o sistema deve criar a conta com sucesso e exibir uma mensagem de boas-vindas