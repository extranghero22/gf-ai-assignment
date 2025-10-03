# AI Girlfriend Chat Application

A sophisticated AI-powered conversational girlfriend application featuring energy-aware responses, dynamic scripting, real-time emotion analysis, and an interactive React-based frontend with animated character sprites.

## 🌟 Features

### Core Capabilities
- **Energy-Aware Conversations**: Real-time analysis of emotional energy and user intent
- **Dynamic Script System**: Context-aware sexual and casual conversation scripts
- **Safety Monitoring**: Multi-layer safety system with crisis detection and intervention
- **Character Visualization**: Animated character sprite with dynamic expressions and outfits
- **Scene Management**: Dynamic background scenes that change based on conversation context
- **Distress Detection**: Automatic script interruption when user shows signs of distress
- **Multi-Message Streaming**: Natural typing simulation with grouped message support

### Advanced Features
- **LLM-Powered Analysis**: Uses Google Gemini for energy, safety, and response analysis
- **Emotion Recognition**: 10 distinct emotion states with intensity scoring
- **Energy Types**: Combative, Cooperative, Neutral, Playful, Intimate
- **Script Types**: 
  - Sexual scripts (Room intimacy & Public exhibitionism)
  - Casual conversation scripts
  - Dynamic scene changes (Room, Beach, Park)
- **Distress Protection**: Prevents inappropriate scripts when user is in distress
- **Emoji-Only Protection**: Prevents scripts from triggering on emoji-only messages

## 📁 Project Structure

```
Assignment/
├── Backend (Python)
│   ├── api_server.py                 # Flask API server with SSE streaming
│   ├── enhanced_main.py               # Main conversation orchestration system
│   ├── enhanced_script_manager.py     # Script management and scenario handling
│   ├── energy_analyzer.py             # LLM-powered energy analysis
│   ├── energy_types.py                # Energy/emotion type definitions
│   ├── safety_monitor.py              # Safety and crisis detection
│   ├── response_analyzer.py           # Response quality analysis
│   ├── girlfriend_agent.py            # AI girlfriend agent with LLM
│   ├── conversation_context.py        # Conversation state management
│   ├── typing_simulator.py            # Realistic typing simulation
│   ├── message_splitter.py            # Multi-message processing
│   ├── requirements.txt               # Python dependencies
│   └── girlfriend_dataset.jsonl       # Training/reference data
│
├── Frontend (React + TypeScript)
│   ├── src/
│   │   ├── App.tsx                    # Main application component
│   │   ├── types.ts                   # TypeScript type definitions
│   │   ├── components/
│   │   │   ├── CharacterSprite.tsx    # Animated character component
│   │   │   ├── CharacterSprite.css    # Character styling
│   │   │   ├── ChatInput.tsx          # User input component
│   │   │   ├── ChatMessage.tsx        # Message display component
│   │   │   ├── EnergyIndicator.tsx    # Energy status display
│   │   │   ├── MetricsModal.tsx       # Session metrics modal
│   │   │   ├── SessionControls.tsx    # Session management controls
│   │   │   └── CrisisToast.tsx        # Crisis alert notifications
│   │   └── services/
│   │       └── api.ts                 # API service layer
│   │
│   └── public/
│       └── images/
│           ├── Incoatnito/            # Character sprites and overlays
│           │   ├── 7 idle standing outfits/
│           │   │   ├── fullbody/      # Base character images
│           │   │   └── overlays/      # Expression overlays
│           │   └── ...
│           └── scenes/                # Background scenes
│               ├── room.jpg
│               ├── beach.jpg
│               └── walkway-garden-bangkok-thailand.jpg
│
└── Scripts
    ├── start_app.bat                  # Windows batch starter
    └── start_app.ps1                  # PowerShell starter
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+
- Google Gemini API Key

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd Assignment
```

2. **Set up Python environment**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

4. **Install frontend dependencies**
```bash
cd frontend
npm install
```

5. **Build frontend** (optional, for production)
```bash
npm run build
```

### Running the Application

#### Option 1: Using Start Scripts (Recommended)
**Windows (PowerShell):**
```powershell
.\start_app.ps1
```

**Windows (Command Prompt):**
```cmd
start_app.bat
```

#### Option 2: Manual Start
**Terminal 1 - Backend:**
```bash
python api_server.py
```

