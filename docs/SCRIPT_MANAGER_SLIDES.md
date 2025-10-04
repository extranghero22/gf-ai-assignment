---
marp: true
theme: default
class: lead
paginate: true
backgroundColor: #fff
backgroundImage: url('https://marp.app/assets/hero-background.svg')
---

# Script Manager LLM
## Dynamic Scenario & Script Orchestration

**Mistral AI-Powered Script Management**

---

# Overview

## Purpose
- **Manage conversation scenarios** and script execution
- **Dynamic script selection** based on energy and context
- **Message grouping** for natural conversation flow
- **Scene-aware delivery** with appropriate backgrounds

## Model
- **Primary**: Mistral AI (7B/8x7B)
- **Input**: Energy signature + conversation context + user message
- **Output**: Selected scenario with structured messages
- **Features**: Trigger word matching, energy-based selection

---

# Core Functionality

## Script Selection Process
```
Energy Data + Context + User Message
    │
    ▼
┌─────────────────┐
│ Trigger Word    │ ──► Scenario Selection
│ Matching        │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ Energy-based    │ ──► Alternative Selection
│ Analysis        │     (if no triggers)
└─────────────────┘
```

## Output Structure
- **Selected Scenario**: Appropriate script type
- **Message Sequence**: Structured conversation flow
- **Scene Setting**: Background environment
- **Progress Tracking**: Script execution state

---

# Scenario Types

## Sexual Scenarios
1. **Room Intimacy**: Private bedroom setting (10 messages)
   - **Scene**: Room background
   - **Outfit Progression**: Casual → Pullshirt → Both revealed
   - **Trigger**: Sexual keywords, intimate energy

2. **Exhibitionism**: Public outdoor setting (10 messages)
   - **Scene**: Beach or park background
   - **Outfit Progression**: Buttoned coat → Open topless → Fully nude
   - **Trigger**: Public/outdoor sexual interest

---

# Scenario Types (Continued)

## Casual Scenarios
1. **Shopping Scenario**: Story-based casual conversation
   - **Scene**: Current background maintained
   - **Content**: Shopping story, daily life
   - **Trigger**: Story interest, casual topics

2. **Low Energy Scenario**: Comfort and support
   - **Scene**: Calm, comfortable setting
   - **Content**: Gentle support, rest
   - **Trigger**: Low energy, tiredness

---

# Scenario Types (Continued)

## Crisis Scenarios
1. **Crisis Support**: Immediate intervention
   - **Scene**: Safe park background
   - **Content**: Professional support, resources
   - **Trigger**: Crisis detection, distress

2. **Intimate Scenario**: Emotional connection
   - **Scene**: Intimate setting
   - **Content**: Deep emotional sharing
   - **Trigger**: High intimacy, loving energy

---

# Trigger Word System

## Sexual Triggers
- **Room**: bedroom, private, alone, intimate
- **Public**: outside, beach, park, public, exhibition
- **Action**: undress, naked, sexy, hot, desire

## Casual Triggers
- **Story**: tell me, story, what happened, interesting
- **Shopping**: buy, store, shopping, mall, clothes
- **Daily**: day, work, school, routine, normal

---

# Trigger Word System (Continued)

## Crisis Triggers
- **Emergency**: help, crisis, emergency, suicide
- **Distress**: sad, depressed, overwhelmed, can't cope
- **Support**: alone, nobody cares, abandoned

## Energy Triggers
- **High Energy**: excited, energetic, pumped, thrilled
- **Low Energy**: tired, exhausted, drained, worn out
- **Intimate**: love, care, affection, close, together

---

# Energy-Based Selection

## Crisis Detection (Highest Priority)
- **Condition**: SAD emotion + intensity > 0.8
- **Condition**: FIGHT/FLIGHT nervous system + intensity > 0.7
- **Selection**: Crisis support scenario
- **Priority**: Immediate intervention

## Low Energy Detection
- **Condition**: Energy level = LOW
- **Selection**: Low energy comfort scenario
- **Approach**: Gentle support, rest, comfort

---

# Energy-Based Selection (Continued)

## High Sexual Energy
- **Condition**: HIGH/INTENSE energy + EXCITED emotion + intensity > 0.7
- **Selection**: Room intimacy scenario (default sexual)
- **Approach**: Intimate, passionate interaction

## High Intimacy Energy
- **Condition**: LOVING emotion + intensity > 0.6 + conversation history > 5
- **Selection**: Intimate scenario
- **Approach**: Deep emotional connection

---

# Energy-Based Selection (Continued)

## Default Selection
- **Condition**: No specific energy patterns
- **Selection**: Shopping scenario (casual)
- **Approach**: Normal conversation flow

---

# Message Structure

## Single Messages
- **Format**: Simple string content
- **Delivery**: Immediate single response
- **Use Case**: Simple statements, questions

## Grouped Messages
- **Format**: Array of related messages
- **Delivery**: Sequential delivery with pauses
- **Use Case**: Complex scenarios, story progression

---

# Scene Management

## Background Selection
- **Room Scenarios**: Room background image
- **Beach Scenarios**: Beach background image
- **Park Scenarios**: Park background image
- **Default**: Current background maintained

## Scene Transitions
- **Smooth Changes**: Natural background transitions
- **Context Awareness**: Appropriate scene selection
- **User Comfort**: Non-jarring visual changes

---

# LLM Prompt Engineering

