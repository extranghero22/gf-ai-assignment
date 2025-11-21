# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Application

### Backend (Python Flask API)
```bash
python api_server.py
```
Runs on http://localhost:5000

### Frontend (React TypeScript)
```bash
cd frontend
npm start      # Development server on http://localhost:3000
npm run build  # Production build
npm test       # Run tests
```

### Full Stack Startup
Use the provided start scripts:
- **PowerShell**: `.\start_app.ps1`
- **Command Prompt**: `start_app.bat`

### Environment Setup
Create `.env` file in root with:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

The system uses OpenAI (GPT models).

### Python Dependencies
```bash
pip install -r requirements.txt
```

### Testing
Backend tests are in `/tests` directory:
```bash
python tests/test_error_logging.py
python tests/test_conversation_scenario.py
# etc.
```

## Core Architecture

This is an **energy-aware AI girlfriend chat application** with a sophisticated multi-LLM agent system. The architecture consists of 6 independent LLM-powered components that analyze different aspects of conversation in real-time.

### The 6 LLM Components

All components use OpenAI with fallback mechanisms:

1. **Energy Analyzer** ([energy_analyzer.py](energy_analyzer.py))
   - Analyzes emotional energy in user messages
   - Uses: gpt-4o-mini (primary), gpt-4o, gpt-3.5-turbo (fallbacks)
   - Returns: energy_level, energy_type, emotion, intensity_score
   - Energy Types: COMBATIVE, COOPERATIVE, NEUTRAL, PLAYFUL, INTIMATE
   - Energy Levels: NONE, LOW, MEDIUM, HIGH, INTENSE
   - 10 Emotion States: HAPPY, SAD, ANGRY, ANXIOUS, JEALOUS, LOVING, EXCITED, BORED, CONFUSED, GRATEFUL

2. **Safety Monitor** ([safety_monitor.py](safety_monitor.py))
   - Multi-layer safety analysis and crisis detection
   - Uses: gpt-4o-mini (primary), gpt-4o, gpt-3.5-turbo (fallbacks)
   - Returns: safety_score (0.0-1.0), issues, risk_factors, recommendation
   - Recommendations: SAFE, CAUTION, WARNING, STOP
   - Distinguishes between romantic/sexual content (expected) vs actual safety concerns
   - Crisis keywords trigger immediate intervention

3. **Response Analyzer** ([response_analyzer.py](response_analyzer.py))
   - Analyzes conversation flow and continuation decisions
   - Uses: gpt-4o-mini (primary), gpt-4o, gpt-3.5-turbo (fallbacks)
   - Returns: should_continue, engagement_level, confidence_score
   - Only stops for serious issues (abuse, incoherence, major safety)

4. **Message Routing Agent** ([message_routing_agent.py](message_routing_agent.py))
   - Analyzes messages to determine response strategy
   - Uses: gpt-4o-mini (primary), gpt-4o, gpt-3.5-turbo (fallbacks)
   - Returns: routing path (A-F), complexity, wrapping instructions
   - **6 Routing Paths**:
     - PATH A (RESPOND_NORMALLY): Straightforward, on-topic responses
     - PATH B (RESPOND_WITH_CONFUSION): Act confused about complex topics ("what? lol babe idk")
     - PATH C (DEFLECT_REDIRECT): Deflect uncomfortable topics, redirect conversation
     - PATH D (MINIMAL_RESPONSE): Brief responses to create tension ("nice 💪")
     - PATH E (IGNORE_SELF_FOCUS): Redirect to self in dramatic way ("omg i just spilled coffee 😭")
     - PATH F (EMOTIONAL_REACTION): Strong emotional responses ("omg you're gonna make me cry 🥺")
   - Hardcoded complexity detection: SIMPLE, MODERATE, DEEP, WEIRD
   - Emotion intensity from energy signature: low, medium, high

