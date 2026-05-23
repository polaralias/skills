$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$skillRoot = Split-Path -Parent $scriptDir
$requirements = Join-Path $skillRoot 'requirements.txt'

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw 'python is required to install the tasklist-gantt-creator dependencies.'
}

python -m pip install -r $requirements
Write-Host 'tasklist-gantt-creator dependencies installed.'
