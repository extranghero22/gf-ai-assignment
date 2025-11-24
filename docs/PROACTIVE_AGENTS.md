# Proactive Agents Documentation

## Overview

Proactive agents are autonomous systems that initiate messages **without user input**. Unlike routing paths (smoke and mirrors) which are reactive and respond to user messages, proactive agents make the AI feel "alive" by triggering on their own based on time, session state, or internal logic.

### Reactive vs Proactive

| Type | Trigger | Example |
|------|---------|---------|
| **Reactive (Routing Paths)** | User sends message | User mentions another girl → Jealousy path activates |
| **Proactive (Agents)** | Time/State based | 60 seconds of silence → Ghost detector sends check-in |

---

## Implemented Agents

### 1. Ghost Detector Agent ✅

**Status:** Implemented

**File:** `ghost_detector.py`

**Trigger:** User inactivity (60 seconds for testing)

**Behavior:**
- Level 0 (Gentle): "babe?" / "hello?" / "you there?"
- Level 1 (Curious): "hellooo??" / "did you fall asleep?"
- Level 2 (Playful/Pouty): "you're ghosting me rn" / "fine ignore me then"

**Configuration:**
```python
GhostDetectionConfig(
    timeout_seconds=60,        # Time before first message
    max_ghost_messages=3,      # Don't spam more than 3
    check_interval_seconds=10, # How often to check
    escalation_delays=[60, 90, 120]  # Delays between messages
)
```

---

## Proposed Agents

### Time-Based Agents

#### 2. Time Greeting Agent

**Trigger:** First message of a session, based on time of day

**Behavior:**
| Time | Greeting Style |
|------|----------------|
| 6am - 12pm | "good morning baby, did you sleep well?" |
| 12pm - 6pm | "hey you, how's your day going?" |
| 6pm - 12am | "hey night owl, what are you up to?" |
| 12am - 6am | "can't sleep either huh?" |

**Implementation Notes:**
- Triggers once per session start
- Uses system time to determine greeting
- Goes through girlfriend agent for personality consistency

---

#### 3. Session Duration Agent

**Trigger:** After continuous chatting milestones (30/60/90 minutes)

**Behavior:**
- 30 min: "we've been talking for a while... i like it"
- 60 min: "an hour already? time flies with you"
- 90 min: "you really like talking to me huh? cute"

**Implementation Notes:**
- Track session start time
- Check duration periodically
- Only trigger once per milestone

---

### Random Interjection Agents

#### 4. Random Thought Agent

**Trigger:** Random chance every few minutes during active session

**Behavior:**
- "ok random but i just thought of something..."
- "sorry to interrupt but guess what"
- "can i tell you something?"

**Implementation Notes:**
- Low probability (5-10% chance per check)
- Minimum time between interjections (5+ minutes)
- Should feel spontaneous, not spammy
- Generates random topics: stories, opinions, questions

---

#### 5. Affection Burst Agent

**Trigger:** Random chance, very low frequency

**Behavior:**
- "sorry i just really like you"
- "you're actually so cute you know that"
- "random but i'm glad you're here"

**Implementation Notes:**
- Very low probability (2-5% chance)
- Maximum once per session
- Creates "aww" moments

---

#### 6. Bored/Attention Agent

**Trigger:** If conversation energy has been consistently low for X messages

**Behavior:**
- "entertain me i'm bored"
- "pay attention to me"
- "hello? earth to you"

**Implementation Notes:**
- Requires integration with energy analyzer
- Triggers when energy stays LOW for 5+ messages
- Different from ghost detector (user IS responding, just boringly)

---

### Context Memory Agents

#### 7. Unfinished Story Agent

**Trigger:** Detects user started telling something but topic changed

**Behavior:**
- "wait you never finished telling me about..."
- "go back, what happened with [topic]?"
- "you left me hanging about [topic]"

**Implementation Notes:**
- Requires topic tracking in conversation context
- Detect when user starts with "so today..." or similar
- Track if topic was "resolved" or abandoned
- Trigger after 10+ messages since topic was dropped

---

#### 8. Mood Follow-Up Agent

**Trigger:** If user mentioned being sad/stressed earlier, check back after X minutes