**Terminal 2 - Frontend (Development):**
```bash
cd frontend
npm start
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

## 🎯 Usage Guide

### Starting a Conversation
1. Open the application in your browser
2. Click "Start New Session" to begin
3. Type your message and press Enter or click Send
4. The AI girlfriend will respond with energy-aware messages

### Energy States
The system tracks and responds to different energy states:

| Status | Description | Visual Indicator |
|--------|-------------|------------------|
| 🟢 Green | Healthy conversation flow | Green badge |
| 🟡 Yellow | Caution - monitor conversation | Yellow badge |
| 🔴 Red | Crisis detected - support needed | Red badge |
| 🔥 Sexual | Intimate/sexual content | Fire emoji |
| 💬 Casual | Casual conversation mode | Chat emoji |
| 😏 Teasing | Playful teasing mode | Smirk emoji |

### Script Modes

#### Sexual Script
Triggered by explicit keywords or intimate energy. Two scenarios:
1. **Room Intimacy**: Private/bedroom setting (10 messages)
   - Background changes to room scene
   - Character outfit progresses: base → pullshirt → fully revealed
   
2. **Public Exhibitionism**: Outdoor/public setting (10 messages)
   - Background changes to park or beach (if "beach" mentioned)
   - Character outfit progresses in 3 stages:
     - **Stage 1 (Messages 1-3)**: Buttoned coat - fully covered
     - **Stage 2 (Messages 4-6)**: Open coat, topless underneath
     - **Stage 3 (Messages 7-10)**: Fully nude/exposed

#### Casual Script
Triggered by story-related keywords:
- Automatically starts when user shows interest in stories
- Can be paused/resumed by user
- Natural conversation flow maintained

### Character Sprites
The character dynamically changes based on:
- **Outfit**: 
  - Room script: casual → pullshirt → both revealed
  - Exhibitionism script: buttoned coat → open topless → fully nude
- **Expression**: Happy, smirk, wink, neutral, closed eyes, pout
- **Blush**: Appears during intimate/sexual content
- **Background**: Changes based on script location (room, beach, park)

### Safety Features

#### Distress Detection
The system automatically detects distress keywords and:
- Immediately exits any active script mode
- Switches to supportive AI responses
- Changes background back to default

Distress keywords include:
- Crisis: help, emergency, crisis, suicide, self-harm
- Grief: died, death, passed away, funeral, grief
- Medical: sick, hospital, ambulance, injury
- Mental health: panic attack, anxiety attack, breakdown
- General: stop, uncomfortable, upset, scared

#### Emoji-Only Protection
Scripts won't trigger from emoji-only messages like "🔥🔥🔥" or "😏💕"

## 🧠 Technical Architecture

### Backend Architecture

#### 1. Enhanced Main System (`enhanced_main.py`)
- **ConversationSession**: Manages individual user sessions
- **EnhancedMultiAgentConversation**: Main orchestration class
- **Energy Detection**: Real-time energy flag detection
- **Script Management**: Handles sexual and casual scripts
- **Distress Detection**: Monitors user input for crisis signals

#### 2. Energy Analysis (`energy_analyzer.py`)
- LLM-powered energy analysis using Google Gemini
- Returns: energy_level, energy_type, emotion, intensity_score
- Fallback to rule-based analysis if LLM fails

#### 3. Safety Monitor (`safety_monitor.py`)
- Multi-layer safety analysis
- Crisis detection and intervention
- Contextual safety scoring
- Returns: safety_score, issues, risk_factors, recommendation

#### 4. Script Manager (`enhanced_script_manager.py`)
- Manages multiple scenario scripts
- Handles grouped messages
- Scene-aware script delivery
- Progress tracking

#### 5. API Server (`api_server.py`)
- Flask-based REST API
- Server-Sent Events (SSE) for real-time streaming
- Endpoints:
  - `POST /api/start_session` - Start new conversation
  - `POST /api/send_message` - Send message (SSE stream response)
  - `GET /api/session_info` - Get session information

### Frontend Architecture

#### Component Hierarchy
```
App.tsx
├── SessionControls
├── CharacterSprite
│   └── Dynamic background & expressions
├── EnergyIndicator
├── ChatMessage (multiple)
├── ChatInput
├── MetricsModal
└── CrisisToast
```

#### State Management
- React useState hooks for local state
- Real-time updates via SSE connection
- Energy flags propagated to relevant components

#### Styling
- Custom CSS with modern design
- Glassmorphism effects
- Smooth transitions and animations
- Responsive design (mobile-friendly)

## 🔧 Configuration

### Energy Thresholds
Defined in `enhanced_main.py`:
```python
ENERGY_THRESHOLDS = {
    "crisis_intensity": 0.85,
    "sexual_intensity": 0.75,
    "intimate_level": EnergyLevel.INTENSE
}
```

### Script Triggers
Sexual script keywords in `enhanced_main.py` line 425-430:
```python
explicit_trigger_keywords = [
    "fuck", "sex", "cum", "make love", 
    "touch me", "kiss me", ...
]
```

### Safety Settings
Configure in `safety_monitor.py`:
- Safety score thresholds
- Crisis keyword lists
- Intervention protocols

## 📊 Data Flow

### Message Flow
```
User Input → API Server → Enhanced Main System
    ↓
