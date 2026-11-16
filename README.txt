#------------------------------------------
# ARQUIVO.........: README.TXT
# FINALIDADE......: FORNECER AS ORIENTAÇÕES PARA A EXECUÇÃO DO PROJETO DE AUTOMAÇÃO DE TESTES
# AUTOR...........: CARLOS HENRIQUE CICCOLANI
# CRIAÇÃO.........: 06/11/26
# ÚLTIMA ALTERAÇÃO: 08/11/26
#------------------------------------------

# PARÂMETROS DO PROJETO:

	TECNOLOGIA APLICADA:
		Linguagem = PYTHON;
		Framework BDD: BEHAVE.

	INTERAÇÃO COM O NAVEGADOR:
		IDE de automação = SELENIUM.

# 1-) INSTRUÇÕES PARA O FUNCIONAMENTO

	Ponto de atenção: pré-requisitos para a execução dos testes:
		- python;
		- selenium;
		- behave.

	Caso a estação que for executar os testes não possua esses recursos, eles serão instalados
	automática e silenciosamente, conforme a opção de utilização escolhida.

	Opções de execução:
		Criei 2 opções para a execução dos testes.
			- Se a máquina que for executar o teste não possuir os pré-requisitos mencionados, recomendo a opção "1";
				Observação: os recursos mencionados acima serão instalados automaticamente.
			- Se a máquina que for executar possuir os requisitos mencionados, tanto faz, opção "1" ou "2";
			- Se for um usuário técnico da nossa área, sugiro a opção "2".
	
	Opção-1:
	a-) Acesse a seguinte url: https://github.com/brhavos/topaz.git;
	b-) Na tela que abrir, clique no botão verde, chamado "Code" e escolha a opção "download ZIP";
	c-) Descompacte o arquivo no local que desejar;
	d-) Vá no local onde o arquivo ZIP foi descompactado;
	e-) Localiza o arquivo "executa.bat", que está na raiz do projeto.
	f-) Dê um duplo-clique no arquivo "executa.bat" e aguarda o término do teste.
		Obs.: haverá instalações dos recursos necessários automaticamente.

	Opção-2:
	a-) Acesse a seguinte url: https://github.com/brhavos/topaz.git;
	b-) Na tela que abrir, clique no botão verde, chamado "Code" e escolha a opção "download ZIP";
	c-) Descompacte o arquivo no local que desejar;
	d-) Abra o VsCode;
	e-) No VsCode, abra a pasta onde foi feita a descompactação;
	f-) No Vscode, abra uma sessão do terminal;
	g-) Cria o ambiente virtual, digitando o seguinte comando: python -m venv venv;
	h-) Ativa o ambiente virtual, digitando o seguinte comando: venv\Scripts\activate;
	i-) Instala as dependências (selenium e behave), digitando o seguinte comando: pip install -r requirements.txt;
	j-) Executa o teste utilizando o seguinte comando: "behave" (sem as aspas).

	Espera pela verificação de humanidade do Cloudflare:
		Quando o Cloudflare exibe o desafio anti-bot, o teste para e escreve na hora,
		no console, uma mensagem avisando que está aguardando a validação.
		- Não há confirmação a dar: basta marcar "Confirme que é humano" na janela do
		  navegador controlada pelo Selenium;
		- O teste espera o prazo da chave "espera_verificacao_humana" (aba PARAMETROS,
		  secao TEMPOS; padrao 5s); assim que a página liberar, ele retoma sozinho de
		  onde parou;
		- Se a verificação não for concluída nesse prazo, o teste falha, com a mensagem
		  "A página não liberou dentro de 5s (desafio do Cloudflare)";
		- Se o envio for interrompido e o formulário voltar vazio, o teste avisa, espera
		  o mesmo prazo e preenche/envia o cadastro novamente, até 2 tentativas.
		- A tela do momento da pausa (URL, título, iframes e texto) fica registrada em
		  "docs/diagnostico_pausa.txt" e aparece no próprio console.
		Por isso, execute os testes com a janela do navegador visível (navegador_headless = N).

