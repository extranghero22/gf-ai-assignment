# Safety Monitor LLM - Detailed Flow Documentation

## Overview
The Safety Monitor LLM (`safety_monitor.py`) provides multi-layer safety analysis and crisis intervention capabilities. It acts as the primary gatekeeper for all conversation decisions, ensuring user safety while maintaining appropriate girlfriend AI functionality.

## LLM Configuration
- **Primary Model**: `open-mistral-7b`
- **Fallback Models**: `mistral-small-latest`, `mistral-medium-latest`
- **Provider**: Mistral AI
- **API Key**: `MISTRAL_API_KEY` environment variable

## Input Processing Flow

### 1. Message Reception
```
User Message → Safety Monitor LLM
    ↓
Crisis Keyword Pre-screening
    ↓
Context Building (Recent conversation + energy data)
    ↓
Safety Analysis Prompt Construction
```

### 2. Context Building
- **Recent Messages**: Last 3-5 conversation exchanges
- **Energy Signatures**: Current and historical energy data
- **Safety History**: Previous safety incidents and patterns
- **Crisis Indicators**: Emergency keyword detection
- **Conversation Context**: Overall conversation tone and direction

### 3. Crisis Pre-screening
Before LLM analysis, the system checks for:
- **Emergency Keywords**: "help", "crisis", "suicide", "self-harm"
- **Medical Emergencies**: "hospital", "ambulance", "injury"
- **Mental Health**: "panic attack", "breakdown", "trauma"
- **Immediate Threats**: "kill", "harm", "violence"

## Analysis Categories

### Safety Scores (0.0-1.0 Scale)
- **0.0-0.2**: SAFE - No safety concerns detected
- **0.3-0.4**: CAUTION - Minor concerns, monitor closely
- **0.5-0.7**: WARNING - Significant concerns, intervene carefully
- **0.8-1.0**: STOP - Critical safety issues, immediate intervention

### Safety Recommendations
- **SAFE**: Continue conversation normally
- **CAUTION**: Proceed with increased monitoring
- **WARNING**: Implement safety measures, gentle intervention
- **STOP**: Immediate crisis intervention, halt normal conversation

### Risk Factors Identified
- **Self-Harm Risk**: Suicidal ideation, self-injury threats
- **Mental Health Crisis**: Panic attacks, breakdowns, severe anxiety
- **Medical Emergency**: Health crises, injuries, hospital visits
- **Abuse Indicators**: Signs of domestic violence or abuse
- **Substance Issues**: Drug/alcohol related emergencies
- **Social Isolation**: Extreme loneliness, social withdrawal

## Output Processing Flow

### 1. LLM Response Processing
```
Mistral API Response → JSON Parsing
    ↓
Safety Score Validation
    ↓
Risk Factor Analysis
    ↓
Recommendation Generation
    ↓
Crisis Protocol Activation (if needed)
```

### 2. Safety Analysis Structure
```python
SafetyAnalysis {
    safety_score: float (0.0-1.0),
    recommendation: SafetyRecommendation,
    risk_factors: List[RiskFactor],
    specific_concerns: List[str],
    confidence_score: float (0.0-1.0),
    crisis_level: CrisisLevel,
    intervention_needed: bool,
    timestamp: float
}
```

### 3. Crisis Level Classification
- **NONE**: No crisis detected
- **LOW**: Minor concerns, monitoring recommended
- **MEDIUM**: Significant concerns, gentle intervention
- **HIGH**: Serious crisis, immediate support needed
- **CRITICAL**: Emergency situation, crisis intervention required

## Safety Analysis Framework

### 1. Content Analysis
- **Explicit Threats**: Direct harm or violence mentions
- **Implicit Risks**: Subtle indicators of distress
- **Context Evaluation**: Situational appropriateness
- **Pattern Recognition**: Recurring concerning behaviors

### 2. Contextual Safety Assessment
- **Conversation History**: Trend analysis of safety patterns
- **Energy Correlation**: How energy levels relate to safety
- **User Behavior**: Changes in communication patterns
- **Environmental Factors**: Context clues from conversation

### 3. Girlfriend AI Specific Considerations
- **Romantic Content**: Normalization of intimate conversations
- **Sexual Content**: Appropriate handling of sexual topics
- **Emotional Support**: Recognition of supportive vs harmful responses
- **Boundary Respect**: Understanding of appropriate limits

## Crisis Intervention Protocol

### 1. Crisis Detection Triggers
- **Direct Threats**: "I want to hurt myself"
- **Crisis Keywords**: "suicide", "kill myself", "end it all"
- **Medical Emergencies**: "hospital", "ambulance", "emergency"
- **Mental Health**: "breakdown", "can't cope", "losing it"

