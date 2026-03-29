$ErrorActionPreference = "Stop"

$workspace = Split-Path -Parent $PSScriptRoot
$srcPath = Join-Path $workspace "src"
$sitePackages = Join-Path $workspace ".venv\\Lib\\site-packages"
$env:PYTHONPATH = "$srcPath;$sitePackages"

& "C:\Users\DABC\AppData\Roaming\uv\python\cpython-3.11.14-windows-x86_64-none\python.exe" `
    -m uvicorn procurebrain.main:app --host 127.0.0.1 --port 8001
