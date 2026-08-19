$ErrorActionPreference = 'Stop'
$sourceRoot = (Resolve-Path -LiteralPath $PSScriptRoot).Path
$supportRoot = (Resolve-Path -LiteralPath (Join-Path $sourceRoot '..')).Path
$stagedData = Join-Path $sourceRoot 'data'
$stagedResults = Join-Path $sourceRoot 'results'
$finalResults = Join-Path $supportRoot 'results'

try {
    if (Test-Path -LiteralPath $stagedData) { Remove-Item -LiteralPath $stagedData -Recurse -Force }
    if (Test-Path -LiteralPath $stagedResults) { Remove-Item -LiteralPath $stagedResults -Recurse -Force }
    Copy-Item -LiteralPath (Join-Path $supportRoot 'data') -Destination $stagedData -Recurse
    Copy-Item -LiteralPath $finalResults -Destination $stagedResults -Recurse

    Push-Location -LiteralPath $sourceRoot
    python scripts/run_pipeline.py
    if ($LASTEXITCODE -ne 0) { throw "run_pipeline.py failed with exit code $LASTEXITCODE" }
    python scripts/validate_modeling.py
    if ($LASTEXITCODE -ne 0) { throw "validate_modeling.py failed with exit code $LASTEXITCODE" }
    Pop-Location

    Copy-Item -LiteralPath (Join-Path $stagedResults '*') -Destination $finalResults -Recurse -Force
    Write-Host 'Reproducibility pipeline completed successfully.' -ForegroundColor Green
}
finally {
    if ((Get-Location).Path -eq $sourceRoot) { Pop-Location }
    if (Test-Path -LiteralPath $stagedData) { Remove-Item -LiteralPath $stagedData -Recurse -Force }
    if (Test-Path -LiteralPath $stagedResults) { Remove-Item -LiteralPath $stagedResults -Recurse -Force }
}
