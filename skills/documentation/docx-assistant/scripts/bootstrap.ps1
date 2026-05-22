$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$skillRoot = Split-Path -Parent $scriptDir
$nodeModules = Join-Path $skillRoot 'node_modules'
$requirements = Join-Path $skillRoot 'requirements.txt'

if (Test-Path $nodeModules) {
    Write-Host 'Node dependencies already installed.'
} else {
    if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
        throw 'npm is required to install the JS builder dependencies.'
    }

    Push-Location $skillRoot
    try {
        npm ci
    }
    finally {
        Pop-Location
    }
}

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw 'python is required to install the DOCX assistant Python dependencies.'
}

python -m pip install -r $requirements
Write-Host 'DOCX assistant dependencies installed.'
