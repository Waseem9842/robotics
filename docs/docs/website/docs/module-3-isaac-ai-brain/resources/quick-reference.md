---
title: "Quick Reference: Isaac AI Robot Brain"
---

# Quick Reference: Isaac AI Robot Brain

## Common Isaac Sim Commands

### Launching Isaac Sim
```bash
# Launch Isaac Sim with a specific world
isaac sim /path/to/world.usd

# Launch Isaac Sim with default environment
isac sim
```

### Isaac Sim with ROS 2
```bash
# Launch Isaac Sim with ROS 2 bridge
ros2 launch isaac_ros_common isaac_sim.launch.py
```

## Common Isaac ROS Commands

### Isaac ROS Perception
```bash
# Launch Isaac ROS Visual SLAM
ros2 launch isaac_ros_visual_slam visual_slam.launch.py

# Launch Isaac ROS Image Pipeline
ros2 launch isaac_ros_image_pipeline image_pipeline.launch.py
```

### Isaac ROS Navigation
```bash
# Launch Isaac ROS Navigation
ros2 launch nav2_bringup isaac_nav.launch.py
```

## Isaac Sim Physics Parameters
- Gravity: `<gravity>0 0 -9.8</gravity>` (standard Earth gravity)
- Time step: 0.001s for accurate physics
- Update rate: 1000 Hz for physics, 100 Hz for sensors

## Isaac ROS Message Types
- `isaac_ros_interfaces/msg/IsaacPose`: Robot pose estimation
- `sensor_msgs/msg/Image`: Camera images
- `sensor_msgs/msg/LaserScan`: LiDAR data
- `nav_msgs/msg/Path`: Navigation path planning
- `geometry_msgs/msg/Twist`: Robot velocity commands

## Isaac Sim Coordinate Frames
- `base_link`: Robot base frame
- `odom`: Odometry frame (integrated motion)
- `map`: Global map frame
- `camera_link`: Camera optical frame
- `imu_link`: IMU sensor frame

## Performance Optimization
### Isaac Sim Performance
- Use simpler collision geometry than visual geometry
- Limit physics update rate to required accuracy
- Reduce visual quality for non-critical elements
- Use appropriate solver parameters

### Isaac ROS Performance
- Use hardware acceleration (GPU) for perception
- Optimize sensor data rates for processing capability
- Implement efficient sensor fusion algorithms

## Common Coordinate Conventions
- Isaac Sim uses right-handed coordinate system (X: forward, Y: left, Z: up)
- ROS 2 uses right-handed coordinate system (X: forward, Y: left, Z: up)
- Isaac ROS bridges maintain consistent frame conventions

## Isaac Sim-ROS 2 Integration
- Use `isaac_ros_common` package for ROS 2 bridge
- Configure appropriate topic names and types
- Monitor bandwidth usage for sensor data
- Validate time synchronization between systems