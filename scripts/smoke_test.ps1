$ErrorActionPreference = "Stop"

$base = "http://127.0.0.1:8000"

Write-Host "1) v1 health"
$h = Invoke-RestMethod -Method Get -Uri "$base/v1/health"
if ($h.data.status -ne "ok") { throw "Health failed" }

Write-Host "2) v1 ready (optional in local)"
try {
  $r = Invoke-RestMethod -Method Get -Uri "$base/v1/ready"
  if ($r.data.status -ne "ready") { throw "Ready payload not ready" }
  Write-Host "Ready passed"
}
catch {
  Write-Host "Ready not available locally (continuing): $($_.Exception.Message)"
}

Write-Host "3) v1 auth token"
$tokRes = Invoke-RestMethod -Method Post -Uri "$base/v1/auth/token" -ContentType "application/json" -Body '{"username":"smoke-user","role":"user"}'
$access = $tokRes.data.access_token
if (-not $access) { throw "Token missing" }

Write-Host "4) v1 chat"
$chat = Invoke-RestMethod -Method Post -Uri "$base/v1/chat" -Headers @{Authorization="Bearer $access"} -ContentType "application/json" -Body '{"message":"smoke ping"}'
if (-not $chat.data.message_id) { throw "Chat failed" }

Write-Host "5) v1 history"
$hist = Invoke-RestMethod -Method Get -Uri "$base/v1/chat/history?limit=5" -Headers @{Authorization="Bearer $access"}
if (-not $hist.data) { throw "History failed" }

Write-Host "SMOKE TEST PASSED"