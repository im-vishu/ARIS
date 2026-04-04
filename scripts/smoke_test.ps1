$ErrorActionPreference = "Stop"

Write-Host "1) health"
$h = Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8000/health"
if ($h.status -ne "ok") { throw "Health failed" }

Write-Host "2) ready"
$r = Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8000/ready"
if ($r.status -ne "ready") { throw "Ready failed" }

Write-Host "3) auth token"
$tok = Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/auth/token" -ContentType "application/json" -Body '{"username":"smoke-user","role":"user"}'
if (-not $tok.access_token) { throw "Token missing" }

Write-Host "4) chat"
$chat = Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/chat" -Headers @{Authorization="Bearer $($tok.access_token)"} -ContentType "application/json" -Body '{"message":"smoke ping"}'
if (-not $chat.message_id) { throw "Chat failed" }

Write-Host "5) history"
$hist = Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8000/chat/history?limit=5" -Headers @{Authorization="Bearer $($tok.access_token)"}
if (-not $hist) { throw "History failed" }

Write-Host "SMOKE TEST PASSED"