# Quick Start Guide

Get your AI Girlfriend application running in minutes!

## 🚀 Quick Setup (5 minutes)

### Step 1: Install Dependencies

**Install Python packages:**
```bash
pip install -r requirements.txt
```

**Install Node.js packages:**
```bash
cd frontend
npm install
cd ..
```

### Step 2: Configure API Key

Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_api_key_here
```

**Get your Gemini API key:**
1. Visit https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy and paste into `.env` file

### Step 3: Start the Application

**Option A: Use Start Script (Easiest)**

Windows PowerShell:
```powershell
.\start_app.ps1
```

Windows Command Prompt:
```cmd
start_app.bat
```

**Option B: Manual Start**

Terminal 1 (Backend):
```bash
python api_server.py
```

Terminal 2 (Frontend):
```bash
cd frontend
npm start
```

### Step 4: Open Browser

Navigate to: **http://localhost:3000**

## 🎮 First Conversation

1. Click **"Start New Session"**
2. Type: `"Hey, how are you?"`
3. Watch the character respond with dynamic expressions!

## 🔥 Try These Commands

### Sexual Script
Type: `"I'm feeling horny"` or `"let's fuck"`
- System will ask: Room or Public?
- Background changes based on your choice

### Casual Script  
Type: `"tell me a story"` or `"i'm bored"`
- AI will share an interesting story
- Character expressions change with emotions

### Safety Test
Type: `"I'm feeling depressed"` or `"help"`
- Script exits automatically
- Supportive AI response activated

## 💡 Tips

### Character Customization
- **Expressions**: Automatically change based on conversation
- **Outfits**: Progress during sexual scripts
- **Backgrounds**: Change with location (room/beach/park)

### Energy Indicators
Watch the badge colors:
- 🟢 **Green**: Normal conversation
- 🔥 **Sexual**: Intimate content active
- 💬 **Casual**: Story mode
- 🔴 **Red**: Crisis detected

### Best Practices
1. Start conversations casually
2. Wait for character responses to complete
3. Script mode needs 3+ messages before triggering
4. Use clear keywords for script activation

## ⚙️ Configuration

### Port Changes
Edit `api_server.py`:
```python
app.run(port=5000)  # Change port here
```

Edit `frontend/src/services/api.ts`:
```typescript
const API_BASE_URL = 'http://localhost:5000';  // Update URL
```

### Typing Speed
Edit `typing_simulator.py`:
```python
BASE_WPM = 200  # Adjust typing speed (words per minute)
```

### Script Triggers
Edit keywords in `enhanced_main.py` (line ~425):
```python
explicit_trigger_keywords = [
    "fuck", "sex", "cum",  # Add your keywords
]
```

## 🐛 Troubleshooting

### API Key Error
```
Error: GEMINI_API_KEY not set
```
**Fix**: Ensure `.env` file exists with correct API key

### Port Already in Use
```
Error: Address already in use
```
**Fix**: Kill process on port 5000 or change port number

### Character Not Loading
**Fix**: 
1. Check `/frontend/public/images/` folder exists
2. Verify sprite images are present
3. Clear browser cache (Ctrl+F5)

### No Response from AI
**Fix**:
1. Check backend console for errors
2. Verify Gemini API key is valid
3. Check internet connection

## 📱 Mobile Access

Access from phone on same network:
1. Find your computer's IP address
2. Open `http://YOUR_IP:3000` on phone
3. Character may not display on small screens (by design)

## 🎯 Next Steps

After setup, explore:
- Different conversation styles
- Script triggers and progression
- Energy detection patterns
- Character sprite variations

## 📖 Full Documentation

See `README.md` for complete technical documentation.

## ❓ Common Questions

**Q: Is my conversation data stored?**  
A: No, all data is session-based and cleared when you close.

**Q: Can I customize the character?**  
A: Yes, replace images in `/frontend/public/images/Incoatnito/`

**Q: How do I add more scenes?**  
A: Add `.jpg` files to `/frontend/public/images/scenes/` and update code

**Q: Can I change the AI personality?**  
A: Yes, edit prompts in `girlfriend_agent.py`

**Q: Why do I need an API key?**  
A: The application uses Google's Gemini AI for intelligent responses

---

**Need Help?** Check the console logs for detailed error messages!
