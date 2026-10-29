@echo off
cd /d "%~dp0"

py -3.14 -c "import streamlit, pymupdf" >nul 2>&1
if errorlevel 1 (
    echo Instalando las dependencias del proyecto...
    py -3.14 -m pip install -r requirements.txt
)

if errorlevel 1 (
    echo No se pudieron instalar las dependencias. Revisa que Python 3.14 este instalado.
    pause
    exit /b 1
)

py -3.14 -m streamlit run app.py
pause