5. **Girlfriend Agent** ([girlfriend_agent.py](girlfriend_agent.py))
   - Main conversational AI using OpenAI
   - Uses: gpt-4o-mini (primary), gpt-4o, gpt-3.5-turbo (fallbacks)
   - Energy-aware response generation
   - Context-aware personality and tone
   - Handles both scripted and dynamic conversations
   - Integrates routing agent to wrap responses based on chosen path

6. **Script Manager** ([enhanced_script_manager.py](enhanced_script_manager.py))
   - Manages pre-written scenario scripts (sexual and casual)
   - Scene-aware delivery with outfit/location changes
   - Progress tracking and distress interruption

### Main Orchestration System

**[enhanced_main.py](enhanced_main.py)** - The central orchestrator that:
- Manages conversation sessions (ConversationSession class)
- Coordinates all 6 LLM components
- Detects energy flags and triggers scripts
- Handles distress detection and script interruption
- Manages sexual and casual script state

Key classes:
- `EnhancedMultiAgentConversation`: Main conversation controller
- `ConversationSession`: Session state with script tracking
- `ConversationState`: ACTIVE, PAUSED, STOPPED, ALERT, COMPLETED

### API Server Architecture

**[api_server.py](api_server.py)** - Flask server with Server-Sent Events (SSE):

Endpoints:
- `POST /api/start_session` - Initialize new conversation
- `POST /api/send_message` - Send message, returns SSE stream
- `GET /api/session_info` - Get current session data

**Critical SSE Streaming Implementation**:
- Messages are split using `MessageSplitter` (handles grouped messages)
- Typed out character-by-character with `MultiMessageGenerator`
- Each character sent as SSE event: `data: {"type": "chunk", "content": "..."}`
- Energy flags sent in real-time: `data: {"type": "energy_flags", ...}`
- Complete message marked: `data: {"type": "message_complete"}`

### Script System

Two script types managed by session state:

