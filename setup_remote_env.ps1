# PowerShell script to set up remote management environment variables
Write-Host "Setting up remote management environment variables..." -ForegroundColor Green

# Set your Railway portal URL
$env:PORTAL_URL = "https://narrow-clocks-staging.up.railway.app"

# Set your admin API key (change this to something secure!)
$env:ADMIN_API_KEY = "your_secure_admin_key_change_me_123"

Write-Host "✅ Environment variables set!" -ForegroundColor Green
Write-Host ""
Write-Host "PORTAL_URL: $env:PORTAL_URL" -ForegroundColor Cyan
Write-Host "ADMIN_API_KEY: $env:ADMIN_API_KEY" -ForegroundColor Cyan
Write-Host ""
Write-Host "Now you can run:" -ForegroundColor Yellow
Write-Host "  python remote_data_manager.py test" -ForegroundColor White
Write-Host "  python remote_data_manager.py list" -ForegroundColor White
Write-Host "  python remote_data_manager.py upload database.db customer@email.com 'Project'" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to continue"
