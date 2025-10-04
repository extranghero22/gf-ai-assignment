# Script Manager LLM - Detailed Flow Documentation

## Overview
The Script Manager LLM (`enhanced_script_manager.py`) manages structured conversation scenarios and scripted interactions. It provides pre-defined conversation flows for specific situations while adapting content based on user energy and context.

## LLM Configuration
- **Content Type**: Pre-defined scripted scenarios
- **Adaptation Method**: Energy-aware message modification
- **Integration**: Works with Girlfriend Agent LLM
- **Trigger System**: Keyword and energy-based activation

## Input Processing Flow

### 1. Scenario Activation
```
Energy Detection → Script Manager LLM
    ↓
Trigger Word Matching
    ↓
Energy-Based Scenario Selection
    ↓
Context Analysis
    ↓
Script Execution
```

### 2. Trigger Detection
The system monitors for:
- **Energy Flags**: Specific energy patterns that trigger scenarios
- **Keyword Matching**: Pre-defined trigger words and phrases
- **Context Clues**: Conversation context that suggests scenario activation
- **User Behavior**: Patterns that indicate scenario appropriateness

### 3. Scenario Selection Process
- **Trigger Analysis**: Evaluates trigger word matches
- **Energy Assessment**: Considers current energy signatures
- **Context Evaluation**: Analyzes conversation context
- **Scenario Suitability**: Determines best scenario match

## Available Scenarios

### 1. Shopping Scenario
**Purpose**: Casual story sharing and everyday conversation
**Triggers**: 
- Shopping-related keywords: "shopping", "store", "buy", "mall"
- Casual conversation energy
- Story-sharing requests

**Content Structure**:
- **Message 1**: Introduction to shopping story
- **Message 2**: Story development and details
- **Message 3**: Story conclusion and user engagement
- **Message 4**: Transition to user's shopping experiences
- **Message 5**: Interactive discussion about shopping

**Energy Adaptation**:
- **High Energy**: Energetic and enthusiastic storytelling
- **Low Energy**: Gentle and calming story delivery
- **Playful Energy**: Fun and engaging story presentation
- **Intimate Energy**: Personal and close story sharing

### 2. Low Energy Scenario
**Purpose**: Gentle support for tired or low-energy users
**Triggers**:
- Low energy detection
- Tiredness indicators: "tired", "exhausted", "sleepy"
- Low engagement patterns

**Content Structure**:
- **Message 1**: Gentle acknowledgment of low energy
- **Message 2**: Supportive and caring response
- **Message 3**: Gentle encouragement and comfort
- **Message 4**: Calming and soothing interaction
- **Message 5**: Gentle transition to rest or comfort

**Energy Adaptation**:
- **Very Low Energy**: Extra gentle and calming responses
- **Moderate Low Energy**: Supportive with gentle encouragement
- **Recovering Energy**: Gradual energy building responses

### 3. Crisis Scenario
**Purpose**: Crisis support and intervention
**Triggers**:
- Crisis keywords: "help", "crisis", "emergency", "suicide"
- Safety status RED
- Distress indicators

**Content Structure**:
- **Message 1**: Immediate support and validation
- **Message 2**: Professional resource provision
- **Message 3**: Calming and grounding response
- **Message 4**: Ongoing support and encouragement
- **Message 5**: Professional guidance and resources

**Energy Adaptation**:
- **High Distress**: Extra calming and supportive responses
- **Moderate Crisis**: Balanced support and guidance
- **Recovery Phase**: Gentle encouragement and support

### 4. Intimate Scenario
**Purpose**: Deep emotional connection and intimacy
**Triggers**:
- Intimate energy detection
- Emotional connection keywords: "love", "care", "close", "intimate"
- High emotional engagement

**Content Structure**:
- **Message 1**: Emotional connection establishment
- **Message 2**: Deep emotional sharing
- **Message 3**: Intimate bonding and connection
- **Message 4**: Emotional validation and support
- **Message 5**: Deepening emotional intimacy

**Energy Adaptation**:
- **High Intimate Energy**: Deep and personal responses
- **Moderate Intimate Energy**: Warm and close responses
- **Building Intimacy**: Gradual intimacy development

### 5. Room Intimacy Scenario
**Purpose**: Private sexual experience (10 messages)
**Triggers**:
- Explicit sexual keywords
- Sexual script activation
- Room/bedroom location choice

**Content Structure**:
- **Messages 1-3**: Initial intimate setup and preparation
- **Messages 4-6**: Escalating intimacy and physical connection
- **Messages 7-9**: Peak intimate experience
- **Message 10**: Intimate conclusion and aftercare

**Energy Adaptation**:
- **High Sexual Energy**: Intense and passionate responses
- **Moderate Sexual Energy**: Balanced intimate responses
- **Building Sexual Energy**: Gradual escalation

### 6. Exhibitionism Scenario
**Purpose**: Public sexual experience (10 messages)
**Triggers**:
- Explicit sexual keywords
- Sexual script activation
- Public/outdoor location choice

**Content Structure**:
- **Messages 1-3**: Public setting establishment and initial exposure
- **Messages 4-6**: Escalating public intimacy and risk
- **Messages 7-9**: Peak public sexual experience
- **Message 10**: Public conclusion and aftercare

