# 💬 Casual Script Improvements

## Overview

The casual store story script has been enhanced with **grouped messages** and **intelligent disinterest detection** to create a more natural, responsive conversation experience.

---

## ✨ What's New

### 1. **Grouped Messages** (Multi-message sends)

Some messages are now sent **together without waiting** for user response, creating natural story flow.

#### **Message Groups:**

**Group 1: Messages 4-5 (Story Introduction)**
```
"okkkii i went to the store today. There is this bottle of soda that i really want to try"
"can i tell you more?"
```
→ Sent together to build momentum

**Group 2: Messages 7-10 (Story Climax)**
```
"but here's the thing... it was kinda expensive for just a drink you know? like $4.99 for one bottle 😅 but i really wanted to try it"
"so i stood there for like 5 minutes just staring at it trying to decide lmao 🤭 people probably thought i was weird"
"and then this old lady walked by and she was like 'oh honey just get it, treat yourself' and smiled at me 🥰"
"so i did! i bought it! and omg baby it was SO GOOD like literally the best decision ever 😋 i should've bought two honestly lol"
```
→ Sent together as complete story arc

---

### 2. **Disinterest Detection** 

The AI now **detects when users aren't interested** and responds naturally!

#### **How It Works:**

**After Message 3**, the system checks each user response for disinterest signals:

**Disinterest Signals:**
- Very short responses: "ok", "k", "cool", "nice", "meh", "whatever"
- Disinterest phrases: "boring", "not interested", "don't care", "stop"
- Length check: Must be ≤ 10 chars for most signals, < 20 for explicit disinterest

**When Detected:**
```
User: "k"
→ AI: "lol ok i will stop you dont seem interested in my story"
```

---

### 3. **Recovery Flow**

If user apologizes or asks to continue, the story **resumes**!

**Recovery Phrases:**
- "sorry"
- "continue", "keep going", "go on"
- "tell me", "finish"
- "no wait", "actually"
- "i want to hear"
- "please continue"
- "my bad"
- "go ahead"

**Recovery Flow:**
```
1. User: "k"
   AI: "lol ok i will stop you dont seem interested in my story"

2. User: "sorry continue"
   AI: "ok ill continue my story"

3. [Script resumes from where it left off]
```

**If User Confirms Disinterest:**
```
1. User: "k"
   AI: "lol ok i will stop you dont seem interested in my story"

2. User: "yeah whatever"
   [Script ends, returns to normal conversation]
```

---

## 📊 Script Structure

### **Before (11 separate messages):**
```
1. "can i ask you a question then?"     [wait]
2. "are u sure?"                         [wait]
3. "promise u won't tell anyone?"        [wait]
4. "okkkii i went to the store..."       [wait]
5. "can i tell you more?"                [wait]
6. "so i saw this limited edition..."    [wait]
7. "but here's the thing..."             [wait]
8. "so i stood there..."                 [wait]
9. "and then this old lady..."           [wait]
10. "so i did! i bought it..."           [wait]
11. "anyway that was the highlight..."   [wait]
```

### **After (7 interaction points):**
```
1. "can i ask you a question then?"                                    [wait]
2. "are u sure?"                                                       [wait]
3. "promise u won't tell anyone?"                                      [wait]
4. "okkkii..." + "can i tell you more?"                               [wait]
5. "so i saw this limited edition..."                                  [wait]
6. "but here's the thing..." + "so i stood there..." + 
   "and then this old lady..." + "so i did!"                          [wait]
7. "anyway that was the highlight..."                                  [wait]
```

---

## 🎯 Example Flows

### **Flow 1: Engaged User**
```
AI: "can i ask you a question then?"
User: "sure"

AI: "are u sure?"
User: "yes"

AI: "promise u won't tell anyone?"
User: "i promise"

AI: "okkkii i went to the store today. There is this bottle of soda that i really want to try"
    "can i tell you more?"
User: "yes tell me!"

AI: "so i saw this limited edition flavor..."
User: "ooh nice"

AI: "but here's the thing... it was kinda expensive..."
    "so i stood there for like 5 minutes..."
    "and then this old lady walked by..."
    "so i did! i bought it! and omg baby it was SO GOOD..."
User: "haha that's cute"

AI: "anyway that was the highlight of my day haha 😊 what did you do today?"
```

---

