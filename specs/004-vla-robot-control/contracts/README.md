# API Contracts: Vision-Language-Action (VLA) Robot Control

This directory contains the API contracts for the VLA system components that would be referenced in the documentation.

## Voice Processing API

### `/api/vla/voice/transcribe`
- **Method**: POST
- **Description**: Transcribes voice input to text using Whisper
- **Request**: Audio file or stream
- **Response**: Transcribed text with confidence score

### `/api/vla/voice/intent`
- **Method**: POST
- **Description**: Maps transcribed text to robot intent
- **Request**: Transcribed text
- **Response**: Robot intent with parameters

## LLM Planning API

### `/api/vla/llm/plan`
- **Method**: POST
- **Description**: Generates action sequence from natural language task
- **Request**: Natural language task description
- **Response**: Validated action sequence with safety checks

## ROS 2 Action API

### `/api/vla/ros2/execute`
- **Method**: POST
- **Description**: Executes action sequence on robot
- **Request**: Action sequence with parameters
- **Response**: Execution result with success/failure status

## Simulation API

### `/api/vla/sim/validate`
- **Method**: POST
- **Description**: Validates action sequence in simulation before execution
- **Request**: Action sequence
- **Response**: Validation results with safety assessment