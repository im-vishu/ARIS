param(
  [string]$BaseUrl = "http://127.0.0.1:8000"
)

$rid = [guid]::NewGuid().ToString()
Write-Host "Request ID: $rid"

$tokenBody = @{ username = "vishu"; role = "user" } | ConvertTo-Json
$tok = (iwr -UseBasicParsing -Method POST "$BaseUrl/auth/token" `
  -Headers @{ "x-request-id" = $rid } `
  -ContentType "application/json" -Body $tokenBody).Content | ConvertFrom-Json

$chatBody = @{ message = "log correlation test" } | ConvertTo-Json
iwr -UseBasicParsing -Method POST "$BaseUrl/chat" `
  -Headers @{ Authorization = "Bearer $($tok.access_token)"; "x-request-id" = $rid } `
  -ContentType "application/json" -Body $chatBody | Out-Null

Write-Host "`nAPI logs:"
docker compose logs --tail=80 aris-api

Write-Host "`nWorker logs:"
docker compose logs --tail=80 aris-worker