# HISTÓRICO DAS ATUALIZAÇÕES DO PROJETO

## 16/11/2026

### Pedido-1:
Quero que quando gerar as evidências os nomes das imagens tenham o seguinte padrão:
#### Estrutura da nomenclatura para os nomes das imagens dos cenários que passarem com sucesso:
aaaammdd_hhmmss-passed-nome_do_cenario-nome_do_step
#### Estrutura da nomenclatura para os nomes das imagens dos cenários que passarem com sucesso:
aaaammdd_hhmmss-no_passed-nome_do_cenario-nome_do_step
###-------------------------------------------------------------------
### Pedido-2: Implementações no arquivo "log_transacoes"
Mantendo a estrutura atual do arquivo "log_transacoes", quero incrementar as seguintes informações:
#### Nome do cenário BDD
Adicionar a informação "Nome do cenário BDD".
#### Step
Adicionar a informação "Nome do step".
#### Comentários
Adicionar a informação "Comentários".
Para transações bem sucedidas, informar "N/A".
Para todas as transações inválidas, adicionar uma mensagem em linguagem amigável a descrição do problema ocorrido, as possíveis causas e as sugestões de opções de solução.
###-------------------------------------------------------------------
### Pedido-3: Implementação de verificação de humanidade
Durante os testes, se o Parabank invocar o Claudflare, solicitando a verificação de humanidade, a automação deve parar, solicitar que o humano faça a verificação.
Depois da verificação humana, a automação retoma o controle dos testes e dá prosseguimento normalmente.
A automação só deve prosseguir depois que o humano fizer a verificação.
###-------------------------------------------------------------------