### **Flow 2: Disinterested User**
```
AI: "can i ask you a question then?"
User: "sure"

AI: "are u sure?"
User: "yes"

AI: "promise u won't tell anyone?"
User: "ok"

AI: "okkkii i went to the store today..."
    "can i tell you more?"
User: "k"

AI: "lol ok i will stop you dont seem interested in my story"
[Script ends]
```

---

### **Flow 3: Recovery Flow**
```
AI: "okkkii i went to the store today..."
    "can i tell you more?"
User: "meh"

AI: "lol ok i will stop you dont seem interested in my story"

User: "sorry no continue"

AI: "ok ill continue my story"

[Next user response triggers next script message]
User: "ok"

AI: "so i saw this limited edition flavor..."
[Script continues normally]
```

---

## 🛠️ Technical Implementation

### **Grouped Messages Format:**

```python
casual_story_script = [
    "message 1",                    # Single message
    "message 2",                    # Single message
    [                               # Grouped messages
        "message 3a",
        "message 3b",
        "message 3c"
    ],
    "message 4"                     # Single message
]
```

### **Disinterest Detection Logic:**

```python
# Only check after message 3 (give them time to engage)
if script_index >= 3:
    # Check for short, disinterested responses
    is_disinterested = (
        (len(last_user_msg) <= 10 and matches_disinterest_signal) or
        (explicit_disinterest_phrase and len(last_user_msg) < 20)
    )
```

### **State Tracking:**

- `casual_script_active`: True while script is running
- `casual_script_paused`: True when user showed disinterest
- `casual_script_index`: Current position in script

---

## 📱 Frontend Behavior

### **Grouped Messages Display:**

The frontend will receive multiple messages in quick succession:

```typescript
// Message group arrives as separate events but quickly
onMessagePart({ content: "message 1", index: 0, group_part: 0 })
onMessagePart({ content: "message 2", index: 0, group_part: 1 })
onMessagePart({ content: "message 3", index: 0, group_part: 2 })
```

All appear in chat rapidly, creating natural story flow.

---

## ⚙️ Configuration

### **Adjust Disinterest Sensitivity:**

In `enhanced_main.py`:

```python
# More sensitive (triggers easier)
if script_index >= 2:  # Was 3

# Less sensitive (requires more signals)
if script_index >= 5:  # Was 3
```

### **Add More Disinterest Signals:**

```python
disinterest_signals = [
    "ok", "k", "cool", ...,
    "your_custom_signal"
]
```

### **Modify Recovery Phrases:**

```python
recovery_phrases = [
    "sorry", "continue", ...,
    "your_custom_phrase"
]
```

---

## 🎨 Benefits

### **Grouped Messages:**
✅ More natural story flow  
✅ Reduces user fatigue (fewer responses needed)  
✅ Creates momentum in storytelling  
✅ Better pacing and rhythm  

### **Disinterest Detection:**
✅ Respects user's attention  
✅ Prevents annoying continuation  
✅ Shows emotional intelligence  
✅ Allows graceful exit  

### **Recovery Flow:**
✅ Allows second chances  
✅ Handles misunderstandings  
✅ Natural conversation repair  
✅ User feels heard  

---

## 📊 Statistics

- **Total Messages:** 11 (unchanged)
- **Interaction Points:** 7 (reduced from 11)
- **User Responses Needed:** 6-7 (down from 10)
- **Disinterest Check:** Starts after message 3
- **Recovery Phrases:** 12 recognized
- **Disinterest Signals:** 16 recognized

---

## 🧪 Testing

### **Test Grouped Messages:**
```bash
# Start app
python api_server.py
cd frontend && npm start

# Send: "hey"
# Watch messages 4-5 arrive together
# Watch messages 7-10 arrive together
```

### **Test Disinterest Detection:**
```
1. Trigger casual script: "hey"
2. Respond to first 3 messages normally
3. Send: "k"
4. Watch AI respond: "lol ok i will stop..."
```

### **Test Recovery:**
```
1. Trigger disinterest: "k"
2. AI: "lol ok i will stop..."
3. Send: "sorry continue"
4. AI: "ok ill continue my story"
5. Script resumes!
```

---

## 🎯 Summary

The casual script now features:

1. **Grouped Messages** - Story flows naturally with 7 interaction points instead of 11
2. **Disinterest Detection** - Recognizes when user isn't engaged (after message 3)
3. **Recovery Flow** - Allows users to apologize and continue
4. **Natural Exits** - Gracefully ends when user confirms disinterest
5. **Emotional Intelligence** - Responds appropriately to user engagement level

These improvements make the casual script feel more **natural, responsive, and respectful** of the user's attention! 💬✨