**Energy Adaptation**:
- **High Sexual Energy**: Intense and adventurous responses
- **Moderate Sexual Energy**: Balanced public intimate responses
- **Building Sexual Energy**: Gradual public escalation

## Script Execution Flow

### 1. Message Adaptation
```
Script Content → Energy Analysis
    ↓
Message Modification
    ↓
Context Integration
    ↓
Personality Application
    ↓
Response Generation
```

### 2. Energy-Based Adaptation
- **Energy Level**: Adjusts intensity based on user energy
- **Energy Type**: Modifies approach based on energy type
- **Energy Progression**: Adapts to energy changes during script
- **Energy Compatibility**: Ensures energy alignment

### 3. Context Integration
- **Conversation History**: Incorporates recent conversation context
- **User Preferences**: Adapts to individual user patterns
- **Session State**: Considers current session status
- **Safety Status**: Integrates safety considerations

## Progress Tracking

### 1. Script Progress Management
- **Message Counting**: Tracks progress through script messages
- **Completion Status**: Monitors script completion
- **Success Criteria**: Evaluates script success metrics
- **Transition Points**: Manages transitions between script phases

### 2. Success Metrics
- **User Engagement**: Measures user participation and interest
- **Energy Alignment**: Tracks energy compatibility throughout script
- **Response Quality**: Evaluates response appropriateness
- **Completion Rate**: Measures script completion success

### 3. Adaptation Tracking
- **Energy Changes**: Monitors energy changes during script
- **Context Shifts**: Tracks context changes
- **User Feedback**: Incorporates user response patterns
- **Script Effectiveness**: Measures script success

## Integration Points

### 1. Upstream Components
- **Energy Analyzer**: Receives energy signatures for script adaptation
- **Safety Monitor**: Gets safety status for script safety
- **Enhanced Main**: Receives session context and flags
- **Trigger System**: Gets activation signals

### 2. Downstream Components
- **Girlfriend Agent**: Integrates script content with personality
- **Message Splitter**: Sends script messages for streaming
- **API Server**: Provides script content for frontend delivery
- **Frontend**: Delivers script content to user interface

### 3. Real-time Updates
- **Script Progress**: Live script progress tracking
- **Energy Adaptation**: Real-time energy-based modifications
- **Context Integration**: Continuous context incorporation
- **Success Metrics**: Real-time success tracking

## Performance Characteristics

### 1. Response Times
- **Target**: <200ms for script content adaptation
- **Fallback**: <50ms for pre-defined responses
- **Timeout**: 2 seconds maximum wait time

### 2. Quality Metrics
- **Script Appropriateness**: 90%+ relevance to user context
- **Energy Alignment**: 85%+ energy compatibility
- **User Engagement**: 80%+ user participation
- **Completion Success**: 75%+ script completion rate

### 3. Resource Usage
- **Token Consumption**: ~100-200 tokens per adaptation
- **Memory**: Moderate state retention (script progress)
- **Processing**: Lightweight adaptation processing

## Special Features

### 1. Dynamic Script Adaptation
- **Real-time Modification**: Adapts script content based on user energy
- **Context Awareness**: Incorporates conversation context
- **User Personalization**: Adapts to individual user preferences
- **Situational Flexibility**: Adjusts to current situation

### 2. Energy-Aware Content
- **Energy Matching**: Script content matches user energy
- **Energy Progression**: Natural energy flow through script
- **Energy Adaptation**: Dynamic adjustment to energy changes
- **Energy Integration**: Seamless energy signature incorporation

### 3. Safety Integration
- **Safety Priority**: Safety concerns override script execution
- **Crisis Interruption**: Immediate script interruption for crises
- **Support Mode**: Automatic supportive script modification
- **Intervention Integration**: Seamless crisis intervention

## Fallback Mechanisms

### 1. Script Fallbacks
When adaptation fails, the system provides:
- **Pre-defined Responses**: Safe, appropriate script content
- **Generic Alternatives**: Fallback script options
- **Context-Aware Fallbacks**: Responses based on conversation context
- **Safety-First Fallbacks**: Responses prioritizing user safety

### 2. Error Handling Strategy
- **Adaptation Failures**: Fallback to original script content
- **Context Issues**: Use generic script adaptations
- **Energy Mismatches**: Default to moderate energy adaptation
- **Safety Concerns**: Immediate script interruption

## Monitoring & Metrics

### 1. Performance Tracking
- **Adaptation Times**: Average and P95 latency
- **Success Rates**: Script completion and success rates
- **Energy Alignment**: Energy compatibility tracking
- **User Engagement**: User participation metrics

### 2. Script Effectiveness
- **Completion Rates**: Script completion success
- **User Satisfaction**: User satisfaction with script content
- **Energy Compatibility**: Energy alignment effectiveness
- **Context Adaptation**: Context integration success

### 3. Quality Metrics
- **Content Appropriateness**: Script content relevance
- **Adaptation Quality**: Energy-based adaptation effectiveness
- **User Engagement**: User participation and interest
- **Script Success**: Overall script effectiveness

---

**Document Version**: 1.0  
**Last Updated**: January 2025  
**Component**: Script Manager LLM (`enhanced_script_manager.py`)