## Mistral AI Scenario Selection Prompt
```
You are an expert conversation scenario manager.
Select the most appropriate scenario based on user energy and context.

User Message: "{user_message}"
Energy Signature: {energy_data}
Conversation Context: {recent_messages}

Available Scenarios:
- room_intimacy_scenario: Private intimate setting
- exhibitionism_scenario: Public outdoor setting
- shopping_scenario: Casual story-based conversation
- low_energy_scenario: Comfort and support
- crisis_scenario: Emergency support and intervention
- intimate_scenario: Deep emotional connection

Select the most appropriate scenario and provide reasoning.
```

---

# Script Execution

## Message Delivery
1. **Scenario Selection**: Choose appropriate script
2. **Message Sequencing**: Deliver messages in order
3. **Progress Tracking**: Monitor script completion
4. **Scene Updates**: Update background as needed

## Progress Management
- **Index Tracking**: Current message position
- **Completion Detection**: Script end recognition
- **State Updates**: Script active/completed status
- **User Interaction**: Response to user input

---

# Integration Points

## Input Sources
- **Energy Analyzer**: Emotional state data
- **Safety Monitor**: Risk assessment
- **User Messages**: Direct input analysis
- **Conversation Context**: Historical data

## Output Destinations
- **Frontend**: Message delivery and scene updates
- **Character Sprite**: Outfit and expression changes
- **Background System**: Scene transitions
- **Session Management**: Script state tracking

---

# Performance Metrics

## Selection Accuracy
- **Trigger Matching**: Keyword detection accuracy
- **Energy Alignment**: Appropriate energy-based selection
- **Context Relevance**: Situational appropriateness
- **User Satisfaction**: Script engagement quality

## Execution Efficiency
- **Selection Speed**: < 1 second scenario selection
- **Message Delivery**: Smooth conversation flow
- **Scene Transitions**: Natural background changes
- **Progress Tracking**: Accurate state management

---

# Error Handling

## Selection Failures
- **No Triggers**: Default to casual scenario
- **Energy Confusion**: Conservative selection
- **Context Issues**: Fallback to safe options
- **Safety Priority**: Always prioritize user safety

## Execution Errors
- **Message Delivery**: Graceful error handling
- **Scene Updates**: Fallback to default
- **Progress Tracking**: State recovery
- **User Interaction**: Responsive error management

---

# Debugging & Monitoring

## Console Output
```
📖 Script Manager: Scenario selection
📖 Selected: room_intimacy_scenario
📖 Trigger: sexual keywords detected
📖 Energy Match: HIGH sexual energy
📖 Messages: 10 total messages
📖 Scene: room background
```

## Performance Tracking
- **Selection Count**: Total scenarios selected
- **Trigger Accuracy**: Keyword matching success
- **Energy Alignment**: Appropriate energy-based selection
- **User Engagement**: Script completion rates

---

# Configuration Options

## Model Settings
- **Temperature**: 0.3 (consistent scenario selection)
- **Max Tokens**: 300 (sufficient for selection)
- **Timeout**: 5 seconds
- **Retry Attempts**: 2 attempts

## Selection Thresholds
- **Trigger Confidence**: 0.7 minimum
- **Energy Threshold**: 0.6 for high energy
- **Crisis Priority**: Always highest priority
- **Default Fallback**: Casual scenario

---

# Script Customization

## Scenario Modification
- **Message Content**: Adjustable scenario messages
- **Scene Settings**: Customizable backgrounds
- **Trigger Words**: Configurable keyword sets
- **Energy Thresholds**: Adjustable selection criteria

## User Preferences
- **Script Preferences**: User-specific scenario selection
- **Content Adaptation**: Personalized message content
- **Scene Preferences**: Background customization
- **Trigger Sensitivity**: Adjustable detection thresholds

---

# Future Enhancements

## Planned Features
- **Dynamic Scripts**: User-generated scenarios
- **Multi-language**: International scenario support
- **Voice Integration**: Audio script delivery
- **Advanced Analytics**: User preference learning

## Advanced Capabilities
- **AI-Generated Scenarios**: Dynamic script creation
- **Personalization**: User-specific scenario adaptation
- **Learning System**: Continuous script improvement
- **Integration**: External scenario sources

---

# Best Practices

## Scenario Selection
- **Context Awareness**: Situational appropriateness
- **User Safety**: Always prioritize safety
- **Energy Matching**: Appropriate emotional responses
- **Natural Flow**: Smooth conversation progression

## Script Execution
- **Progress Tracking**: Accurate state management
- **User Interaction**: Responsive to user input
- **Scene Management**: Smooth visual transitions
- **Quality Assurance**: Consistent script delivery

---

# Conclusion

## Key Strengths
✅ **Dynamic Selection**: Energy and context-aware scenarios
✅ **Comprehensive Coverage**: Multiple scenario types
✅ **Scene Management**: Appropriate background selection
✅ **Progress Tracking**: Accurate script execution
✅ **Safety Integration**: Crisis-aware scenario selection

## Impact on System
- **User Experience**: Engaging, varied interactions
- **Conversation Flow**: Natural scenario progression
- **Visual Experience**: Appropriate scene transitions
- **System Coordination**: Seamless component integration

---

# Questions & Discussion

**Script Manager Deep Dive Complete!**

*All LLM Components Documented!*

**Ready for System Integration Overview?**