Energy Analysis (Gemini LLM)
    ↓
Safety Analysis (Gemini LLM)
    ↓
Decision Making (Script trigger / Continue / Stop)
    ↓
AI Response Generation (Gemini LLM)
    ↓
Typing Simulation & Message Streaming (SSE)
    ↓
Frontend Display (with energy indicators & character updates)
```

### Script Flow
```
Trigger Detection → Location Choice (for sexual)
    ↓
Script Initialization
    ↓
Message-by-Message Delivery
    ↓
User Response → Distress Check
    ↓
Continue or Exit Script
    ↓
Script Completion → Natural Follow-up
```

## 🛡️ Safety & Privacy

- **No Data Storage**: Conversations are not persisted to disk
- **Session-Based**: All data cleared when session ends
- **Crisis Detection**: Automatic intervention for distress signals
- **Content Filters**: Multi-layer safety analysis
- **API Security**: Environment variables for API keys

## 🐛 Troubleshooting

### Common Issues

**1. "GEMINI_API_KEY not set"**
- Ensure `.env` file exists in root directory
- Check that `GEMINI_API_KEY` is set correctly

**2. Frontend not connecting to backend**
- Verify backend is running on port 5000
- Check CORS settings in `api_server.py`
- Ensure no firewall blocking

**3. Character sprite not loading**
- Check that images exist in `frontend/public/images/`
- Verify image paths in `CharacterSprite.tsx`
- Clear browser cache

**4. Script not triggering**
- Check console logs for energy detection
- Verify message count (scripts require 3+ messages)
- Ensure keywords are present in user input

**5. Typing animation stuck**
- Check browser console for SSE connection errors
- Verify Flask server is running
- Check network tab for event stream

## 📝 Development Notes

### Adding New Emotions
1. Add to `EmotionState` enum in `energy_types.py`
2. Update emotion mapping in `energy_analyzer.py`
3. Add expression image to `public/images/Incoatnito/.../expressions/`
4. Update `getExpressionPaths()` in `CharacterSprite.tsx`

### Adjusting Script Outfit Progression
Edit `CharacterSprite.tsx` (lines 65-88):
```typescript
// For exhibitionism: 3 stages
if (sexualMessageCount >= 7) {
  setCurrentOutfit('overcoat_nude');        // Stage 3
} else if (sexualMessageCount >= 4) {
  setCurrentOutfit('overcoat_open_topless'); // Stage 2
} else {
  setCurrentOutfit('overcoat_buttoned');    // Stage 1
}
```

### Adding New Scenes
1. Add image to `frontend/public/images/scenes/`
2. Update scene type in `types.ts`
3. Add case to `getBackgroundScene()` in `CharacterSprite.tsx`
4. Set scene in backend energy flags

### Creating New Scripts
1. Define scenario in `enhanced_script_manager.py`
2. Add trigger keywords in `_detect_energy_flags()`
3. Create start method in `enhanced_main.py`
4. Add outfit logic in `CharacterSprite.tsx` if needed

## 🤝 Contributing

When contributing, please:
1. Follow existing code style
2. Add comments for complex logic
3. Test thoroughly before submitting
4. Update documentation for new features

## 📄 License

This project is for educational/personal use.

## 🙏 Acknowledgments

- Google Gemini AI for LLM capabilities
- React community for frontend tools
- Flask community for backend framework

---

**Version**: 1.0.0  
**Last Updated**: October 2025  
**Status**: Production Ready
