---
marp: true
theme: default
class: lead
paginate: true
backgroundColor: #fff
backgroundImage: url('https://marp.app/assets/hero-background.svg')
---

# Energy Analyzer LLM
## Real-Time Emotional Intelligence

**Google Gemini Pro-Powered Energy Detection**

---

# Overview

## Purpose
- **Real-time emotional state analysis** of user messages
- **Energy level assessment** for conversation flow
- **Intensity scoring** for appropriate responses
- **Fallback mechanism** for reliability

## Model
- **Primary**: Google Gemini Pro
- **Fallback**: Rule-based analysis
- **Input**: User message + conversation context
- **Output**: Energy signature with detailed metrics

---

# Core Functionality

## Energy Analysis Process
```
User Message
    │
    ▼
┌─────────────────┐
│ Gemini Pro      │ ──► Energy Signature
│ Analysis        │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ Rule-based      │ ──► Fallback Analysis
│ Fallback        │     (if LLM fails)
└─────────────────┘
```

## Output Structure
- **Energy Level**: LOW, MEDIUM, HIGH, INTENSE
- **Emotion State**: HAPPY, SAD, EXCITED, LOVING, NEUTRAL
- **Intensity Score**: 0.0 - 1.0 scale
- **Nervous System State**: REST, ACTIVATED, FIGHT, FLIGHT

---

# Energy Levels

## LOW Energy (0.0 - 0.3)
- **Characteristics**: Tired, disinterested, withdrawn
- **Triggers**: "I'm tired", "not interested", "boring"
- **Response Strategy**: Gentle encouragement, casual topics
- **Script Behavior**: May trigger low-energy scenarios

## MEDIUM Energy (0.3 - 0.6)
- **Characteristics**: Normal, engaged, balanced
- **Triggers**: Regular conversation, neutral topics
- **Response Strategy**: Natural conversation flow
- **Script Behavior**: Default scenario selection

---

# Energy Levels (Continued)

## HIGH Energy (0.6 - 0.8)
- **Characteristics**: Excited, energetic, enthusiastic
- **Triggers**: "I'm excited", "let's do something", "fun"
- **Response Strategy**: Match enthusiasm, suggest activities
- **Script Behavior**: May trigger high-energy scenarios

## INTENSE Energy (0.8 - 1.0)
- **Characteristics**: Overwhelming, intense emotions
- **Triggers**: Strong emotional expressions, urgency
- **Response Strategy**: Calm approach, safety monitoring
- **Script Behavior**: Crisis detection, intervention

---

# Emotion States

## HAPPY 😊
- **Detection**: Positive words, joy expressions
- **Response**: Match positivity, share enthusiasm
- **Scripts**: Casual stories, fun activities

## SAD 😢
- **Detection**: Negative words, sadness indicators
- **Response**: Empathetic support, comfort
- **Scripts**: Crisis intervention, comfort scenarios

## EXCITED 🤩
- **Detection**: Excitement words, high energy
- **Response**: Channel energy, suggest activities
- **Scripts**: High-energy scenarios, adventures

---

# Emotion States (Continued)

## LOVING 💕
- **Detection**: Affectionate words, intimacy
- **Response**: Reciprocal affection, warmth
- **Scripts**: Intimate scenarios, romantic content

## NEUTRAL 😐
- **Detection**: Balanced, calm expressions
- **Response**: Natural conversation flow
- **Scripts**: Default scenarios, casual topics

---

# Nervous System States

## REST State
- **Characteristics**: Calm, relaxed, peaceful
- **Triggers**: "I'm relaxed", "feeling good", "calm"
- **Response**: Gentle conversation, comfort
- **Safety Level**: Green

## ACTIVATED State
- **Characteristics**: Alert, engaged, responsive
- **Triggers**: Normal conversation, interest
- **Response**: Natural engagement
- **Safety Level**: Green

---

# Nervous System States (Continued)

## FIGHT State
- **Characteristics**: Aggressive, confrontational, angry
- **Triggers**: "I'm angry", "frustrated", "mad"
- **Response**: De-escalation, safety monitoring
- **Safety Level**: Red (Crisis)

## FLIGHT State
- **Characteristics**: Anxious, scared, overwhelmed
- **Triggers**: "I'm scared", "anxious", "overwhelmed"
- **Response**: Comfort, support, crisis intervention
- **Safety Level**: Red (Crisis)

---

# Intensity Scoring

## Scale: 0.0 - 1.0

### Low Intensity (0.0 - 0.3)
- **Characteristics**: Subtle emotions, mild expressions
- **Examples**: "I'm okay", "not bad", "fine"
- **Response**: Gentle, supportive

### Medium Intensity (0.3 - 0.6)
- **Characteristics**: Moderate emotions, clear expressions
- **Examples**: "I'm happy", "excited", "interested"
- **Response**: Balanced engagement

---

# Intensity Scoring (Continued)

### High Intensity (0.6 - 0.8)
- **Characteristics**: Strong emotions, clear expressions
- **Examples**: "I'm so excited!", "really happy", "very interested"
- **Response**: Match energy, channel enthusiasm

### Extreme Intensity (0.8 - 1.0)
- **Characteristics**: Overwhelming emotions, urgent expressions
- **Examples**: "I'm freaking out!", "so overwhelmed", "can't handle it"
- **Response**: Crisis intervention, safety first

