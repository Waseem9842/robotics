# Quickstart: Digital Twin Simulation Module

## Overview
This guide helps you get started with the Digital Twin Simulation module, covering physics-based simulation with Gazebo, high-fidelity environments with Unity, and sensor simulation.

## Prerequisites
- Basic ROS 2 knowledge
- Docusaurus development environment
- Gazebo simulation environment
- Unity 3D (for visual simulation content)
- Node.js 18+ for documentation

## Setup Instructions

### 1. Environment Setup
```bash
# Clone the repository
git clone <repository-url>
cd robotics

# Install Docusaurus dependencies
npm install

# Verify ROS 2 installation
source /opt/ros/humble/setup.bash  # or your ROS 2 distribution
```

### 2. Documentation Development Server
```bash
# Navigate to the documentation directory
cd /path/to/your/docusaurus/project

# Start the development server
npm start

# The documentation will be available at http://localhost:3000
```

### 3. Access Module Content
The Digital Twin Simulation module is organized into three main chapters:

#### Chapter 1: Physics-Based Simulation with Gazebo
- Navigate to: `/docs/module-2-digital-twin/chapter-1-gazebo-physics/`
- Learn about digital twins in Physical AI
- Understand gravity, collisions, and dynamics simulation
- Explore Gazebo-ROS 2 integration
- Practice safe humanoid movement testing

#### Chapter 2: High-Fidelity Environments with Unity
- Navigate to: `/docs/module-2-digital-twin/chapter-2-unity-environments/`
- Understand why Unity is used for human-robot interaction
- Learn the balance between visual realism and physics accuracy
- Explore conceptual ROS 2-Unity communication
- Review use cases for interaction and training

#### Chapter 3: Sensor Simulation
- Navigate to: `/docs/module-2-digital-twin/chapter-3-sensor-simulation/`
- Simulate LiDAR, depth cameras, and IMUs
- Understand sensor data pipelines in simulation
- Learn about noise, latency, and realism considerations
- Prepare simulated data for AI models

## Running Simulations
To practice with actual simulation environments:

### Gazebo Physics Simulation
```bash
# Source ROS 2
source /opt/ros/humble/setup.bash

# Launch a sample Gazebo environment
ros2 launch gazebo_ros empty_world.launch.py
```

### Unity Environment (Conceptual)
The module covers Unity integration concepts. For hands-on practice:
1. Install Unity Hub and Unity 3D
2. Import the ROS# package for ROS 2 communication
3. Follow the examples in Chapter 2

## Educational Objectives
By completing this module, you will:
- Understand the role of digital twins in Physical AI
- Be able to create physics-based simulations using Gazebo
- Understand the trade-offs between visual realism and physics accuracy
- Learn to simulate various sensor types with realistic characteristics
- Prepare simulated sensor data for AI model training

## Next Steps
1. Start with Chapter 1 to understand physics simulation fundamentals
2. Progress to Chapter 2 for visual simulation concepts
3. Complete Chapter 3 to master sensor simulation
4. Practice with the provided examples and exercises
5. Apply your knowledge to create your own digital twin simulations