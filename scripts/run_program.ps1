Set-Location -Path $PSScriptRoot
$projectRoot = Split-Path -Parent $PSScriptRoot

$python = "C:/Users/Reduan Ahmad/AppData/Local/Programs/Python/Python313/python.exe"

if (-not (Test-Path $python)) {
    Write-Error "Python executable not found at: $python"
    exit 1
}

& $python (Join-Path $projectRoot "bnl-core/interpreter.py") (Join-Path $projectRoot "bnl-core/program.bnl")
