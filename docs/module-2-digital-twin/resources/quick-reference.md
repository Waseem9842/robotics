# Quick Reference: Digital Twin Simulation

## Common Gazebo Commands

### Launching Gazebo with ROS 2
```bash
# Launch Gazebo with a specific world
ros2 launch gazebo_ros empty_world.launch.py world:=/path/to/world.sdf

# Spawn a robot model
ros2 run gazebo_ros spawn_entity.py -entity my_robot -file /path/to/robot.urdf -x 0 -y 0 -z 1
```

### Common Physics Parameters
- Gravity: `<gravity>0 0 -9.8</gravity>` (standard Earth gravity)
- Time step: 0.001s for accurate physics
- Update rate: 1000 Hz for physics, 100 Hz for sensors

## Common Unity-ROS 2 Communication

### Basic Unity ROS Connection
```csharp
using Unity.Robotics.ROSTCPConnector;

public class UnityROSConnection : MonoBehaviour
{
    private RosConnection ros;

    void Start()
    {
        ros = RosConnection.GetOrCreateInstance();
        ros.RegisterPublisher<JointStateMsg>("joint_states");
    }
}
```

### Common Message Types
- `sensor_msgs/JointState`: Robot joint positions, velocities, efforts
- `sensor_msgs/LaserScan`: LiDAR data
- `sensor_msgs/Image`: Camera images
- `sensor_msgs/Imu`: Inertial measurement unit data
- `geometry_msgs/Twist`: Robot velocity commands

## Sensor Simulation Parameters

### LiDAR Configuration
```xml
<sensor name="lidar" type="ray">
  <ray>
    <scan>
      <horizontal>
        <samples>1080</samples>
        <resolution>1</resolution>
        <min_angle>-3.14159</min_angle>
        <max_angle>3.14159</max_angle>
      </horizontal>
    </scan>
    <range>
      <min>0.1</min>
      <max>30.0</max>
      <resolution>0.01</resolution>
    </range>
  </ray>
</sensor>
```

### Camera Configuration
```xml
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
      <far>10.0</far>
    </clip>
  </camera>
</sensor>
```

### IMU Configuration
```xml
<sensor name="imu" type="imu">
  <imu>
    <angular_velocity>
      <x>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>2e-4</stddev>
        </noise>
      </x>
    </angular_velocity>
    <linear_acceleration>
      <x>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>1.7e-2</stddev>
        </noise>
      </x>
    </linear_acceleration>
  </imu>
</sensor>
```

## Common Coordinate Frames

### ROS 2 TF Frames
- `base_link`: Robot base frame
- `odom`: Odometry frame (integrated motion)
- `map`: Global map frame
- `camera_link`: Camera optical frame
- `imu_link`: IMU sensor frame

### Unity Coordinate System
- X: Right
- Y: Up
- Z: Forward
- Conversion to ROS: ROS X=Unity X, ROS Y=Unity Z, ROS Z=Unity Y

## Performance Optimization

### Gazebo Performance
- Use simpler collision geometry than visual geometry
- Limit physics update rate to required accuracy
- Reduce visual quality for non-critical elements
- Use appropriate solver parameters

### Unity Performance
- Use Level of Detail (LOD) for complex models
- Implement occlusion culling
- Use GPU instancing for multiple similar objects
- Optimize lighting with baked illumination

## Debugging Common Issues

### Sensor Data Issues
- Check coordinate frame transformations
- Verify time synchronization
- Validate sensor mounting positions
- Confirm appropriate noise models

### Physics Simulation Issues
- Check mass and inertia properties
- Verify joint limits and constraints
- Adjust solver parameters if unstable
- Validate collision geometry

### ROS Communication Issues
- Confirm network connectivity
- Check topic names and types
- Verify message publishing rates
- Monitor bandwidth usage