# 🚀 AI Girlfriend Chat - Startup Guide

## Quick Start Options

### Option 1: Windows Batch File (Recommended)
```bash
start_app.bat
```

### Option 2: PowerShell Script
```powershell
.\start_app.ps1
```

### Option 3: Manual Startup

**Terminal 1 - Backend:**
```bash
python api_server.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

### Option 4: Python Startup Script
```bash
python start_react_app.py
```

## Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000

## Prerequisites

- ✅ Node.js (v14+)
- ✅ Python 3.8+
- ✅ All Python dependencies installed
- ✅ React dependencies installed (`npm install` in frontend folder)

## Troubleshooting

### If npm is not found:
- Make sure Node.js is installed and in your PATH
- Try running `npm --version` to verify installation

### If Python modules are missing:
```bash
pip install flask flask-cors google-generativeai python-dotenv openai
```

### If frontend dependencies are missing:
```bash
cd frontend
npm install
```

## Features

- 🎨 Modern React UI with TypeScript
- 💬 Real-time chat interface
- 📊 Energy monitoring and visualization
- 📈 Session metrics and analytics
- 🎯 Session management (start/stop)
- 📱 Mobile responsive design

## Development

- Frontend hot reloads on changes
- Backend restarts on Python file changes
- CORS enabled for development
- Error handling and user feedback

Enjoy your AI girlfriend chat experience! 💕
