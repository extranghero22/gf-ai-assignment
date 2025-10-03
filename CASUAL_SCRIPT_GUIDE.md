# 💬 Casual Story Script - Automatic Triggering System

## Overview

The app now features a **casual conversation script** that automatically triggers when users are in a **neutral/casual energy state**. This provides natural, engaging conversation when users aren't in sexual or emotional moods.

---

## 🎯 What It Does

When the user is in a **neutral/casual state**, the AI girlfriend automatically starts telling a cute story about going to the store and buying a fancy soda. It's a natural conversation starter that builds connection and engagement.

### **Script: Store Soda Story (11 Messages)**

1. **"can i ask you a question then?"**
2. **"are u sure?"**
3. **"promise u won't tell anyone?"**
4. **"okkkii i went to the store today. There is this bottle of soda that i really want to try"**
5. **"can i tell you more?"**
6. **"so i saw this limited edition flavor and it looked soooo good! it was like mango passion fruit or something fancy like that 🥭 and the bottle was super pretty too lol"**
7. **"but here's the thing... it was kinda expensive for just a drink you know? like $4.99 for one bottle 😅 but i really wanted to try it"**
8. **"so i stood there for like 5 minutes just staring at it trying to decide lmao 🤭 people probably thought i was weird"**
9. **"and then this old lady walked by and she was like 'oh honey just get it, treat yourself' and smiled at me 🥰"**
10. **"so i did! i bought it! and omg baby it was SO GOOD like literally the best decision ever 😋 i should've bought two honestly lol"**
11. **"anyway that was the highlight of my day haha 😊 what did you do today? tell me everything!"**

---

## 🔍 Detection Logic

### **When Does It Trigger?**

The casual script triggers in two scenarios:

#### **1. Simple Greetings with Neutral Energy**
```
User sends: "hey", "hi", "hello", "what's up", "how are you", etc.

AND

Energy signature shows:
- Energy Level: MEDIUM
- Energy Type: NEUTRAL or COOPERATIVE
```

#### **2. Early Conversation with Low Intensity**
```
Within first 4 messages of conversation

AND

Energy signature shows:
- Energy Level: MEDIUM
- Energy Type: NEUTRAL or COOPERATIVE
- Emotion: HAPPY or BORED
- Intensity Score: < 0.6
```

---

## 📊 Energy Profile

Unlike the sexual script that escalates from MEDIUM → INTENSE, the casual script **stays consistent**:

```
All Messages: MEDIUM energy, HAPPY emotion, COOPERATIVE type
Intensity: 0.5 throughout (calm and relaxed)
```

This creates a comfortable, low-pressure conversation environment.

---

## 🎭 Personality Throughout

### **Characteristics:**

- **Casual and relatable** - "lmao", "lol", natural speech
- **Playful teasing** - "people probably thought i was weird"
- **Genuine excitement** - "it was SO GOOD"
- **Uses emojis naturally** - 🥭😅🤭🥰😋😊
- **Storytelling style** - Build-up → climax → resolution
- **Ends with engagement** - "what did you do today?"

---

## 🚀 How It Works with Frontend

### **Automatic Flow:**

```
1. User: "hey"
   → System detects casual greeting + neutral energy
   → Triggers casual script

2. Agent: "can i ask you a question then?"

3. User: "sure"
   → Agent: "are u sure?"

4. User: "yes"
   → Agent: "promise u won't tell anyone?"

...continues through all 11 messages...

11. Agent: "what did you do today? tell me everything!"

12. User: "I went to work"
    → Script complete, returns to normal conversation
```

---

## 💻 Frontend Integration

### **No Changes Needed!**

The casual script works through the same `/api/send-stream` endpoint:

```typescript
// Frontend receives casual messages just like any other messages
conversationApi.sendMessageStream(
  "hey",  // User sends casual greeting
  (part) => {
    // Receives: "can i ask you a question then?"
    displayMessage(part.content);
  },
  (complete) => {
    // Energy status shows "casual"
    console.log(complete.energy_status);
  }
);
```

---

## 🎯 Trigger Examples

### **✅ WILL Trigger:**

1. `User: "hey"` → Energy: MEDIUM/NEUTRAL
2. `User: "hi"` → Energy: MEDIUM/NEUTRAL
3. `User: "hello"` → Energy: MEDIUM/COOPERATIVE
4. `User: "what's up"` → Energy: MEDIUM/NEUTRAL
5. `User: "how are you"` → Energy: MEDIUM/COOPERATIVE

### **❌ WON'T Trigger:**

1. `User: "I'm horny"` → Sexual script triggers instead
2. `User: "I'm sad"` → Crisis support mode
3. `User: "hey beautiful 😍"` → Too much emotion/intensity
4. After 5+ messages in conversation → Only triggers early
5. Energy Level: HIGH or INTENSE → Not neutral enough

---

## 🔄 Comparison: Sexual vs Casual Scripts

