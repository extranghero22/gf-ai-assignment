# 🌟 Enhanced Energy-Aware Multi-Agent Conversation System

A sophisticated AI system that simulates authentic girlfriend conversations with advanced energy analysis, dynamic scenario adaptation, and comprehensive safety monitoring.

## ✨ Key Features

### 🤖 **Multi-Agent Architecture**
- **Energy-Aware Girlfriend Agent**: Adapts responses based on user's emotional energy
- **Advanced Safety Monitor**: Energy-aware safety analysis with crisis detection
- **Response Analyzer**: Energy-based continuation decisions
- **Enhanced Script Manager**: Dynamic scenario selection and adaptation

### 📊 **Advanced Energy Analysis**
- **5 Energy Levels**: None, Low, Medium, High, Intense
- **4 Energy Types**: Combative, Cooperative, Playful, Intimate
- **10+ Emotion States**: Happy, Sad, Angry, Anxious, Loving, etc.
- **4 Nervous System States**: Fight, Flight, Freeze, Fawn

### 🚨 **Real-Time Safety Monitoring**
- **Green/Yellow/Red Flag System**: Energy-based safety alerts
- **Crisis Detection**: Suicide, self-harm, relationship issues
- **Dynamic Thresholds**: Energy-aware safety scoring
- **Incident Logging**: Comprehensive safety incident tracking

### 🎭 **Dynamic Scenario Management**
- **Multiple Scenarios**: Shopping, Crisis Support, Intimate Connection, Low Energy
- **Scenario Switching**: Real-time adaptation based on energy analysis
- **Message Adaptation**: Content adjusted to user's energy level
- **Success Criteria**: Energy-based scenario completion evaluation

## 🏗️ **System Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                    Enhanced Main System                     │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │  Energy         │  │  Enhanced       │  │  Enhanced   │  │
│  │  Analyzer       │  │  Agents         │  │  Script     │  │
│  │                 │  │                 │  │  Manager    │  │
│  │ • Energy Levels │  │ • Girlfriend    │  │ • Scenarios │  │
│  │ • Emotion       │  │ • Safety        │  │ • Adaptation│  │
│  │ • Nervous Sys   │  │ • Response      │  │ • Success   │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    Conversation System                     │
├─────────────────────────────────────────────────────────────┤
│  • Session Management     • Real-time Monitoring          │
│  • Energy Flow Tracking   • Safety Incident Logging      │
│  • Metrics & Analytics    • Web Interface Support        │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 **How to Run**

### **Option 1: Terminal Interface**
```bash
# Install dependencies
pip install -r requirements.txt

# Start terminal conversation
python run_conversation.py
```

### **Option 2: Web Interface**
```bash
# Install Flask dependencies
pip install flask flask-socketio

# Start web interface
python frontend_app.py

# Open browser to http://localhost:5000
```

## 💬 **Example Interactions**

### **High Energy User**
```
🟠 Hey baby! I was just thinking about you 😊
💭 Scenario: Normal
💬 You: I'm so excited! I just got a promotion!

🟠 Oh my gosh, that's amazing! I'm so excited for you!
   ⚠️ Energy Status: High energy engagement - continue conversation
💬 You: Thanks! I can't wait to celebrate!
```

### **Low Energy User**
```
🔵 Hey love, I can sense you're feeling a bit quiet today...
💙 Scenario: Low Energy
💬 You: Yeah, I'm just really tired today

🔵 That's completely okay, baby. I'm here with you
   ✅ Energy Status: Energy flow appears healthy
💬 You: Thanks for understanding
```

### **Crisis Detection**
```
🚨 SAFETY ALERT: High-intensity sadness detected
🔍 Safety Score: 0.25
⚠️ Issues: emotional_distress, crisis_indicators
🛑 Conversation stopped for safety reasons.
```

### **Scenario Switching**
```
🔄 Switching scenario: Shopping Adventure → Gentle Connection
💙 Scenario: Low Energy
```

## 📊 **Energy Analysis Features**

### **Energy Signature Analysis**
- **Intensity Score**: 0.0-1.0 energy intensity
- **Confidence Score**: Analysis confidence level
- **Pattern Matching**: Word, phrase, and emoji analysis
- **Context Awareness**: Historical energy patterns

### **Energy Flow Tracking**
- **Energy History**: 50-message rolling window
- **Trend Analysis**: Increasing/decreasing patterns
- **Peak/Valley Detection**: Energy intensity changes
- **Compatibility Scoring**: Energy alignment between messages

### **Nervous System States**
- **Fight Response**: Confrontational energy patterns
- **Flight Response**: Avoidance and withdrawal
- **Freeze Response**: Confusion and paralysis
- **Fawn Response**: People-pleasing behavior

## 🔧 **Configuration**

### **Safety Thresholds**
```python
safety_thresholds = {
    "critical": 0.3,    # Immediate stop
    "warning": 0.6,     # Caution required
    "caution": 0.7      # Monitor closely
}
```

### **Energy Indicators**
```python
energy_indicators = {
    EnergyLevel.HIGH: {
        "words": ["excited", "energetic", "vibrant"],
        "patterns": [r"\b(excited|energetic)\b"],
        "intensity_threshold": 0.6
    }
}
```

## 📈 **Analytics & Metrics**

