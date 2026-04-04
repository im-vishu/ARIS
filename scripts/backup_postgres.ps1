param(
  [string]$ContainerName = "aris-postgres",
  [string]$DbUser = "aris",
  [string]$DbName = "aris",
  [string]$OutFile = ""
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($OutFile)) {
  $ts = Get-Date -Format "yyyyMMdd_HHmmss"
  $OutFile = ".\backup_aris_$ts.sql"
}

Write-Host "Creating backup from container '$ContainerName'..."
docker exec $ContainerName pg_dump -U $DbUser -d $DbName > $OutFile

if (!(Test-Path $OutFile)) {
  throw "Backup failed: file not created"
}

Write-Host "Backup completed: $OutFile"