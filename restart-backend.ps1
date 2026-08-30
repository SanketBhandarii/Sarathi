$ErrorActionPreference = "SilentlyContinue"

Get-NetTCPConnection -LocalPort 8000 -State Listen | ForEach-Object {
  Stop-Process -Id $_.OwningProcess -Force
}

Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" |
  Where-Object { $_.CommandLine -match "uvicorn app.main:app" } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force }

Start-Sleep -Seconds 2

Get-ChildItem -Path "backend" -Recurse -Directory -Filter "__pycache__" |
  Where-Object { $_.FullName -notmatch "\.venv" } |
  Remove-Item -Recurse -Force

Start-Process -FilePath "backend\.venv\Scripts\python.exe" `
  -ArgumentList "-m","uvicorn","app.main:app","--host","127.0.0.1","--port","8000","--reload" `
  -WorkingDirectory "backend" -WindowStyle Hidden

Write-Output "backend restarting on http://127.0.0.1:8000"
