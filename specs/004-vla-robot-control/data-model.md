# Data Model: Vision-Language-Action (VLA) Robot Control

## Entities

### VoiceCommand
- **Fields**:
  - id: string (unique identifier)
  - text: string (transcribed speech)
  - timestamp: datetime (when command was received)
  - confidence: float (speech recognition confidence)
  - audio_metadata: object (audio source, quality metrics)
- **Relationships**: Connected to RobotIntent
- **Validation**: Text must not be empty, confidence > 0.5

### RobotIntent
- **Fields**:
  - id: string (unique identifier)
  - command_type: string (navigation, manipulation, sensing, etc.)
  - parameters: object (specific parameters for the action)
  - extracted_entities: array (recognized objects, locations, etc.)
  - confidence: float (intent recognition confidence)
- **Relationships**: Connected to VoiceCommand and LLMPlan
- **Validation**: command_type must be from predefined list

### LLMPlan
- **Fields**:
  - id: string (unique identifier)
  - task_description: string (original natural language task)
  - action_sequence: array (ordered list of ROS 2 actions)
  - safety_flags: object (identified safety concerns)
  - status: string (pending, validated, executed, failed)
- **Relationships**: Connected to RobotIntent and ROS2Action
- **Validation**: action_sequence must be non-empty and valid

### ROS2Action
- **Fields**:
  - id: string (unique identifier)
  - action_type: string (type of ROS 2 action)
  - parameters: object (action-specific parameters)
  - target_robot: string (robot identifier)
  - priority: integer (execution priority)
  - timeout: integer (timeout in seconds)
- **Relationships**: Connected to LLMPlan
- **Validation**: action_type must match available ROS 2 actions

### VLAExecutionLog
- **Fields**:
  - id: string (unique identifier)
  - voice_command_id: string (reference to VoiceCommand)
  - intent_id: string (reference to RobotIntent)
  - plan_id: string (reference to LLMPlan)
  - action_results: array (results of executed actions)
  - execution_time: datetime (when execution started)
  - completion_time: datetime (when execution completed)
  - success: boolean (whether execution was successful)
  - errors: array (any errors encountered)
- **Relationships**: Connected to all other entities
- **Validation**: Must have valid references to other entities

## State Transitions

### VoiceCommand State Transitions
- `received` → `processing` → `transcribed` → `intent_mapped`
- Alternative: `received` → `processing` → `failed` (if speech recognition fails)

### LLMPlan State Transitions
- `created` → `validating` → `validated` → `executing` → `completed`
- Alternative: `created` → `validating` → `invalid` (if safety checks fail)

### ROS2Action State Transitions
- `planned` → `scheduled` → `executing` → `completed` | `failed`
- Alternative: `planned` → `rejected` (if safety validation fails)

## Validation Rules

### Voice Command Validation
- Minimum confidence threshold of 0.5 for speech recognition
- Command must contain actionable intent
- Audio quality must meet minimum standards

### Intent Mapping Validation
- Intent must map to valid ROS 2 action types
- Parameters must be within acceptable ranges
- Safety constraints must be satisfied

### LLM Plan Validation
- Action sequences must be executable in order
- Safety checks must pass before execution
- Resource availability must be confirmed

### Execution Validation
- Robot state must be appropriate for action
- Environment must be safe for action execution
- Action parameters must be valid for current context