param(
  [string]$ContainerName = "aris-postgres",
  [string]$DbUser = "aris",
  [string]$DbName = "aris",
  [Parameter(Mandatory = $true)][string]$BackupFile
)

$ErrorActionPreference = "Stop"

if (!(Test-Path $BackupFile)) {
  throw "Backup file not found: $BackupFile"
}

Write-Host "Restoring '$BackupFile' into container '$ContainerName' database '$DbName'..."
Get-Content $BackupFile | docker exec -i $ContainerName psql -U $DbUser -d $DbName

Write-Host "Restore completed."
Write-Host "Tip: run smoke test after restore:"
Write-Host "powershell -ExecutionPolicy Bypass -File .\scripts\smoke_test.ps1"