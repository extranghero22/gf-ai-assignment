# AI Girlfriend Chat - PowerShell Startup Script

Write-Host "🌟 AI Girlfriend Chat - Starting Full Stack Application" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# Check if frontend directory exists
if (-not (Test-Path "frontend")) {
    Write-Host "❌ Frontend directory not found. Please run this from the project root." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if node_modules exists
if (-not (Test-Path "frontend\node_modules")) {
    Write-Host "📦 Installing frontend dependencies..." -ForegroundColor Yellow
    Set-Location "frontend"
    npm install
    Set-Location ".."
}

Write-Host "🚀 Starting Flask API server..." -ForegroundColor Green
Start-Process -FilePath "python" -ArgumentList "api_server.py" -WindowStyle Normal

# Wait a moment for backend to start
Start-Sleep -Seconds 3

Write-Host "📱 Starting React frontend..." -ForegroundColor Green
Set-Location "frontend"
Start-Process -FilePath "npm" -ArgumentList "start" -WindowStyle Normal
Set-Location ".."

Write-Host "✅ Backend started on http://localhost:5000" -ForegroundColor Green
Write-Host "✅ Frontend will start on http://localhost:3000" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Both servers are starting in separate windows." -ForegroundColor Yellow
Write-Host "Close this window when you're done." -ForegroundColor Yellow

Read-Host "Press Enter to exit"