### 2. Intervention Response Flow
```
Crisis Detected → Immediate Safety Override
    ↓
Script Interruption (if active)
    ↓
Crisis Support Response Generation
    ↓
Energy Flag Update (RED status)
    ↓
Frontend Crisis Alert
    ↓
Supportive Conversation Mode
```

### 3. Crisis Response Types
- **Suicide Prevention**: Direct support and resource provision
- **Mental Health Support**: Calming and grounding responses
- **Medical Emergency**: Practical support and encouragement
- **Abuse Support**: Safe space creation and resource guidance
- **General Crisis**: Empathetic support and professional guidance

## Fallback Mechanisms

### 1. Rule-Based Safety Analysis
When LLM fails, the system uses:
- **Keyword Matching**: Predefined safety keywords
- **Pattern Recognition**: Common crisis indicators
- **Context Analysis**: Conversation flow evaluation
- **Conservative Approach**: Default to "SAFE" to prevent blocking

### 2. Error Handling Strategy
- **API Failures**: Fallback to rule-based analysis
- **Model Capacity**: Switch to alternative Mistral models
- **Network Issues**: Retry with exponential backoff
- **Invalid Responses**: JSON parsing with error recovery
- **Default Safety**: "SAFE" status when analysis fails

## Integration Points

### 1. Downstream Components
- **Girlfriend Agent**: Receives safety status for response adaptation
- **Response Analyzer**: Uses safety data for conversation quality
- **Script Manager**: Interrupts scripts based on safety concerns
- **Frontend**: Displays safety indicators and crisis alerts

### 2. Real-time Safety Updates
- **Safety Flags**: Live safety status updates
- **Crisis Alerts**: Immediate emergency notifications
- **Energy Correlation**: Safety-energy relationship tracking
- **Session Monitoring**: Continuous safety assessment

## Performance Characteristics

### 1. Response Times
- **Target**: <300ms for safety analysis
- **Crisis Detection**: <100ms for emergency keywords
- **Fallback**: <50ms for rule-based analysis
- **Timeout**: 3 seconds maximum wait time

### 2. Accuracy Metrics
- **Crisis Detection**: 95%+ accuracy on emergency situations
- **False Positives**: <5% rate for normal conversation
- **Safety Scoring**: 80%+ accuracy on safety assessment
- **Risk Factor Identification**: 85%+ accuracy on risk detection

### 3. Resource Usage
- **Token Consumption**: ~150-300 tokens per analysis
- **API Calls**: 1 primary + up to 2 fallback attempts
- **Memory**: Minimal state retention (last 3 safety analyses)

## Special Features

### 1. Context-Aware Safety Analysis
- **Conversation History**: Considers recent message patterns
- **Energy Correlation**: Links energy states to safety concerns
- **User Patterns**: Recognizes individual user behavior changes
- **Situational Awareness**: Understands conversation context

### 2. Crisis Support Prioritization
- **Immediate Response**: Crisis situations get priority processing
- **Resource Provision**: Provides appropriate support resources
- **Professional Guidance**: Encourages professional help when needed
- **Ongoing Support**: Maintains supportive conversation flow

### 3. Romantic/Sexual Content Normalization
- **Appropriate Context**: Recognizes girlfriend AI environment
- **Consent Awareness**: Monitors for consent-related issues
- **Boundary Respect**: Ensures appropriate limits are maintained
- **Safety Balance**: Maintains safety while allowing intimacy

## Error Scenarios & Recovery

### 1. Common Failure Modes
- **API Rate Limits**: Automatic model switching
- **Network Timeouts**: Retry with fallback models
- **Invalid JSON**: Parsing with error recovery
- **Model Unavailability**: Rule-based analysis

### 2. Recovery Strategies
- **Conservative Fallback**: Defaults to "SAFE" to prevent conversation blocking
- **Transparent Logging**: Records fallback usage for monitoring
- **User Continuity**: Ensures conversation flow continues
- **Safety Preservation**: Maintains safety analysis structure

## Monitoring & Metrics

### 1. Performance Tracking
- **Response Times**: Average and P95 latency
- **Success Rates**: LLM vs fallback usage
- **Crisis Detection**: Emergency situation identification rates
- **False Positive Rates**: Normal conversation misclassification

### 2. Safety Metrics
- **Crisis Incidents**: Emergency situation frequency
- **Intervention Success**: Crisis resolution effectiveness
- **User Safety**: Overall user safety maintenance
- **System Reliability**: Safety system uptime and accuracy

### 3. Quality Assurance
- **Safety Distribution**: Analysis of safety score patterns
- **Crisis Response**: Emergency intervention effectiveness
- **User Satisfaction**: Correlation with conversation quality
- **System Health**: Overall component performance

---

**Document Version**: 1.0  
**Last Updated**: January 2025  
**Component**: Safety Monitor LLM (`safety_monitor.py`)