# 2-) EVIDÊNCIAS

    As imagens das evidências encontram-se na pasta "evidencias", do projeto.
    	* Toda vez que o teste automatizado é executado, novas imagens são geradas automaticamente.
    	* Como o nome inclui data e hora, execuções diferentes não se sobrescrevem: a pasta acumula
    	  o histórico. A limpeza é manual, se desejar.

    Padrão dos nomes das imagens:
		aaaammdd_hhmmss-situacao-nome_do_cenario-nome_do_step.png
		* situacao = "passed" (cenário aprovado) ou "no_passed" (reprovado ou não executado);
		* o step registrado é o que falhou ou, quando não há falha, o último step executado;
		* acentos e símbolos são removidos (ex.: "transferências" -> "transferencias").

    Para dar fé na eficácia da solução, criei um vídeo demonstrativo.
    Ele foi colocado na pasta "docs" e o seu nome é "evidencia_completa.mp4".

# 3-) PARÂMETROS DE TESTE (PLANILHA)

    Para garantir o reúso dos artefatos, criei uma parametrização.
    Todos os parâmetros dos testes ficam na planilha "config\parametros.xlsx".
    Para alterar qualquer valor, basta editar a planilha e executar os testes normalmente.
		* Se desejar alterar, faça com prudência e somente depois de ler as instruções, que estão
	contidas na aba "instrucoes" da própria planilha.
	SUGIRO FORTEMENTE QUE ANTES DE ALTERAR, EXECUTE PELO MENOS UMA VEZ O TESTE NA FORMA ORIGINAL.

    Abas da planilha parametros.xlsx:

	- PARAMETROS......: SECAO | CHAVE | VALOR | DESCRICAO
	                    URLs do sistema, opções do navegador, tempos de espera,
	                    dados de login, quantidades/valores de transferência,
	                    mensagens esperadas e pasta de evidências.
	- DADOS_CADASTRO..: PERFIL | tipo | primeiro_nome | sobrenome | endereco | cidade | estado
	                    | cep | telefone | ssn | senha | prefixo_usuario | erro_esperado | ativo
	                    Tipo PERFIL: um perfil por cenário (CADASTRO, LOGIN e TRANSFERENCIA).
	                    Tipo VALIDO: usuários registrados pela massa de testes.
	                    Tipo INVALIDO: usuários recusados; erro_esperado indica a mensagem exigida.
	                    Deixando o campo "SSN" vazio, o teste gera um "SSN" exclusivo automaticamente.
	                    Coluna ativo: "S" executa o registro e "N" o ignora sem apagar a linha.
	- INSTRUCOES......: ensina como editar a planilha.

    Observações:
	- Não renomeie as abas nem a coluna CHAVE: os testes localizam os valores por esses nomes.
	- Valores booleanos aceitam True/False (também Sim/Não).
	- A massa de usuários usa somente os registros da aba DADOS_CADASTRO com
	  ativo = S; os marcados com N são ignorados, sem precisar apagar a linha.
	- mensagens_sucesso_transferencia aceita vários textos separados por ";".
	- quantidade_transferencias_validas e quantidade_transferencias_invalidas
	  definem quantas transferências executar. Quando a quantidade
	  supera a lista de valores, os valores são repetidos ciclicamente.
	- Cada transação executada é registrada em "docs/log_transacoes.txt", com
	  data/hora, nome do cenário BDD, nome do step, usuário, contas, valor,
	  situação, mensagem e comentários.
	- A planilha é lida pelo arquivo "config/leitor.py".
	- Para recriar a planilha com os valores de fábrica: python config\gerar_planilha.py --forcar

# 4-) OBSERVABILIDADE

	a-) Visualização das métricas das execuções dos testes:
		Toda vez que um teste termina, um painel em HTML é exibido (com base na planilha 
		"log.xlsx", situada na pasta "docs", que é alimentada dinamicamente, durante a execução
		de cada teste);
		Por ser um arquivo HTML, o mesmo pode ser levado às reuniões syncs gerenciais ou diretoria.
	b-) Log de transações:
		Toda transação é registrada no arquivo "log_transacoes.txt", situado na pasta "docs".
		Esse log pode ter uma variedade de utilizações (por exemplo, análises/métricas c/ power-bi).
		Cada registro traz, além dos dados da operação, o nome do cenário BDD e o nome do
		step que originaram a transação. O campo "Comentários" vale "N/A" quando a
		transferência é concluída e, quando é recusada, descreve em linguagem amigável o
		problema ocorrido, as possíveis causas e as sugestões de solução.

# 5-) ANÁLISE DO PROJETO
	Toda a análise do projeto, escrita dos cenários BDD, mapeamento dos steps, tecnologias e 
	relatos de intercorrências relevantes estão no arquivo "analise.doc", situado na pasta "docs".

---(fim deste documento)---