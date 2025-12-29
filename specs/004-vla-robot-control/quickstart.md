# Quickstart: Vision-Language-Action (VLA) Robot Control

## Prerequisites

- ROS 2 Humble Hawksbill installed
- NVIDIA Isaac Sim (for simulation)
- Python 3.8+ with pip
- Node.js 18+ for Docusaurus documentation
- Docker (for containerized components)

## Setup Environment

### 1. Clone the Repository
```bash
git clone <repository-url>
cd robotics-documentation
```

### 2. Install ROS 2 Dependencies
```bash
# Source ROS 2 environment
source /opt/ros/humble/setup.bash

# Install Isaac ROS packages
sudo apt update
sudo apt install ros-humble-isaac-ros-common ros-humble-isaac-ros-perception
```

### 3. Set up Python Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install openai-whisper transformers torch
```

### 4. Install Docusaurus
```bash
npm install
```

## Running the VLA System

### 1. Start ROS 2 Environment
```bash
# Terminal 1: Start ROS 2 daemon
source /opt/ros/humble/setup.bash
ros2 daemon start

# Terminal 2: Launch Isaac Sim
isaac-sim
```

### 2. Launch VLA Components
```bash
# Terminal 3: Start voice processing node
source venv/bin/activate
python3 -m vla.voice_processor

# Terminal 4: Start LLM planning node
source venv/bin/activate
python3 -m vla.llm_planner
```

### 3. Build Documentation
```bash
npm run build
npm run start
```

## Example Usage

### Voice Command Processing
```python
from vla.voice_processor import VoiceProcessor

processor = VoiceProcessor()
command = processor.listen_for_command()
print(f"Recognized: {command.text}")
```

### LLM Task Planning
```python
from vla.llm_planner import LLMPlanner

planner = LLMPlanner()
plan = planner.create_plan("Navigate to the kitchen and pick up the red cup")
print(f"Generated plan: {plan.action_sequence}")
```

### ROS 2 Action Execution
```python
from vla.ros2_executor import ROS2Executor

executor = ROS2Executor()
result = executor.execute_plan(plan)
print(f"Execution result: {result.success}")
```

## Testing the System

### Unit Tests
```bash
# Python unit tests
python -m pytest tests/unit/

# JavaScript component tests
npm test
```

### Integration Tests
```bash
# End-to-end VLA pipeline test
python -m pytest tests/integration/test_vla_pipeline.py
```

## Documentation Structure

The VLA module documentation is organized as follows:

- **Chapter 1**: `docs/module-4-vla-robot-control/voice-to-action/` - Voice processing with Whisper
- **Chapter 2**: `docs/module-4-vla-robot-control/llm-planning/` - LLM-based task decomposition
- **Chapter 3**: `docs/module-4-vla-robot-control/capstone/` - End-to-end implementation

Each chapter contains multiple MDX files covering specific aspects of the VLA pipeline.