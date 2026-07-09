# Run as Administrator
# This script allows the Vite dev server (port 5173) through Windows Firewall

Write-Host "Adding firewall rule for dev server on port 5173..." -ForegroundColor Green

# Add firewall rule for inbound traffic on port 5173
netsh advfirewall firewall add rule `
  name="Vite Dev Server (5173)" `
  dir=in `
  action=allow `
  protocol=tcp `
  localport=5173 `
  remoteip=LocalSubnet `
  profile=private

# Also allow port 8080 for backend
netsh advfirewall firewall add rule `
  name="Backend API (8080)" `
  dir=in `
  action=allow `
  protocol=tcp `
  localport=8080 `
  remoteip=LocalSubnet `
  profile=private

Write-Host "✅ Firewall rules added successfully!" -ForegroundColor Green
Write-Host "Your phone should now be able to access https://10.31.1.2:5173" -ForegroundColor Cyan
