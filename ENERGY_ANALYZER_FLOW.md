# Energy Analyzer LLM - Detailed Flow Documentation

## Overview
The Energy Analyzer LLM (`energy_analyzer.py`) is responsible for real-time emotional and energy analysis of user messages. It serves as the foundation for all other LLM components by providing energy signatures that inform conversation decisions.

## LLM Configuration
- **Primary Model**: `open-mistral-7b`
- **Fallback Models**: `mistral-small-latest`, `mistral-medium-latest`
- **Provider**: Mistral AI
- **API Key**: `MISTRAL_API_KEY` environment variable

## Input Processing Flow

### 1. Message Reception
```
User Message → Energy Analyzer LLM
    ↓
Input Validation & Preprocessing
    ↓
Context Building (Recent conversation history)
    ↓
Prompt Construction
```

### 2. Context Building
- **Recent Messages**: Last 3-5 conversation exchanges
- **Energy History**: Previous energy signatures for trend analysis
- **Crisis Keywords**: Priority detection for emergency situations
- **Sexual Content**: Normalization for girlfriend AI context

### 3. Prompt Engineering
The LLM receives a structured prompt containing:
- **System Instructions**: Role definition and analysis guidelines
- **Context Data**: Recent conversation history
- **Analysis Framework**: JSON structure requirements
- **Crisis Priority**: Emergency detection instructions

## Analysis Categories

### Energy Levels (5 Levels)
- **NONE**: No detectable energy
- **LOW**: Minimal emotional engagement
- **MEDIUM**: Moderate emotional presence
- **HIGH**: Strong emotional engagement
- **INTENSE**: Overwhelming emotional intensity

### Energy Types (5 Types)
- **COMBATIVE**: Confrontational or argumentative energy
- **COOPERATIVE**: Collaborative and helpful energy
- **NEUTRAL**: Balanced, non-emotional energy
- **PLAYFUL**: Light-hearted and fun energy
- **INTIMATE**: Romantic or sexual energy

### Emotion States (10 States)
- **HAPPY**: Joyful and positive emotions
- **SAD**: Melancholy or depressed feelings
- **ANGRY**: Frustrated or hostile emotions
- **ANXIOUS**: Worried or nervous feelings
- **JEALOUS**: Possessive or envious emotions
- **LOVING**: Affectionate and caring feelings
- **EXCITED**: Enthusiastic and energetic emotions
- **BORED**: Disinterested or unengaged feelings
- **CONFUSED**: Uncertain or puzzled emotions
- **GRATEFUL**: Appreciative and thankful feelings

### Nervous System States (5 States)
- **REST_AND_DIGEST**: Calm and relaxed state
- **FIGHT**: Aggressive or confrontational state
- **FLIGHT**: Avoidant or escape-oriented state
- **FREEZE**: Immobilized or paralyzed state
- **FAWN**: People-pleasing or submissive state

## Output Processing Flow

### 1. LLM Response Processing
```
Mistral API Response → JSON Parsing
    ↓
Data Validation & Sanitization
    ↓
Confidence Score Calculation
    ↓
Fallback Mechanism (if needed)
    ↓
Energy Signature Creation
```

### 2. Energy Signature Structure
```python
EnergySignature {
    energy_level: EnergyLevel,
    energy_type: EnergyType,
    dominant_emotion: Emotion,
    nervous_system_state: NervousSystemState,
    intensity_score: float (0.0-1.0),
    confidence_score: float (0.0-1.0),
    timestamp: float,
    analysis_metadata: dict
}
```

### 3. Confidence Scoring
- **High Confidence (0.8-1.0)**: Clear emotional indicators
- **Medium Confidence (0.5-0.8)**: Mixed or subtle signals
- **Low Confidence (0.0-0.5)**: Ambiguous or unclear emotions

## Fallback Mechanisms

### 1. Rule-Based Analysis
When LLM fails, the system uses:
- **Keyword Matching**: Predefined emotional keywords
- **Pattern Recognition**: Common emotional expressions
- **Context Clues**: Conversation history analysis
- **Default Values**: Safe fallback energy signatures

### 2. Error Handling
- **API Failures**: Automatic fallback to rule-based system
- **Model Capacity**: Switch to alternative Mistral models
- **Network Issues**: Retry with exponential backoff
- **Invalid Responses**: JSON parsing with error recovery

## Integration Points

### 1. Downstream Components
- **Safety Monitor**: Receives energy signatures for safety assessment
- **Response Analyzer**: Uses energy data for conversation quality analysis
- **Girlfriend Agent**: Adapts personality based on user energy
- **Script Manager**: Triggers scenarios based on energy patterns

### 2. Real-time Updates
- **Energy Flags**: Live energy status updates
- **Frontend Indicators**: Visual energy representation
- **Session Metrics**: Energy trend tracking
- **Crisis Alerts**: Emergency energy detection

## Performance Characteristics

### 1. Response Times
- **Target**: <500ms for energy analysis
- **Fallback**: <100ms for rule-based analysis
- **Timeout**: 5 seconds maximum wait time

### 2. Accuracy Metrics
- **High Confidence**: 85%+ accuracy on clear emotional signals
- **Medium Confidence**: 70%+ accuracy on mixed signals
- **Crisis Detection**: 95%+ accuracy on emergency situations

### 3. Resource Usage
- **Token Consumption**: ~200-400 tokens per analysis
- **API Calls**: 1 primary + up to 2 fallback attempts
- **Memory**: Minimal state retention (last 5 energy signatures)

## Special Features

### 1. Crisis Detection Priority
- **Immediate Processing**: Crisis keywords bypass normal flow
- **High Sensitivity**: Detects subtle distress signals
- **Context Awareness**: Considers conversation history
- **Emergency Protocols**: Triggers immediate safety responses

### 2. Sexual Content Normalization
- **Expected Context**: Recognizes girlfriend AI environment
- **Appropriate Analysis**: Treats sexual content as normal
- **Energy Classification**: Properly categorizes intimate energy
- **Safety Balance**: Maintains safety while allowing intimacy

### 3. Trend Analysis
- **Energy Trajectory**: Tracks emotional progression
- **Pattern Recognition**: Identifies recurring energy types
- **Predictive Analysis**: Anticipates energy changes
- **Historical Context**: Uses past energy for current analysis

## Error Scenarios & Recovery

### 1. Common Failure Modes
- **API Rate Limits**: Automatic model switching
- **Network Timeouts**: Retry with fallback models
- **Invalid JSON**: Parsing with error recovery
- **Model Unavailability**: Rule-based analysis

### 2. Recovery Strategies
- **Graceful Degradation**: Maintains functionality with reduced accuracy
- **Transparent Fallback**: Logs fallback usage for monitoring
- **User Continuity**: Ensures conversation flow continues
- **Data Integrity**: Preserves energy signature structure

## Monitoring & Metrics

### 1. Performance Tracking
- **Response Times**: Average and P95 latency
- **Success Rates**: LLM vs fallback usage
- **Accuracy Metrics**: Confidence score distributions
- **Error Rates**: Failure mode analysis

### 2. Quality Assurance
- **Energy Distribution**: Analysis of energy type patterns
- **Crisis Detection**: Emergency situation identification rates
- **User Satisfaction**: Correlation with conversation quality
- **System Health**: Overall component performance

---

**Document Version**: 1.0  
**Last Updated**: January 2025  
**Component**: Energy Analyzer LLM (`energy_analyzer.py`)
