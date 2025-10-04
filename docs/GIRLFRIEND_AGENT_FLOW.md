# Girlfriend Agent LLM - Detailed Flow Documentation

## Overview
The Girlfriend Agent LLM (`girlfriend_agent.py`) is the primary conversational AI component that generates contextually appropriate responses with personality adaptation. It serves as the main interface between the user and the AI system, incorporating energy signatures, safety status, and conversation context.

## LLM Configuration
- **Primary Model**: `open-mistral-7b`
- **Fallback Models**: `mistral-small-latest`, `mistral-medium-latest`, `mistral-large-latest`
- **Provider**: Mistral AI
- **API Key**: `MISTRAL_API_KEY` environment variable

## Input Processing Flow

### 1. Message Reception
```
User Message → Girlfriend Agent LLM
    ↓
Context Integration (Energy + Safety + Conversation History)
    ↓
Personality Matrix Application
    ↓
Few-shot Example Selection
    ↓
Prompt Construction
```

### 2. Context Integration
- **Energy Signatures**: Current and historical energy data
- **Safety Status**: Current safety analysis results
- **Conversation History**: Recent message exchanges
- **Session Context**: Current session state and flags
- **User Preferences**: Individual user interaction patterns

### 3. Personality Matrix
The agent adapts personality based on:
- **Base Traits**: casual, natural, caring, playful, confident, authentic
- **Safety Responses**: green (casual), yellow (caring), red (supportive)
- **Energy Adaptation**: tone, pace, and approach based on user energy
- **Context Awareness**: situational personality adjustments

## Conversation Modes

### 1. Crisis Mode
**Triggers**: Safety status RED, crisis keywords detected
**Personality Traits**:
- Supportive and caring
- Professional and helpful
- Resource-focused
- Calming and grounding

**Response Characteristics**:
- Immediate support and validation
- Professional resource provision
- Calming and reassuring tone
- Crisis-appropriate language

### 2. Teasing Mode
**Triggers**: Teasing keywords, playful energy, safety status GREEN
**Personality Traits**:
- Playful and flirty
- Confident and teasing
- Non-explicit content
- Fun and engaging

**Response Characteristics**:
- Playful banter and teasing
- Confident and flirty tone
- Non-explicit sexual content
- Engaging and fun interactions

### 3. Sexual Mode
**Triggers**: Explicit sexual keywords, intimate energy, sexual script activation
**Personality Traits**:
- Dominant and instructional
- Confident and assertive
- Explicit content appropriate
- Intimate and personal

**Response Characteristics**:
- Direct and explicit content
- Dominant and instructional tone
- Intimate and personal language
- Sexual script integration

### 4. Emotional Mode
**Triggers**: Emotional keywords, caring energy, support requests
**Personality Traits**:
- Caring and supportive
- Empathetic and understanding
- Patient and gentle
- Emotionally intelligent

**Response Characteristics**:
- Empathetic and supportive responses
- Emotional validation and understanding
- Gentle and patient tone
- Care-focused interactions

### 5. Regular Mode
**Triggers**: Normal conversation, balanced energy, safety status GREEN
**Personality Traits**:
- Natural and authentic
- Casual and friendly
- Balanced and engaging
- Genuine and real

**Response Characteristics**:
- Natural conversation flow
- Casual and friendly tone
- Authentic personality expression
- Balanced interaction style

## Response Generation Flow

### 1. Context Building
```
Energy Signature → Personality Adaptation
    ↓
Safety Status → Response Mode Selection
    ↓
Conversation History → Context Integration
    ↓
Few-shot Examples → Response Style
    ↓
Prompt Construction → Mistral API Call
```

### 2. Few-shot Learning
The agent uses dataset examples for:
- **Response Style**: Appropriate response patterns
- **Personality Expression**: Natural personality traits
- **Context Adaptation**: Situational response examples
- **Quality Assurance**: High-quality response templates

### 3. Prompt Engineering
The LLM receives structured prompts containing:
- **System Instructions**: Role definition and personality guidelines
- **Context Data**: Energy, safety, and conversation history
- **Few-shot Examples**: Relevant response examples
- **Response Guidelines**: Mode-specific response instructions

## Output Processing Flow

### 1. LLM Response Processing
```
Mistral API Response → Response Validation
    ↓
Personality Consistency Check
    ↓
Safety Compliance Verification
    ↓
Energy Alignment Assessment
    ↓
Response Quality Evaluation
```

### 2. Response Validation
- **Content Appropriateness**: Ensures response matches context
- **Personality Consistency**: Verifies personality alignment
- **Safety Compliance**: Confirms safety guidelines adherence
- **Energy Alignment**: Checks energy compatibility