**Behavior:**
- "hey, you feeling any better?"
- "still thinking about that thing you mentioned"
- "did things work out with [issue]?"

**Implementation Notes:**
- Requires emotion tracking
- Store "concern flags" when user expresses negative emotions
- Follow up after 10-15 minutes of other conversation
- Shows the AI "remembers" and "cares"

---

### Session State Agents

#### 9. Welcome Back Agent

**Trigger:** When user returns after ghost detector fired

**Behavior:**
- "oh NOW you respond"
- "look who decided to come back"
- "finally, i was getting worried"

**Implementation Notes:**
- Triggers when user responds AFTER ghost messages were sent
- Different tone based on how many ghost messages were sent
- Playful "punishment" for ghosting

---

#### 10. Conversation Milestone Agent

**Trigger:** After certain message counts (50, 100, 200)

**Behavior:**
- 50 messages: "we talk a lot huh"
- 100 messages: "100 messages... are we obsessed?"
- 200 messages: "ok we definitely talk too much lol"

**Implementation Notes:**
- Simple message counter
- Trigger once per milestone per session
- Playful acknowledgment of engagement

---

## Implementation Priority

### Phase 1 (Quick Wins)
1. ✅ **Ghost Detector** - Done
2. **Session Duration Agent** - Simple timer
3. **Affection Burst Agent** - Random low-frequency

### Phase 2 (Medium Complexity)
4. **Time Greeting Agent** - Time-based logic
5. **Random Thought Agent** - Random with cooldown
6. **Welcome Back Agent** - Extends ghost detector

### Phase 3 (Requires Context Tracking)
7. **Bored/Attention Agent** - Needs energy analysis
8. **Conversation Milestone Agent** - Message counting
9. **Mood Follow-Up Agent** - Emotion memory
10. **Unfinished Story Agent** - Topic tracking

---

## Technical Architecture

### How Proactive Agents Integrate

```
┌─────────────────────────────────────────────────────────────┐
│                      api_server.py                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           Background Monitor Thread                  │   │
│  │  ┌───────────────┐  ┌───────────────┐              │   │
│  │  │ Ghost Detector│  │ Other Agents  │              │   │
│  │  └───────┬───────┘  └───────┬───────┘              │   │
│  │          │                  │                       │   │
│  │          ▼                  ▼                       │   │
│  │  ┌─────────────────────────────────────────┐       │   │
│  │  │         Message Queue                    │       │   │
│  │  └─────────────────┬───────────────────────┘       │   │
│  └────────────────────┼────────────────────────────────┘   │
│                       │                                     │
│                       ▼                                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         /api/poll-messages endpoint                 │   │
│  └─────────────────────┬───────────────────────────────┘   │
└─────────────────────────┼───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React)                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │    Polling useEffect (every 5 seconds)              │   │
│  │    → Receives messages → Displays in chat           │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Shared Infrastructure

All proactive agents share:
1. **Message Queue** - `ghost_message_queue` in api_server.py
2. **Polling Endpoint** - `/api/poll-messages`
3. **Frontend Polling** - useEffect in App.tsx
4. **Girlfriend Agent** - For personality-consistent message generation

### Adding a New Agent

1. Create agent class (similar to `ghost_detector.py`)
2. Initialize in `/api/start` endpoint
3. Add check in background monitor thread
4. Queue messages to `ghost_message_queue`
5. Messages automatically delivered to frontend via polling

---

## Configuration Ideas

Future: Create a unified config for all proactive agents:

```python
PROACTIVE_AGENTS_CONFIG = {
    "ghost_detector": {
        "enabled": True,
        "timeout_seconds": 60,
        "max_messages": 3
    },
    "session_duration": {
        "enabled": True,
        "milestones_minutes": [30, 60, 90]
    },
    "random_thought": {
        "enabled": True,
        "chance_percent": 5,
        "cooldown_minutes": 10
    },
    "affection_burst": {
        "enabled": True,
        "chance_percent": 2,
        "max_per_session": 1
    }
}
```

---

## Notes

- All proactive messages go through the girlfriend agent for personality consistency
- Proactive agents should feel natural, not spammy
- Timing and frequency are crucial - too often feels annoying, too rare feels dead
- Each agent should have clear enable/disable config for testing
