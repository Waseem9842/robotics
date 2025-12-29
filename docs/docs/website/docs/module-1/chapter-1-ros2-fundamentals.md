---
sidebar_position: 1
title: "Chapter 1: ROS 2 Fundamentals"
---

# Chapter 1: ROS 2 Fundamentals

## Purpose of ROS 2 in Physical AI

ROS 2 (Robot Operating System 2) serves as the middleware that connects AI logic to humanoid robot bodies. It provides a communication framework that allows different components of a robot system to interact seamlessly, enabling the integration of perception, decision-making, and actuation systems.

In the context of Physical AI and humanoid robotics, ROS 2 provides the essential infrastructure that allows AI algorithms to interact with the physical world through robotic systems. It abstracts the complexity of hardware interfaces and communication protocols, allowing AI developers to focus on creating intelligent behaviors rather than managing low-level hardware details.

## ROS 2 vs ROS 1 (High Level)

ROS 2 was developed to address the limitations of the original ROS framework, particularly in areas of:

- **Quality of Service (QoS)**: ROS 2 provides more sophisticated message delivery guarantees
- **Security**: Built-in security features for communication between nodes
- **Real-time support**: Better real-time performance capabilities
- **Multi-robot systems**: Improved support for coordinating multiple robots
- **Deployment flexibility**: Can run on a wider variety of platforms and operating systems

## Core Concepts: Nodes, Topics, Services, Actions

### Nodes
Nodes are the fundamental execution units in ROS 2. Each node runs a specific task or function and can communicate with other nodes through the ROS 2 communication infrastructure. Nodes are typically implemented as processes that perform specific functions like sensor processing, control algorithms, or user interfaces.

### Topics
Topics enable asynchronous communication between nodes using a publish-subscribe model. Publishers send messages to topics, and subscribers receive messages from topics. This decouples nodes from each other, allowing for flexible system architectures.

### Services
Services provide synchronous request-response communication between nodes. A client sends a request to a service and waits for a response. This is useful for operations that require immediate feedback or have a clear start and end.

### Actions
Actions are for long-running tasks that may take significant time to complete. They provide feedback during execution, the ability to cancel tasks, and result reporting when tasks complete. Actions are ideal for navigation, manipulation, or other complex robot behaviors.

## ROS 2 as a Robotic Nervous System

Thinking of ROS 2 as a robotic nervous system provides an intuitive understanding of its role:

- **Sensory neurons** are like sensor nodes that collect information from the environment
- **Motor neurons** are like actuator nodes that control the robot's physical movements
- **Interneurons** are like processing nodes that interpret sensory data and make decisions
- **The brain** is like the AI algorithms that provide high-level intelligence and planning
- **The spinal cord** is like the ROS 2 communication infrastructure that connects all components

Just as the nervous system enables coordinated behavior in biological organisms, ROS 2 enables coordinated behavior in robotic systems by providing the communication infrastructure that allows all components to work together effectively.

## Summary

This chapter introduced the fundamental concepts of ROS 2 and its role in connecting AI logic to robot bodies. In the [next chapter](./chapter-2-communication-control.md), we'll explore communication patterns and control systems in more detail.