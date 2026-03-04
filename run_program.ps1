Set-Location -Path $PSScriptRoot

$python = "C:/Users/Reduan Ahmad/AppData/Local/Programs/Python/Python313/python.exe"

if (-not (Test-Path $python)) {
    Write-Error "Python executable not found at: $python"
    exit 1
}

& $python "interpreter.py" "program.bnl"
