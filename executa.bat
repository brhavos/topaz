@echo off
setlocal enabledelayedexpansion
title Automacao de Testes - Inicializacao Inteligente

echo ========================================================
echo [1/4] Verificando se o Python esta instalado...
echo ========================================================

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [AVISO] Python nao encontrado nesta maquina. 
    echo Iniciando o download e instalacao automatica do Python...
    
    :: Define a URL oficial do instalador do Python 3.11 (ou versao compativel)
    set "PYTHON_INSTALLER=python-3.11.8-amd64.exe"
    set "PYTHON_URL=https://www.python.org/ftp/python/3.11.8/!PYTHON_INSTALLER!"
    
    echo Baixando o instalador do Python...
    powershell -Command "Invoke-WebRequest -Uri '!PYTHON_URL!' -OutFile '!PYTHON_INSTALLER!'"
    
    echo Instalando o Python (aguarde alguns instantes)...
    :: Instala silenciosamente, adiciona ao PATH para todos os usuarios e instala o pip
    start /wait "" "!PYTHON_INSTALLER!" /quiet InstallAllUsers=1 PrependPath=1 Include_pip=1
    
    echo Removendo arquivos temporarios de instalacao...
    del "!PYTHON_INSTALLER!"
    
    echo [SUCESSO] Python instalado com sucesso!
    echo IMPORTANTE: Caso o terminal nao reconheca o Python imediatamente, feche este prompt e abra novamente.
    echo.
) else (
    echo [OK] Python ja esta instalado na maquina.
)

echo.
echo ========================================================
echo [2/4] Verificando e criando o ambiente virtual (venv)...
echo ========================================================
if not exist "venv" (
    python -m venv venv
)

echo.
echo ========================================================
echo [3/4] Instalando/atualizando dependencias (requirements.txt)...
echo ========================================================
call venv\Scripts\activate
python -m pip install --upgrade pip
if exist "requirements.txt" (
    pip install -r requirements.txt
) else (
    pip install behave selenium
)

echo.
echo ========================================================
echo [4/4] Executando os testes BDD com Behave...
echo ========================================================
behave

echo.
echo ========================================================
echo Processo finalizado com sucesso!
echo ========================================================
pause