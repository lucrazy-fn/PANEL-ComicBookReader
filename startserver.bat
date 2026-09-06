@echo off
set "PANEL_PYTHON=python"
if exist ".venv\Scripts\python.exe" set "PANEL_PYTHON=.venv\Scripts\python.exe"
if exist .env (
    "%PANEL_PYTHON%" -m uvicorn panel_backend.api.app:app --env-file .env
) else (
    "%PANEL_PYTHON%" -m uvicorn panel_backend.api.app:app
)
