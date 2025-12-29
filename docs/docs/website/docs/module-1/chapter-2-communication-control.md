---
sidebar_position: 2
title: "Chapter 2: Communication & Control"
---

# Chapter 2: Communication & Control

## Node Lifecycle and Execution

In ROS 2, nodes have a well-defined lifecycle that allows for better resource management and system coordination. The lifecycle includes several states:

- **Unconfigured**: The node is created but not yet configured
- **Inactive**: The node is configured but not executing
- **Active**: The node is actively running and executing callbacks
- **Finalized**: The node is shutting down and cleaning up resources

This lifecycle management allows for more robust systems where nodes can be started, stopped, and reconfigured dynamically without requiring a full system restart.

## Topics vs Services vs Actions (Use Cases)

### Topics (Publish-Subscribe)
- **Use Case**: Continuous data streams like sensor readings, robot pose, or camera images
- **Characteristics**: Asynchronous, many-to-many communication
- **Example**: Publishing laser scan data for obstacle detection

### Services (Request-Response)
- **Use Case**: Discrete operations with immediate results like saving a map or changing a parameter
- **Characteristics**: Synchronous, one-to-one communication
- **Example**: Requesting a path plan from a navigation system

### Actions (Long-Running Tasks)
- **Use Case**: Operations that take time to complete like navigation or manipulation
- **Characteristics**: Support for feedback, goals, and cancellation
- **Example**: Sending a robot to a specific location with progress feedback

## QoS (Quality of Service) Basics

Quality of Service settings in ROS 2 allow you to fine-tune communication behavior to match your application's requirements:

- **Reliability**: Choose between reliable (all messages delivered) or best-effort (faster but may lose messages)
- **Durability**: Determine if late-joining subscribers get previous messages
- **History**: Control how many messages to store
- **Deadline**: Specify timing requirements for message delivery

These settings are crucial for real-time systems where timing and reliability requirements vary between different data streams.

## Data Flow from Perception to Actuation

The typical data flow in a robotic system follows this pattern:

1. **Perception**: Sensors collect data from the environment
2. **Processing**: Algorithms interpret sensor data to understand the world
3. **Decision**: Planning algorithms determine appropriate actions
4. **Actuation**: Commands are sent to robot hardware to execute actions
5. **Feedback**: Sensors confirm the results of actions

This flow is coordinated through ROS 2's communication infrastructure, with different QoS settings applied based on the criticality and timing requirements of each data stream.

## Summary

This chapter explored the different communication patterns in ROS 2 and how they're used in robotic systems. In the [next chapter](./chapter-3-python-agents-robot-description.md), we'll look at how to integrate Python-based AI agents with ROS 2 and work with robot descriptions.