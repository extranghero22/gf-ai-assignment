@echo off
echo 🌟 AI Girlfriend Chat - Starting Full Stack Application
echo ============================================================

REM Check if frontend directory exists
if not exist "frontend" (
    echo ❌ Frontend directory not found. Please run this from the project root.
    pause
    exit /b 1
)

REM Check if node_modules exists
if not exist "frontend\node_modules" (
    echo 📦 Installing frontend dependencies...
    cd frontend
    npm install
    cd ..
)

echo 🚀 Starting Flask API server...
start "Backend" cmd /k "python api_server.py"

REM Wait a moment for backend to start
timeout /t 3 /nobreak > nul

echo 📱 Starting React frontend...
cd frontend
start "Frontend" cmd /k "npm start"
cd ..

echo ✅ Backend started on http://localhost:5000
echo ✅ Frontend will start on http://localhost:3000
echo ============================================================
echo Press any key to exit...
pause > nul
