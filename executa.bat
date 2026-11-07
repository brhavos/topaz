@echo off
setlocal enabledelayedexpansion
title Automacao de Testes

echo ========================================================
echo [1/4] Verificando se o Python esta instalado...
echo ========================================================

set "PYTHON_EXE="

:: 1. Verifica primeiro nos caminhos oficiais de instalacao (evita o atalho da Windows Store)
if exist "C:\Program Files\Python311\python.exe" (
    set "PYTHON_EXE=C:\Program Files\Python311\python.exe"
) else if exist "%LocalAppData%\Programs\Python\Python311\python.exe" (
    set "PYTHON_EXE=%LocalAppData%\Programs\Python\Python311\python.exe"
) else (
    :: 2. Se nao esta nos caminhos padroes, procura no PATH ignorando a pasta WindowsApps
    for /f "tokens=*" %%i in ('where python 2^>nul') do (
        echo %%i | findstr /i "WindowsApps" >nul
        if errorlevel 1 (
            if not defined PYTHON_EXE set "PYTHON_EXE=%%i"
        )
    )
)

:: 3. Se nao encontrou um Python real, baixa e instala a versao oficial
if not defined PYTHON_EXE (
    echo [AVISO] Python real nao encontrado. Baixando e instalando...
    
    powershell -NoProfile -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe' -OutFile 'python_installer.exe'"
    if errorlevel 1 (
        echo [ERRO] Falha no download. Verifique sua conexao.
        pause
        exit /b 1
    )

    echo Instalando o Python...
    powershell -NoProfile -Command "Start-Process -FilePath 'python_installer.exe' -ArgumentList '/quiet', 'InstallAllUsers=1', 'PrependPath=1', 'Include_pip=1' -Wait -NoNewWindow"
    del "python_installer.exe" >nul 2>&1

    if exist "C:\Program Files\Python311\python.exe" (
        set "PYTHON_EXE=C:\Program Files\Python311\python.exe"
    ) else if exist "%LocalAppData%\Programs\Python\Python311\python.exe" (
        set "PYTHON_EXE=%LocalAppData%\Programs\Python\Python311\python.exe"
    )
)

if not defined PYTHON_EXE (
    echo [ERRO] A instalacao falhou ou o Python nao foi localizado.
    pause
    exit /b 1
)

echo [OK] Python localizado em: "%PYTHON_EXE%"

echo.
echo ========================================================
echo [2/4] Criando ambiente virtual (venv)...
echo ========================================================
if not exist "venv" (
    "%PYTHON_EXE%" -m venv venv
    if errorlevel 1 (
        echo [ERRO] Falha ao criar o ambiente virtual.
        pause
        exit /b 1
    )
)

echo.
echo ========================================================
echo [3/4] Instalando dependencias...
echo ========================================================
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
if exist "requirements.txt" (
    pip install -r requirements.txt
) else (
    pip install behave selenium
)

echo.
echo ========================================================
echo [4/4] Executando os testes...
echo ========================================================
behave

echo.
echo Processo finalizado.
pause