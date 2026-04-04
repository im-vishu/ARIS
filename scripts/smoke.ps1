param(
  [string]$BaseUrl = "http://127.0.0.1:8000",
  [string]$Username = "vishu"
)

Write-Host "== Health =="
curl.exe -s -i "$BaseUrl/health"

Write-Host "`n== Ready =="
curl.exe -s -i "$BaseUrl/ready"

Write-Host "`n== Token =="
$body = @{ username = $Username; role = "user" } | ConvertTo-Json
$tok = (iwr -UseBasicParsing -Method POST "$BaseUrl/auth/token" -ContentType "application/json" -Body $body).Content | ConvertFrom-Json
$tok | ConvertTo-Json -Depth 5

Write-Host "`n== Chat =="
$chat = @{ message = "hello from smoke" } | ConvertTo-Json
iwr -UseBasicParsing -Method POST "$BaseUrl/chat" -Headers @{ Authorization = "Bearer $($tok.access_token)" } -ContentType "application/json" -Body $chat