---

# LLM Prompt Engineering

## Gemini Pro Prompt Structure
```
You are an expert emotional intelligence analyzer. 
Analyze the user's message for emotional state and energy level.

User Message: "{user_message}"
Conversation Context: {recent_messages}

Provide analysis in JSON format:
{
  "energy_level": "LOW|MEDIUM|HIGH|INTENSE",
  "emotion_state": "HAPPY|SAD|EXCITED|LOVING|NEUTRAL",
  "intensity_score": 0.0-1.0,
  "nervous_system_state": "REST|ACTIVATED|FIGHT|FLIGHT",
  "confidence": 0.0-1.0,
  "reasoning": "explanation"
}
```

---

# Fallback Mechanism

## Rule-Based Analysis
When Gemini Pro fails, system uses keyword-based analysis:

### Energy Keywords
- **LOW**: tired, bored, disinterested, exhausted
- **HIGH**: excited, energetic, thrilled, pumped
- **INTENSE**: overwhelmed, freaking, can't handle

### Emotion Keywords
- **HAPPY**: happy, joy, excited, thrilled, great
- **SAD**: sad, depressed, down, upset, crying
- **LOVING**: love, adore, care, affection, sweet

### Safety Keywords
- **CRISIS**: help, emergency, crisis, suicide, self-harm

---

# Integration Points

## Input Sources
- **User Messages**: Direct text input
- **Conversation Context**: Recent message history
- **Session State**: Current conversation status
- **Energy History**: Previous energy assessments

## Output Destinations
- **Safety Monitor**: Risk assessment input
- **Girlfriend Agent**: Response generation context
- **Script Manager**: Scenario selection criteria
- **Frontend**: Energy indicator display

---

# Performance Metrics

## Response Time
- **Target**: < 2 seconds per analysis
- **Gemini Pro**: ~1.5 seconds average
- **Fallback**: < 0.1 seconds
- **Caching**: Repeated patterns cached

## Accuracy Metrics
- **Confidence Scoring**: 0.0 - 1.0 scale
- **Fallback Triggers**: LLM failure detection
- **Error Handling**: Graceful degradation
- **Monitoring**: Real-time performance tracking

---

# Error Handling

## LLM Failures
- **Timeout**: 10-second limit
- **API Errors**: Network issues, rate limits
- **Invalid Responses**: Malformed JSON
- **Fallback Activation**: Automatic rule-based analysis

## Data Validation
- **JSON Parsing**: Robust error handling
- **Range Validation**: Score bounds checking
- **Type Validation**: Expected data types
- **Sanitization**: Input cleaning

---

# Debugging & Monitoring

## Console Output
```
🔋 Energy Analysis: HIGH energy detected
🔋 Emotion: EXCITED (intensity: 0.75)
🔋 Nervous System: ACTIVATED
🔋 Confidence: 0.85
🔋 Reasoning: User shows clear excitement indicators
```

## Performance Tracking
- **Analysis Count**: Total analyses performed
- **Success Rate**: LLM vs fallback usage
- **Average Response Time**: Performance metrics
- **Error Rate**: Failure frequency

---

# Configuration Options

## Model Settings
- **Temperature**: 0.1 (consistent analysis)
- **Max Tokens**: 500 (sufficient for analysis)
- **Timeout**: 10 seconds
- **Retry Attempts**: 3 attempts

## Fallback Thresholds
- **Confidence Minimum**: 0.7
- **Error Threshold**: 3 consecutive failures
- **Fallback Duration**: 5 minutes
- **Recovery Attempts**: Every 30 seconds

---

# Future Enhancements

## Planned Features
- **Multi-language Support**: International emotional analysis
- **Voice Analysis**: Tone and pitch detection
- **Historical Patterns**: Long-term emotional trends
- **Personalization**: User-specific emotional baselines

## Advanced Capabilities
- **Micro-expressions**: Subtle emotional indicators
- **Context Awareness**: Situational emotional understanding
- **Predictive Analysis**: Emotional state forecasting
- **Integration**: External emotional data sources

---

# Best Practices

## Prompt Optimization
- **Clear Instructions**: Specific analysis requirements
- **Context Provision**: Relevant conversation history
- **Format Specification**: Structured JSON output
- **Example Cases**: Sample analyses for guidance

## Error Prevention
- **Input Validation**: Message sanitization
- **Timeout Management**: Reasonable limits
- **Fallback Testing**: Regular rule-based validation
- **Monitoring**: Continuous performance tracking

---

# Conclusion

## Key Strengths
✅ **Real-time Analysis**: Immediate emotional assessment
✅ **High Accuracy**: Gemini Pro-powered intelligence
✅ **Robust Fallback**: Rule-based reliability
✅ **Comprehensive Metrics**: Detailed energy profiling
✅ **Safety Integration**: Crisis detection capability

## Impact on System
- **Personalized Responses**: Energy-aware conversations
- **Safety Enhancement**: Emotional distress detection
- **Script Selection**: Appropriate scenario triggering
- **User Experience**: Emotionally intelligent interactions

---

# Questions & Discussion

**Energy Analyzer Deep Dive Complete!**

*Ready for the next component: Safety Monitor?*
