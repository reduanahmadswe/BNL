param(
    [Parameter(Position = 0)]
    [string]$Name = "program"
)

Set-Location -Path $PSScriptRoot

$python = "C:/Users/Reduan Ahmad/AppData/Local/Programs/Python/Python313/python.exe"
if (-not (Test-Path $python)) {
    Write-Error "Python executable not found at: $python"
    exit 1
}

$fileName = $Name
if (-not $fileName.EndsWith(".bnl")) {
    $fileName = "$fileName.bnl"
}

if (-not (Test-Path $fileName)) {
    Write-Error "Program file not found: $fileName"
    exit 1
}

& $python "interpreter.py" $fileName
