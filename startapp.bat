@echo off
setlocal
cd /d "%~dp0"
set "PANEL_PYTHON="
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -c "import tkinter; tkinter.Tcl()" >nul 2>&1
    if not errorlevel 1 set "PANEL_PYTHON=.venv\Scripts\python.exe"
)
if not defined PANEL_PYTHON (
    where py >nul 2>&1 && set "PANEL_PYTHON=py"
)
if not defined PANEL_PYTHON (
    where python >nul 2>&1 && set "PANEL_PYTHON=python"
)
if not defined PANEL_PYTHON (
    echo Python com suporte ao Tkinter nao foi encontrado.
    echo Instale o Python oficial em https://python.org e tente novamente.
    pause
    exit /b 1
)
"%PANEL_PYTHON%" -m panel_app
if errorlevel 1 (
    echo.
    echo Nao foi possivel iniciar o PANEL.
    pause
)