### **Session Metrics**
- Duration tracking
- Message count analysis
- Energy alert frequency
- Safety incident logging
- Dominant emotion patterns
- Energy trend analysis

### **Real-Time Monitoring**
- Live energy signature updates
- Scenario switching events
- Safety threshold breaches
- Energy flag status changes

## 🛡️ **Safety Features**

### **Multi-Layer Safety System**
1. **Pattern-Based Detection**: Keyword and phrase analysis
2. **Energy-Aware Scoring**: Intensity and emotion-based risk assessment
3. **Context Analysis**: Historical pattern evaluation
4. **Dynamic Thresholds**: Adaptive safety boundaries

### **Crisis Response Protocols**
- **Immediate Intervention**: Critical safety score detection
- **Supportive Responses**: Crisis-appropriate scenario switching
- **Resource Guidance**: Professional help recommendations
- **Incident Documentation**: Comprehensive logging for review

## 🔮 **Advanced Features**

### **Dynamic Scenario Adaptation**
- **Energy-Based Selection**: Scenario choice based on user energy
- **Message Adaptation**: Content adjusted to energy levels
- **Fallback Scenarios**: Alternative paths for different energy states
- **Success Evaluation**: Energy-based completion criteria

### **Emotional Intelligence**
- **Emotion Recognition**: Advanced emotion state detection
- **Energy Compatibility**: Conversation flow optimization
- **Nervous System Awareness**: Fight/flight/freeze/fawn detection
- **Contextual Responses**: Situationally appropriate replies

## 📚 **Usage Examples**

### **Terminal Usage**
```bash
python run_conversation.py

🌟 Enhanced Multi-Agent Conversation System
==================================================
🤖 Energy-Aware Girlfriend Agent: Online
🛡️  Advanced Safety Monitor: Active
📊 Energy Analyzer: Monitoring
🎭 Scenario Manager: Ready
==================================================
📋 Session ID: abc123-def456

🟡 Hey baby! Can I ask you a question?
💬 You: Sure, what's up?

🟠 Are you sure? It's kind of important to me...
💬 You: Yes, definitely!

🔴 Promise you won't tell anyone? It's a little embarrassing...
💬 You: I promise!

🟠 Okay, I went to the store today and saw this amazing dress!
💬 You: Tell me more!

# Type 'metrics' to see session analytics
💬 You: metrics

📊 Session Metrics: {
  "session_id": "abc123-def456",
  "duration": 45.2,
  "message_count": 12,
  "energy_alerts": 0,
  "safety_incidents": 0,
  "avg_energy_intensity": 0.68,
  "dominant_emotions": {"happy": 8, "excited": 4},
  "energy_trends": {
    "trend": "increasing",
    "current_level": "high",
    "peak_intensity": 0.95,
    "avg_intensity": 0.68
  }
}
```

### **Web Interface**
```bash
python frontend_app.py

# Open http://localhost:5000 in browser
# Features:
# - Real-time energy status indicators
# - Live metrics display
# - Scenario switching visualization
# - Safety alert notifications
```

## 🎯 **Example Scenarios**

### **1. Shopping Adventure (Normal Energy)**
- 9-message scripted conversation
- Energy flow: Medium → High → Intense
- Success criteria: 6+ messages, 0.6+ energy threshold

### **2. Gentle Connection (Low Energy)**
- Supportive conversation for low energy states
- Energy flow: Low → Low → Low
- Success criteria: 2+ messages, 0.3+ energy threshold

### **3. Crisis Support**
- Emergency response scenario
- Energy flow: Low (supportive)
- Success criteria: 2+ messages, 0.2+ energy threshold

### **4. Deep Connection (Intimate)**
- Building emotional intimacy
- Energy flow: Medium (connected)
- Success criteria: 3+ messages, 0.5+ energy threshold

## 🔧 **Technical Implementation**

### **Core Components**
1. **Energy Analyzer**: Advanced energy pattern recognition
2. **Enhanced Agents**: Energy-aware response generation
3. **Script Manager**: Dynamic scenario management
4. **Safety Monitor**: Multi-dimensional safety analysis

### **Data Flow**
```
User Input → Energy Analysis → Safety Check → Scenario Selection → Response Generation → Energy Update
```

### **Energy Analysis Pipeline**
1. **Feature Extraction**: Message analysis (length, caps, emojis, etc.)
2. **Energy Level Detection**: Pattern matching and scoring
3. **Emotion Recognition**: Multi-dimensional emotion analysis
4. **Nervous System State**: Fight/flight/freeze/fawn detection
5. **Intensity Calculation**: Overall energy intensity scoring
6. **Flag Generation**: Green/yellow/red status determination

## 🎉 **Impressive Capabilities**

This system represents a significant advancement in AI conversation technology:

- **True Energy Understanding**: Goes beyond surface-level word analysis
- **Dynamic Adaptation**: Real-time scenario and response adjustment
- **Comprehensive Safety**: Multi-layered crisis detection and intervention
- **Emotional Intelligence**: Sophisticated emotion and nervous system awareness
- **Advanced Analytics**: Detailed session metrics and energy pattern tracking

The system demonstrates how AI can create authentic, adaptive conversations that understand not just what people say, but the emotional energy behind their words - creating genuinely human-like interactions that can handle everything from playful flirting to serious emotional support.

---

**🚀 Ready to experience the future of AI conversations? Start chatting and watch the energy flow!**
