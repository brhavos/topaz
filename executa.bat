@echo off
echo [1/3] Verificando e criando o ambiente virtual...
if not exist "venv" (
    python -m venv venv
)

echo [2/3] Instalando/atualizando dependencias do requirements.txt...
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt

echo [3/3] Executando os testes BDD com Behave...
behave

echo.
echo Processo finalizado! Pressione qualquer tecla para sair.
pause