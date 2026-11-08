#------------------------------------------
ARQUIVO.........: README.TXT
FINALIDADE......: FORNECER AS ORIENTAÇÕES PARA A EXECUÇÃO DO PROJETO E DOLEITURA DAS EVIDÊNCIAS
AUTOR...........: CARLOS HENRIQUE CICCOLANI
CRIAÇÃO.........: 06/11/26
ÚLTIMA ALTERAÇÃO: 07/11/26
#------------------------------------------

# PARÂMETROS:

	TECNOLOGIA APLICADA:
		PYTHON;
		BEHAVE.

	INTERAÇÃO COM O NAVEGADOR:
		SELENIUM.

# 1-) INSTRUÇÕES PARA O FUNCIONAMENTO

	Ponto de atenção: pré-requisitos para a execução dos testes:
		- python;
		- selenium;
		- behave.

	Criei 2 opções para a execução dos testes.
	- Se a máquina que for executar não possuir os requisitos mencionados, recomendo a opção 1.
	- Se a máquina que for executar possuir os requisitos mencionados, tanto faz, 1 ou 2.
	

    Passos a serem seguidos:

	Opção-1:
        a-) Baixe todo o conteúdo do repositório GIT numa pasta no seu computador;
	b-) Dê um duplo-clique no arquivo "executa.bat".

	Opção-2:
        b-) Abra o VsCode;
        c-) No VsCode, abra a pasta "topaz2";
        d-) No Vscode, abra uma sessão do terminal;
	e-) Criando ambiente virtual: python -m venv venv
	f-) Ativação do ambiente virtual: venv\Scripts\activate
	g-) Instalação das dependências (selenium e behave): pip install -r requirements.txt
        h-) Execução dos testeste o seguinte comando: "behave" (sem as aspas).

# 2-) EVIDÊNCIAS

    As imagens das evidências encontram-se na pasta "evidencias", do projeto.
    	* Toda vez que o teste automatizado é executado, elas são atualizadas (sobrepostas) automaticamente.

    Para dar fé nas imagens dos testes, criei um vídeo demonstrativo.
    Ele foi colocado na pasta "docs" e o seu nome é "evidencia_completa.mp4".

# 3-) PARÂMETROS DE TESTE (PLANILHA)\r

    Todos os parâmetros dos testes ficam na planilha "config\parametros.xlsx".
    Para alterar qualquer valor, basta editar a planilha e executar os testes normalmente.

    Abas da planilha:

	- PARAMETROS......: SECAO | CHAVE | VALOR | DESCRICAO
	                    URLs do sistema, opções do navegador, tempos de espera,
	                    dados de login, quantidades/valores de transferência,
	                    mensagens esperadas e pasta de evidências.
	- DADOS_CADASTRO..: PERFIL | tipo | primeiro_nome | sobrenome | endereco | cidade | estado
	                    | cep | telefone | ssn | senha | prefixo_usuario | erro_esperado | ativo
	                    Tipo PERFIL: um perfil por cenário (CADASTRO, LOGIN e TRANSFERENCIA).
	                    Tipo VALIDO: 10 usuários registrados pela massa de testes.
	                    Tipo INVALIDO: 5 usuários recusados; erro_esperado indica a mensagem exigida.
	                    Deixando o campo ssn vazio, o teste gera um SSN exclusivo automaticamente.
	                    Coluna ativo: S executa o registro e N o ignora sem apagar a linha (padrão S).
	- INSTRUCOES......: lembrete de como editar a planilha.

    Observações:
	- Não renomeie as abas nem a coluna CHAVE: os testes localizam os valores por esses nomes.
	- Valores booleanos aceitam True/False (também Sim/Não).
	- A massa de usuários usa somente os registros da aba DADOS_CADASTRO com
	  ativo = S; os marcados com N são ignorados, sem precisar apagar a linha.
	- mensagens_sucesso_transferencia aceita vários textos separados por ";".
	- quantidade_transferencias_validas e quantidade_transferencias_invalidas
	  definem quantas transferências executar (padrão 10 e 3). Quando a quantidade
	  supera a lista de valores, os valores são repetidos ciclicamente.
	- Cada transação executada é registrada em "docs/log_transacoes.txt", com
	  data/hora, usuário, contas, valor, situação e mensagem.
	- A planilha é lida pelo arquivo "config/leitor.py".
	- Para recriar a planilha com os valores de fábrica: python config\gerar_planilha.py --forcar

