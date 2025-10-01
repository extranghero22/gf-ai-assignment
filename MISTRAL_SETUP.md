# Mistral AI Setup Guide

## 1. Get Your Mistral API Key

1. Go to [https://console.mistral.ai/](https://console.mistral.ai/)
2. Create an account or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the API key

## 2. Set Environment Variable

### Windows (PowerShell):
```powershell
$env:MISTRAL_API_KEY = "your-mistral-api-key-here"
```

### Windows (Command Prompt):
```cmd
set MISTRAL_API_KEY=your-mistral-api-key-here
```

### Linux/Mac:
```bash
export MISTRAL_API_KEY=your-mistral-api-key-here
```

## 3. Install Dependencies

The system has been updated to use Mistral AI instead of Gemini. The required package has been installed:

```bash
pip install mistralai
```

## 4. Changes Made

- **girlfriend_agent.py**: Updated to use Mistral client instead of Gemini
- **energy_analyzer.py**: Updated to use Mistral for energy analysis  
- **requirements.txt**: Added mistralai package
- **Fixed imports**: Updated to use correct Mistral API syntax (`from mistralai import Mistral`)

## 5. Benefits

- **Less Content Blocking**: Mistral is more permissive with adult content
- **Better Instruction Following**: More consistent responses
- **Improved Performance**: Better at following personality instructions

## 6. Models Available & Automatic Fallback

The system now includes automatic fallback when models hit capacity limits:

**Main Agent Models (in priority order):**
1. **mistral-large-latest**: Most capable (primary)
2. **mistral-medium-latest**: Good balance
3. **mistral-small-latest**: Fast and efficient  
4. **open-mistral-7b**: Free tier fallback

**Energy Analyzer Models (in priority order):**
1. **open-mistral-7b**: Free and fast (primary)
2. **mistral-small-latest**: Backup
3. **mistral-medium-latest**: Final fallback

## 7. Capacity Issue Solution

If you see "Service tier capacity exceeded" errors:
- ✅ **Automatic**: System will try next available model
- ✅ **Smart Switching**: Remembers which model works
- ✅ **Graceful Fallback**: Uses context-aware responses if all models fail

The system will automatically handle capacity issues and find working models!
