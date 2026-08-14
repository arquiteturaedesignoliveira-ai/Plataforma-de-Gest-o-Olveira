@echo off
REM Abre o Macro Recorder. Na primeira execucao, cria o ambiente virtual
REM e instala as dependencias automaticamente. Basta dar duplo clique.

cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo.
    echo [ERRO] Python nao encontrado.
    echo Instale o Python 3.10 ou superior em https://www.python.org/downloads/
    echo IMPORTANTE: marque a opcao "Add Python to PATH" durante a instalacao.
    echo.
    pause
    exit /b 1
)

if not exist venv (
    echo Preparando o ambiente pela primeira vez, aguarde...
    python -m venv venv
    call venv\Scripts\activate.bat
    python -m pip install --upgrade pip
    pip install pynput
) else (
    call venv\Scripts\activate.bat
)

python src\main.py
if errorlevel 1 pause
