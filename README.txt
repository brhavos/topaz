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
	                    dados de login, transferência, mensagens esperadas e pasta de evidências.
	- DADOS_CADASTRO..: PERFIL | primeiro_nome | sobrenome | endereco | cidade | estado
	                    | cep | telefone | ssn | senha | prefixo_usuario
	                    Um perfil por cenário (CADASTRO, LOGIN e TRANSFERENCIA).
	                    Deixando o campo ssn vazio, o teste gera um SSN exclusivo automaticamente.
	- INSTRUCOES......: lembrete de como editar a planilha.

    Observações:
	- Não renomeie as abas nem a coluna CHAVE: os testes localizam os valores por esses nomes.
	- Valores booleanos aceitam True/False (também Sim/Não).
	- mensagens_sucesso_transferencia aceita vários textos separados por ";".
	- A planilha é lida pelo arquivo "config/leitor.py".
	- Para recriar a planilha com os valores de fábrica: python config\gerar_planilha.py --forcar

