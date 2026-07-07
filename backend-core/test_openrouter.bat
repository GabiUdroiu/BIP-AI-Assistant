@echo off
cd /d "%~dp0"

for /f "tokens=1,* delims==" %%A in ('findstr /r "ROUTER_API_KEY" .env') do set OPENROUTER_API_KEY=%%B

curl -s https://openrouter.ai/api/v1/chat/completions ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer %OPENROUTER_API_KEY%" ^
  -d "{\"model\": \"openai/gpt-oss-20b:free\", \"messages\": [{\"role\": \"user\", \"content\": \"hello, what model are you and what date is today?\"}]}" > response.json

powershell -NoProfile -Command "try { (Get-Content response.json -Raw | ConvertFrom-Json).choices[0].message.content } catch { Write-Host 'Could not parse response:'; Get-Content response.json }"

del response.json

echo.
pause
