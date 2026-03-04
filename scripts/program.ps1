param(
    [Parameter(Position = 0)]
    [string]$Name = "program"
)

Set-Location -Path $PSScriptRoot
$projectRoot = Split-Path -Parent $PSScriptRoot

$python = "C:/Users/Reduan Ahmad/AppData/Local/Programs/Python/Python313/python.exe"
if (-not (Test-Path $python)) {
    Write-Error "Python executable not found at: $python"
    exit 1
}

$fileName = $Name
if (-not $fileName.EndsWith(".bnl")) {
    $fileName = "$fileName.bnl"
}

if (Test-Path (Join-Path $projectRoot $fileName)) {
    $programPath = Join-Path $projectRoot $fileName
} elseif (Test-Path (Join-Path $projectRoot (Join-Path "bnl-core" $fileName))) {
    $programPath = Join-Path $projectRoot (Join-Path "bnl-core" $fileName)
} else {
    Write-Error "Program file not found: $fileName"
    exit 1
}

& $python (Join-Path $projectRoot "bnl-core/interpreter.py") $programPath
