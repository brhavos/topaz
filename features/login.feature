# language: pt
Funcionalidade: Autenticação de Usuário (Login)
  Como um cliente cadastrado
  Quero realizar o login no ParaBank utilizando minhas credenciais
  Para acessar o painel da minha conta com segurança

  Cenário: Realizar login com credenciais válidas (Caminho Feliz)
    Dado que possuo um usuário ativo cadastrado no sistema
    E estou na página inicial de login do ParaBank
    Quando informo meu usuário e senha válidos
    E clico no botão de login
    Então devo ser autenticado com sucesso e redirecionado para a visão geral das contas

  Esquema do Cenário: Tentativas de login inválidas ou incorretas
    Dado que estou na página inicial de login do ParaBank
    Quando informo o usuário "<usuario>" e a senha "<senha>"
    E clico no botão de login
    Então o sistema deve recusar o acesso e exibir a mensagem de erro esperada

    Exemplos:
      | usuario           | senha        |
      | usuario_inexistente | senha123     |
      |                   |              |
      | standard_user     | senha_errada |