### 3. Response Enhancement
- **Tone Adjustment**: Fine-tunes response tone
- **Personality Injection**: Adds personality-specific elements
- **Context Integration**: Incorporates conversation context
- **Quality Optimization**: Enhances response quality

## Personality Adaptation Framework

### 1. Base Personality Traits
- **Casual**: Relaxed and informal communication style
- **Natural**: Authentic and genuine personality expression
- **Caring**: Empathetic and supportive nature
- **Playful**: Fun and engaging interaction style
- **Confident**: Self-assured and assertive communication
- **Authentic**: Genuine and real personality traits

### 2. Safety-Based Adaptation
- **Green Status**: Casual, playful, confident personality
- **Yellow Status**: Caring, supportive, cautious personality
- **Red Status**: Supportive, professional, crisis-focused personality

### 3. Energy-Based Adaptation
- **High Energy**: Energetic, enthusiastic, dynamic responses
- **Low Energy**: Calm, gentle, supportive responses
- **Intimate Energy**: Personal, close, intimate responses
- **Playful Energy**: Fun, teasing, engaging responses

## Integration Points

### 1. Upstream Components
- **Energy Analyzer**: Receives energy signatures for personality adaptation
- **Safety Monitor**: Gets safety status for response mode selection
- **Response Analyzer**: Uses quality analysis for response optimization
- **Enhanced Main**: Receives session context and flags

### 2. Downstream Components
- **Message Splitter**: Sends responses for streaming processing
- **API Server**: Provides responses for frontend delivery
- **Script Manager**: Integrates with scripted content
- **Frontend**: Delivers responses to user interface

### 3. Real-time Updates
- **Personality Indicators**: Live personality mode display
- **Response Quality**: Real-time response quality metrics
- **Mode Transitions**: Dynamic mode switching
- **Context Adaptation**: Continuous context integration

## Performance Characteristics

### 1. Response Times
- **Target**: <800ms for response generation
- **Fallback**: <200ms for fallback responses
- **Timeout**: 8 seconds maximum wait time

### 2. Quality Metrics
- **Personality Consistency**: 90%+ alignment with selected mode
- **Context Appropriateness**: 85%+ relevance to conversation
- **Safety Compliance**: 95%+ adherence to safety guidelines
- **User Satisfaction**: 80%+ user engagement correlation

### 3. Resource Usage
- **Token Consumption**: ~400-800 tokens per response
- **API Calls**: 1 primary + up to 3 fallback attempts
- **Memory**: Moderate state retention (conversation context)

## Special Features

### 1. Dynamic Personality Switching
- **Mode Transitions**: Seamless switching between conversation modes
- **Context Awareness**: Automatic mode selection based on context
- **User Adaptation**: Learning from user interaction preferences
- **Situational Awareness**: Appropriate mode for current situation

### 2. Energy-Aware Responses
- **Energy Matching**: Responses match user energy levels
- **Energy Progression**: Natural energy flow in conversations
- **Energy Adaptation**: Dynamic adjustment to energy changes
- **Energy Integration**: Seamless energy signature incorporation

### 3. Safety-Gated Responses
- **Safety Priority**: Safety concerns override personality preferences
- **Crisis Response**: Immediate crisis-appropriate responses
- **Support Mode**: Automatic supportive response generation
- **Intervention Integration**: Seamless crisis intervention

## Fallback Mechanisms

### 1. Response Fallbacks
When LLM fails, the system provides:
- **Generic Responses**: Safe, appropriate fallback responses
- **Mode-Specific Fallbacks**: Responses appropriate to current mode
- **Context-Aware Fallbacks**: Responses based on conversation context
- **Safety-First Fallbacks**: Responses prioritizing user safety

### 2. Error Handling Strategy
- **API Failures**: Fallback to pre-defined responses
- **Model Capacity**: Switch to alternative Mistral models
- **Network Issues**: Retry with exponential backoff
- **Invalid Responses**: Response validation and correction

## Monitoring & Metrics

### 1. Performance Tracking
- **Response Times**: Average and P95 latency
- **Success Rates**: LLM vs fallback usage
- **Mode Distribution**: Conversation mode usage patterns
- **Quality Metrics**: Response quality trends

### 2. Personality Metrics
- **Mode Effectiveness**: Success of different conversation modes
- **Personality Consistency**: Alignment with selected personality
- **User Engagement**: Correlation with user interaction
- **Context Adaptation**: Effectiveness of context integration

### 3. User Experience Metrics
- **Response Satisfaction**: User satisfaction with responses
- **Personality Preference**: User preference for different modes
- **Engagement Maintenance**: Ability to maintain user engagement
- **Conversation Quality**: Overall conversation quality improvement

---

**Document Version**: 1.0  
**Last Updated**: January 2025  
**Component**: Girlfriend Agent LLM (`girlfriend_agent.py`)
