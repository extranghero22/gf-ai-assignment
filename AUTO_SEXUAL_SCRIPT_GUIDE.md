# Automatic Sexual Script Triggering System

## Overview

The app now automatically detects when the user expresses sexual interest or arousal and triggers the **Guided Intimacy Script** (Mommy's Instructions) automatically. This creates a seamless, responsive experience where the AI girlfriend adapts to the user's energy and desires.

## How It Works

### 1. **Sexual Energy Detection**

The system detects sexual energy through multiple methods:

#### A. Keyword Detection
The following keywords in user messages trigger sexual energy detection:
- `horny`, `hard`, `wet`, `aroused`, `turned on`
- `want you`, `need you`, `touch me`, `kiss me`
- `fuck`, `sex`, `cum`, `orgasm`, `pleasure`
- `desire`, `lust`, `naughty`, `dirty`, `intimate`
- `make love`, `seduce`, `tease`, `flirt`, `fantasy`
- `dream about you`

#### B. Energy Signature Analysis
The LLM-powered energy analyzer also detects sexual energy based on:
- **Energy Level**: HIGH or INTENSE
- **Energy Type**: INTIMATE
- **Dominant Emotion**: EXCITED or LOVING
- **Intensity Score**: > 0.6 or 0.7

### 2. **Automatic Script Triggering**

When sexual energy is detected:

1. **Energy Flag Set**: Status changes to `"sexual"`
2. **Decision Made**: System decides to trigger the guided intimacy script
3. **Script Executes**: The 5-message guided intimacy sequence begins automatically
4. **User Interaction**: System waits for user response between each message
5. **Return to Normal**: After completion, returns to regular conversation mode

### 3. **The Guided Intimacy Script**

The script consists of 5 carefully crafted messages:

**Message 1**: Opening & Engagement
```
"mommy could reallyy use someone obedient who actually knows how to follow instructions…🥱 what are you doing right now?"
```

**Message 2**: Consent & Dominance
```
"good i love that you're down to listen to mommy ❤️ im being serious though you better not disobey.. i need u to just sit back and relax… are u down? 😈"
```

**Message 3**: Breathing & Relaxation
```
"i'm glad ur being so good so far 🥰 first i wanna set the mood.. close your eyes and take in a big deep breath, hold it for a second then breathe out slowly.. do this a 3 times and notice how your body lets go of any of the stress and tension youve been carrying with you from the week 🤭 are you still with me? should i keep typing? 😘"
```

**Message 4**: Physical Imagery
```
"i knew  you were having fun 😘 now, imagine me lying next to you in bed.. my fingers gently tracing a path from your lips.. over your chest.. down your stomach... and settling at your zipper. i can literally feeel the heat radiating from your cock as the anticipations building 🤭 tell mee, what do you feel baby? 🥵"
```

**Message 5**: Sensory Focus
```
"i want you to focus on those sensations 🥰 notice how the fabric of your pants feels against your skin.. the warmth of your own touch as your hand hovers over your cock.. and the way your breath is starting to get deeper and deeper as you start to get more and more turned on 🥵 give me a minute, let me give you some visuals to work with 🤭"
```

## Implementation Details

### Files Modified

1. **`enhanced_main.py`**
   - Added sexual energy detection in `_detect_energy_flags()`
   - Added decision logic in `_make_energy_aware_decision()`
   - Added handler `_trigger_guided_intimacy_script()`
   - Updated energy monitoring to log sexual status

2. **`girlfriend_multi_turn_manager.py`**
   - Added script as option #6 for manual triggering
   - Available in terminal/CLI mode

3. **`enhanced_script_manager.py`**
   - Added `guided_intimacy_scenario` with full energy tracking
   - Configured energy flow: MEDIUM → HIGH → HIGH → INTENSE → INTENSE
   - Added automatic scenario selection for sexual energy

### Energy Flow Design

The script follows a carefully designed energy progression:

```
User State           →  Script Energy Level
─────────────────────────────────────────────
Sexual interest      →  MEDIUM  (Message 1)
Engaged              →  HIGH    (Message 2)
Relaxed              →  HIGH    (Message 3)
Aroused              →  INTENSE (Message 4)
Focused              →  INTENSE (Message 5)
```

## Testing

### Manual Test
Run the test script:
```bash
python test_auto_sexual_script.py
```

### Interactive Test
1. Start the app: `python api_server.py` (or use the React frontend)
2. Send a message like: "I'm so horny right now"
3. The script should trigger automatically

### Example Conversation Flow

```
User: "Hey baby, I'm feeling really horny"

🔥 Sexual Energy Detected: Sexual energy detected - ready for guided intimacy

🔥💕 Initiating Guided Intimacy Experience...
============================================================

[Script Message 1 appears]
Agent: mommy could reallyy use someone obedient who actually knows how to follow instructions…🥱 what are you doing right now?

💬 You: [User responds]

[Script continues through all 5 messages with user interaction]

✅ Guided intimacy sequence completed successfully!

💬 Continuing conversation... You:
```

## API Integration

### React Frontend
The sexual energy status is sent to the frontend through the energy_status field:

```typescript
{
  "status": "sent",
  "ai_response": "...",
  "energy_status": {
    "status": "sexual",
    "reason": "Sexual energy detected - ready for guided intimacy"
  }
}
```

### Streaming API
The `/api/send-stream` endpoint will stream the script messages with appropriate delays when sexual energy is detected.

## Safety & Consent

### Safety Status
- Sexual content runs with safety status: `"green"`
- The system respects the app's adult nature
- Crisis detection still overrides sexual detection

### User Control
- Script can be interrupted by user
- User can respond normally between messages
- Returns to regular conversation after completion

## Configuration

### Adjusting Sensitivity

To make the detection more/less sensitive, modify these values in `enhanced_main.py`:

```python
# Less sensitive (higher threshold)
if current_energy.intensity_score > 0.8:  # Was 0.7

# More sensitive (lower threshold)  
if current_energy.intensity_score > 0.5:  # Was 0.7
```

### Adding Keywords

Add more sexual keywords in `_detect_energy_flags()`:

```python
sexual_keywords = [
    "horny", "hard", "wet", ...,
    "your_new_keyword_here"
]
```

## Troubleshooting

### Script Not Triggering

1. **Check energy analyzer**: Ensure `GOOGLE_API_KEY` is set for Gemini API
2. **Check keywords**: Verify message contains sexual keywords
3. **Check intensity**: User message might not be intense enough
4. **Check logs**: Look for `🔥 Sexual energy detected!` in console

### Script Interrupts Unexpectedly

1. **Check user response**: System analyzes for stop indicators
2. **Check safety**: Safety monitor might be flagging content
3. **Check energy flags**: Red flags override sexual triggers

## Future Enhancements

Potential improvements:
- Multiple script variations based on context
- Progressive intensity matching
- User preference learning
- More dynamic content generation
- Integration with typing simulator for realistic delays

## Debug Mode

Enable debug logging to see detection in action:

```python
# In enhanced_main.py, the system already logs:
print(f"🔥 Sexual energy detected! Triggering guided intimacy script...")
print(f"🔍 DEBUG: Energy flags: {self.energy_flags}")
```

## Conclusion

The automatic sexual script triggering system creates a natural, responsive experience that adapts to user energy and desires. The system balances automation with user control, maintaining safety while delivering an engaging adult AI girlfriend experience.

