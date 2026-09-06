$ErrorActionPreference = "Stop"
$Python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Python)) { throw "Ambiente .venv não encontrado." }
& $Python -m pip install pyinstaller
& $Python -m PyInstaller --noconfirm --clean --windowed --name PANEL --icon panel.ico --add-data "Icons;Icons" --add-data "panellogo.png;." --add-data "panel.ico;." --collect-all pymupdf -m panel_app
if (Get-Command iscc.exe -ErrorAction SilentlyContinue) { iscc.exe "installer\Panel.iss" }
else { Write-Host "Executável criado em dist\PANEL. Instale o Inno Setup para gerar Panel-Setup.exe." }
