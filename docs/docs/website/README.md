# ROS 2 Fundamentals for Physical AI

This educational website provides foundational knowledge about ROS 2 for AI/software students entering Physical AI and Humanoid Robotics. The site covers the core concepts of ROS 2 as the middleware that connects AI logic to humanoid robot bodies.

## Module 1: The Robotic Nervous System (ROS 2)

This module includes three chapters covering:
1. ROS 2 Fundamentals - Purpose of ROS 2 in physical AI, differences from ROS 1, and core concepts
2. Communication & Control - Node lifecycles, communication patterns, QoS basics, and data flow
3. Python Agents & Robot Description - Integrating Python AI agents with rclpy and URDF basics

## Installation

```bash
npm install
```

## Local Development

```bash
npm start
```

This command starts a local development server and opens up a browser window. Most changes are reflected live without having to restart the server.

## Build

```bash
npm run build
```

This command generates static content into the `build` directory and can be served using any static contents hosting service.

## Deployment

Using SSH:

```bash
USE_SSH=true npm run deploy
```

Not using SSH:

```bash
GIT_USER=<Your GitHub username> npm run deploy
```

If you are using GitHub pages for hosting, this command is a convenient way to build the website and push to the `gh-pages` branch.