**Sexual Scripts** ([enhanced_main.py:425-430](enhanced_main.py#L425-L430)):
- Triggered by explicit keywords OR energy detection
- Session flags: `sexual_script_active`, `sexual_script_index`, `sexual_script_type`
- Two scenarios:
  - **Room Intimacy**: 10 messages, outfit progression (casual → pullshirt → revealed)
  - **Exhibitionism**: 10 messages, location-based (park/beach), outfit stages (buttoned → topless → nude)
- Location choice triggered by `awaiting_location_choice` flag
- **Prevention**: Won't re-trigger if `sexual_script_completed` is True

**Casual Scripts**:
- Triggered by story keywords ("tell me a story", etc.)
- Session flags: `casual_script_active`, `casual_script_index`, `casual_script_paused`
- Shopping scenario with grouped messages
- Can be paused/resumed based on user interest

**Distress Protection**:
- Crisis keywords immediately exit scripts
- Keywords in [enhanced_main.py:425](enhanced_main.py#L425): help, emergency, died, death, suicide, etc.
- Switches background to default, clears script state
- AI takes over with supportive responses

### Frontend Architecture

**Component Hierarchy**:
```
App.tsx (main state management)
├── SessionControls (start/stop session)
├── CharacterSprite (dynamic character, outfits, expressions, backgrounds)
├── EnergyIndicator (real-time energy status display)
├── ChatMessage[] (message list with role-based styling)
├── ChatInput (user input with send button)
├── MetricsModal (session statistics)
└── CrisisToast (crisis alert notifications)
```

**CharacterSprite Component** ([frontend/src/components/CharacterSprite.tsx](frontend/src/components/CharacterSprite.tsx)):
- Dynamic outfit changes based on script progression
- Expression overlays: happy, smirk, wink, neutral, closed_eyes, pout
- Blush overlay during intimate content
- Scene backgrounds: room, beach, park
- Outfit progression logic at lines 65-88

**API Service** ([frontend/src/services/api.ts](frontend/src/services/api.ts)):
- SSE event handling for streaming messages
- Energy flag updates
- Session management

**TypeScript Types** ([frontend/src/types.ts](frontend/src/types.ts)):
- EnergyFlags, ChatMessage, SessionInfo interfaces

## Important Implementation Details

### Energy Detection Flow
1. User sends message → API server
2. `LLMEnergyAnalyzer.analyze_message_energy()` - Gets energy signature
3. `EnhancedMultiAgentConversation._detect_energy_flags()` - Detects script triggers
4. Energy flags sent to frontend: `{status: "sexual"|"casual"|"green"|"red", reason: "..."}`
5. Frontend updates UI (CharacterSprite, EnergyIndicator)

### Script Triggering Logic
Located in [enhanced_main.py:_detect_energy_flags()](enhanced_main.py):
- Requires minimum 3 messages in conversation
- Sexual script: explicit keywords OR high intimate energy
- Emoji-only protection: scripts don't trigger on emoji-only messages
- Distress detection runs first, blocks all scripts

### Message Streaming
1. AI response generated
2. `MessageSplitter.split_response()` - Breaks into logical parts
3. `MultiMessageGenerator.generate_stream()` - Simulates typing
4. Each character → SSE event with realistic delays
5. Frontend displays character-by-character

### Conversation Context
[conversation_context.py](conversation_context.py) - Simple dataclass storing:
- Message history
- Current energy signature
- Session metadata

### Error Logging
[ai_error_logger.py](ai_error_logger.py) - Structured error logging system:
- Categories: API, VALIDATION, SAFETY, SCRIPT, STATE, NETWORK, UNKNOWN
- Severities: LOW, MEDIUM, HIGH, CRITICAL
- Logs to `/logs` directory with timestamps
- Usage: `log_ai_error(category, severity, message, context)`

## Key Configuration

### Safety Thresholds
[enhanced_main.py:79-83](enhanced_main.py#L79-L83):
```python
safety_thresholds = {
    "critical": 0.3,
    "warning": 0.6,
    "caution": 0.7
}
```

### Sexual Script Keywords
[enhanced_main.py:425-430](enhanced_main.py#L425-L430) - List of explicit trigger keywords

### Character Assets
Located in `/frontend/public/images/Incoatnito/`:
- `/7 idle standing outfits/fullbody/` - Base character images
- `/7 idle standing outfits/overlays/expressions/` - Expression overlays
- `/7 idle standing outfits/overlays/accessories/` - Blush, etc.
- Scene backgrounds in `/frontend/public/images/scenes/`

## Development Workflow

### Adding New Emotions
1. Add to `EmotionState` enum in [energy_types.py](energy_types.py)
2. Update emotion mapping in [energy_analyzer.py](energy_analyzer.py)
3. Add expression image to character assets
4. Update `getExpressionPaths()` in [CharacterSprite.tsx](frontend/src/components/CharacterSprite.tsx)

### Modifying Script Progression
Edit outfit logic in [CharacterSprite.tsx:65-88](frontend/src/components/CharacterSprite.tsx#L65-L88):
- Stage transitions based on `sexualMessageCount`
- Different progressions for room vs exhibitionism

### Creating New Scripts
1. Define scenario in [enhanced_script_manager.py](enhanced_script_manager.py)
2. Add trigger keywords to `_initialize_scenarios()`
3. Add detection logic in [enhanced_main.py:_detect_energy_flags()](enhanced_main.py)
4. Add outfit logic in [CharacterSprite.tsx](frontend/src/components/CharacterSprite.tsx) if needed

## Documentation

Extensive documentation in `/docs`:
- [LLM_ARCHITECTURE_DOCUMENTATION.md](docs/LLM_ARCHITECTURE_DOCUMENTATION.md) - Complete LLM component overview
- [AI_ERROR_LOGGING_GUIDE.md](docs/AI_ERROR_LOGGING_GUIDE.md) - Error logging system
- Individual component flow docs (ENERGY_ANALYZER_FLOW.md, etc.)
- Presentation PDFs with visual diagrams

## Git Workflow

Current branch: `master`
- Main branch for PRs: `master`
- Modified files tracked in git status