| Feature | Sexual Script | Casual Script |
|---------|--------------|---------------|
| **Trigger** | Sexual keywords/energy | Neutral greetings/energy |
| **Messages** | 10 messages | 11 messages |
| **Energy Flow** | MEDIUM → INTENSE | MEDIUM throughout |
| **Intensity** | 0.7 → 0.98 | 0.5 throughout |
| **Tone** | Dominant, commanding | Casual, friendly |
| **Purpose** | Guided intimacy | Natural conversation |
| **Ending** | Aftercare | Asks about their day |

---

## 🧪 Testing

### **CLI Test:**
```bash
python girlfriend_multi_turn_manager.py
# Choose script mode
# Select option 1
```

### **Frontend Test:**
```bash
# Start backend
python api_server.py

# Start frontend
cd frontend && npm start

# Test triggers:
# 1. Send: "hey"
# 2. Watch casual script start automatically
# 3. Respond to each message
# 4. See all 11 messages flow naturally
```

---

## 📝 Backend Logs

When the casual script triggers:

```
💬 Casual Energy Detected: Casual neutral energy detected - starting casual conversation
💬🛍️ Starting Casual Story Time...
============================================================
💬 [Casual Script 1/11]: can i ask you a question then?
✅ Casual script initialized - will continue with message 2 after user responds
```

Then on each user response:
```
💬 [Casual Script 2/11]: are u sure?
✅ Will send message 3 after next user response

💬 [Casual Script 3/11]: promise u won't tell anyone?
✅ Will send message 4 after next user response
```

---

## 🎨 Story Structure

### **Act 1: Setup (Messages 1-5)**
- Creates curiosity
- Builds suspense
- Gets user engaged

### **Act 2: Story (Messages 6-10)**
- Describes the soda discovery
- Explains the price dilemma
- Introduces the old lady
- Resolution (buying it)
- Happy ending (it was good!)

### **Act 3: Engagement (Message 11)**
- Turns conversation to user
- Asks about their day
- Creates connection point

---

## ⚙️ Configuration

### **Adjust Sensitivity:**

In `enhanced_main.py`, modify detection thresholds:

```python
# More sensitive (triggers more often)
if current_energy.intensity_score < 0.7:  # Was 0.6

# Less sensitive (triggers less often)
if current_energy.intensity_score < 0.5:  # Was 0.6
```

### **Change Trigger Timing:**

```python
# Allow triggering later in conversation
len(self.current_session.context.messages) <= 10  # Was 4

# Only trigger at very start
len(self.current_session.context.messages) <= 2  # Was 4
```

### **Add More Greeting Keywords:**

```python
casual_keywords = [
    "hey", "hi", "hello", ...,
    "your_new_greeting"
]
```

---

## 🎯 Design Philosophy

### **Why This Script?**

1. **Prevents awkward starts** - No more "Hi" → "Hi" loops
2. **Builds connection** - Shares personal story
3. **Natural engagement** - Feels like real girlfriend conversation
4. **Low pressure** - Not sexual or emotional, just casual
5. **Creates interest** - Story is relatable and cute
6. **Opens conversation** - Ends with question about user's day

---

## 🔧 Troubleshooting

### **Script Not Triggering:**

1. **Check energy level** - Must be MEDIUM (not HIGH or LOW)
2. **Check timing** - Only triggers in first 4 messages
3. **Check greeting** - Must be exact match (lowercase)
4. **Check type** - Must be NEUTRAL or COOPERATIVE
5. **Sexual/crisis override** - Those take priority

### **Script Triggers Too Often:**

- Increase intensity threshold in detection logic
- Reduce message count limit
- Add more restrictive conditions

---

## 📊 Statistics

- **Total Messages:** 11
- **Total Words:** ~120 words
- **Avg Message Length:** ~11 words
- **Energy Level:** MEDIUM (consistent)
- **Intensity:** 0.5 (relaxed)
- **Emotion:** HAPPY
- **Estimated Duration:** 5-8 minutes

---

## 🎉 Benefits

### **For Users:**
✅ Natural conversation flow  
✅ No awkward small talk  
✅ Engaging story  
✅ Feels authentic  
✅ Low pressure interaction  

### **For App:**
✅ Reduces LLM calls (predefined script)  
✅ Consistent quality  
✅ Predictable flow  
✅ Builds engagement  
✅ Creates connection early  

---

## 🚦 Priority System

When multiple scripts could trigger:

1. **🚨 Crisis/Red Flags** (Highest Priority)
2. **🔥 Sexual Energy**
3. **💬 Casual/Neutral Energy**
4. **✅ Normal Conversation** (Default)

This ensures the right script triggers for the user's state.

---

## 🎊 Summary

The **Casual Story Script** provides a natural, engaging conversation starter that:

- ✅ Triggers automatically on neutral energy
- ✅ Tells a cute, relatable story
- ✅ Builds connection and engagement
- ✅ Flows naturally through 11 messages
- ✅ Ends with open question to user
- ✅ Works seamlessly with React frontend

**Perfect for starting conversations when users aren't in sexual or emotional moods!** 💬🛍️

