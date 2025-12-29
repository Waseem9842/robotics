---
title: "Integrating Gazebo with ROS 2"
---

# Integrating Gazebo with ROS 2

## Introduction

The integration between Gazebo and ROS 2 is fundamental to creating effective digital twins for robotics. This integration allows for realistic physics simulation combined with ROS 2's powerful middleware for robot communication, control, and perception.

## Gazebo ROS 2 Packages

The integration is facilitated by several key packages:

- **gazebo_ros_pkgs**: Provides ROS 2 interfaces for Gazebo
- **gazebo_ros2_control**: Bridges Gazebo and ros2_control
- **gazebo_plugins**: Various plugins for sensors and actuators

## Setting Up the Integration

### Launching Gazebo with ROS 2

A typical launch file to start Gazebo with ROS 2 integration:

```python
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    world_path = PathJoinSubstitution([
        FindPackageShare('my_robot_gazebo'),
        'worlds',
        'my_world.sdf'
    ])

    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                FindPackageShare('gazebo_ros'),
                '/launch',
                '/gazebo.launch.py'
            ]),
            launch_arguments={
                'world': world_path
            }.items()
        ),
    ])
```

### Robot State Publisher

To publish robot state information:

```python
robot_state_publisher = Node(
    package='robot_state_publisher',
    executable='robot_state_publisher',
    output='screen',
    parameters=[{'use_sim_time': True}],
    arguments=[urdf_path]
)
```

## Controlling Robots in Gazebo

### Joint State Controller

```yaml
controller_manager:
  ros__parameters:
    update_rate: 100  # Hz

    joint_state_broadcaster:
      type: joint_state_broadcaster/JointStateBroadcaster

    velocity_controller:
      type: velocity_controllers/JointGroupVelocityController
```

### Spawning Robots

To spawn a robot in Gazebo:

```bash
ros2 run gazebo_ros spawn_entity.py -entity my_robot -file /path/to/robot.urdf -x 0 -y 0 -z 1
```

## Sensor Integration

Gazebo supports various sensor types that integrate seamlessly with ROS 2:

- **LIDAR**: `gazebo_ros_ray_sensor`
- **Cameras**: `gazebo_ros_camera`
- **IMU**: `gazebo_ros_imu_sensor`
- **Force/Torque**: `gazebo_ros_ft_sensor`

### Example Sensor Configuration

```xml
<gazebo reference="camera_link">
  <sensor name="camera" type="camera">
    <camera>
      <horizontal_fov>1.089</horizontal_fov>
      <image>
        <width>640</width>
        <height>480</height>
        <format>R8G8B8</format>
      </image>
      <clip>
        <near>0.1</near>
        <far>100</far>
      </clip>
    </camera>
    <plugin name="camera_controller" filename="libgazebo_ros_camera.so">
      <frame_name>camera_optical_frame</frame_name>
      <topic_name>image_raw</topic_name>
    </plugin>
  </sensor>
</gazebo>
```

## Best Practices

- Always use `use_sim_time: true` parameter for nodes in simulation
- Configure appropriate update rates for controllers
- Use ros2_control for hardware abstraction
- Implement proper error handling for simulation scenarios
- Test both simulation and real robot code paths

```mdx-code-block
import SimulationDiagram from '@site/src/components/simulation-diagram/SimulationDiagram';

<div className="simulation-section">
  <SimulationDiagram
    title="Gazebo-ROS2 Integration"
    description="How Gazebo and ROS 2 work together in digital twin simulation"
    type="gazebo"
  />
</div>
```

## Next Steps

In the final section of this chapter, we'll explore how to test humanoid robot movements safely using Gazebo simulation.

## Assessment Questions

1. What are the key packages that facilitate Gazebo-ROS 2 integration?
2. Why is it important to use `use_sim_time: true` parameter in simulation?
3. Describe the role of the robot state publisher in Gazebo-ROS 2 integration.
4. How do you spawn a robot model in Gazebo using ROS 2?
5. What are the main sensor types that can be integrated with ROS 2 in Gazebo?