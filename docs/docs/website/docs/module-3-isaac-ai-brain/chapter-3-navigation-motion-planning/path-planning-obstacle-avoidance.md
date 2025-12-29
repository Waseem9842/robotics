---
title: "Path Planning and Obstacle Avoidance"
---

# Path Planning and Obstacle Avoidance

## Introduction

Path planning and obstacle avoidance are fundamental capabilities for autonomous humanoid robots. These systems enable robots to navigate safely through complex environments while avoiding obstacles and maintaining balance. Isaac ROS and Nav2 provide sophisticated algorithms that leverage perception data to plan safe and efficient paths for humanoid robots.

## Core Concepts

### Path Planning Fundamentals
Path planning involves finding a collision-free path from the robot's current location to a goal location:

- **Global Path Planning**: Finding the optimal route across the entire map
- **Local Path Planning**: Adjusting the path in real-time to avoid obstacles
- **Trajectory Generation**: Creating smooth, executable motion paths
- **Dynamic Replanning**: Updating paths as the environment changes

### Obstacle Avoidance Strategies
Obstacle avoidance uses multiple strategies to handle static and dynamic obstacles:

- **Static Obstacle Avoidance**: Avoiding fixed obstacles in the environment
- **Dynamic Obstacle Avoidance**: Avoiding moving obstacles and people
- **Predictive Avoidance**: Predicting and avoiding future obstacle positions
- **Reactive Avoidance**: Immediate response to unexpected obstacles

## Path Planning Algorithms

### Global Planning
Global planners compute paths across the entire known map:

#### A* Algorithm
- **Advantages**: Optimal path finding with heuristics
- **Use Cases**: Static environments with known obstacles
- **Considerations**: Computationally intensive for large maps

#### Dijkstra's Algorithm
- **Advantages**: Guaranteed optimal path finding
- **Use Cases**: When optimality is critical
- **Considerations**: Higher computational cost than A*

#### Potential Field Methods
- **Advantages**: Smooth path generation
- **Use Cases**: Environments with many obstacles
- **Considerations**: Local minima problems

### Local Planning
Local planners adjust the global path to handle immediate obstacles:

#### Dynamic Window Approach (DWA)
- **Advantages**: Real-time obstacle avoidance
- **Use Cases**: Dynamic environments with moving obstacles
- **Considerations**: Requires accurate robot dynamics model

#### Time Elastic Band (TEB)
- **Advantages**: Smooth, time-optimal trajectories
- **Use Cases**: Environments requiring smooth motion
- **Considerations**: Higher computational requirements

#### Humanoid-Specific Planners
- **Footstep Planning**: For bipedal locomotion
- **ZMP-Based Planning**: For balance-aware navigation
- **Stair Navigation**: For multi-level environments

## Implementation in Nav2

### Configuration Parameters
```yaml
planner_server:
  ros__parameters:
    # Global planner parameters
    NavfnPlanner:
      plugin: "nav2_navfn_planner/NavfnPlanner"
      tolerance: 0.5  # How close to get to goal
      use_astar: false  # Use A* instead of Dijkstra
      allow_unknown: true  # Allow planning through unknown space

    # Local planner parameters
    TebLocalPlanner:
      plugin: "nav2_teb_local_planner::TebLocalPlanner"
      # Robot constraints
      max_vel_x: 0.5  # Max forward velocity (m/s)
      max_vel_x_backwards: 0.2  # Max backward velocity (m/s)
      max_vel_theta: 0.7  # Max angular velocity (rad/s)
      acc_lim_x: 2.5  # Max linear acceleration (m/s^2)
      acc_lim_theta: 3.2  # Max angular acceleration (rad/s^2)
      # Humanoid-specific parameters
      min_turning_radius: 0.3  # Minimum turning radius (m)
      wheelbase: 0.0  # Set to 0 for non-differential drive humanoid

    # Humanoid-specific local planner
    HumanoidLocalPlanner:
      plugin: "nav2_humanoid_local_planner::HumanoidLocalPlanner"
      # Bipedal locomotion constraints
      max_step_size: 0.3  # Maximum step size (m)
      step_height: 0.15  # Maximum step height (m)
      balance_margin: 0.1  # Balance margin (m)
```

### Launch Configuration
```bash
# Launch with specific path planning parameters
ros2 launch nav2_bringup navigation_launch.py \
  use_sim_time:=True \
  autostart:=True \
  default_bt_xml_filename:=navigate_w_replanning_and_recovery.xml

# Launch with custom planners
ros2 launch nav2_bringup navigation_launch.py \
  planner_plugin_name:=NavfnPlanner \
  controller_plugin_name:=HumanoidController
```

## Obstacle Avoidance Techniques

### Static Obstacle Handling
Static obstacles are handled through costmap representation:

```yaml
# Static layer parameters
static_layer:
  plugin: "nav2_costmap_2d::StaticLayer"
  map_topic: "/map"
  transform_tolerance: 0.5
  map_subscribe_transient_local: True

# Inflation layer parameters
inflation_layer:
  plugin: "nav2_costmap_2d::InflationLayer"
  cost_scaling_factor: 3.0  # How much to inflate costs
  inflation_radius: 0.55  # Radius of inflation (m)
  inflate_unknown: false  # Whether to inflate unknown space
  # Humanoid-specific inflation
  robot_radius: 0.3  # Robot radius for inflation (m)
```

### Dynamic Obstacle Handling
Dynamic obstacles require real-time detection and prediction:

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan, PointCloud2
from nav_msgs.msg import OccupancyGrid
from geometry_msgs.msg import Point

class HumanoidObstacleAvoider(Node):
    def __init__(self):
        super().__init__('humanoid_obstacle_avoider')

        # Subscribers for obstacle detection
        self.lidar_sub = self.create_subscription(
            LaserScan, '/scan', self.lidar_callback, 10)
        self.perception_sub = self.create_subscription(
            PointCloud2, '/perception/obstacles', self.obstacle_callback, 10)

        # Publisher for dynamic costmap updates
        self.dynamic_costmap_pub = self.create_publisher(
            OccupancyGrid, '/local_costmap/dynamic_obstacles', 10)

        self.get_logger().info('Humanoid Obstacle Avoider initialized')

    def lidar_callback(self, msg):
        """Process LIDAR data for obstacle detection"""
        # Process laser scan to detect obstacles
        obstacles = self.process_lidar_scan(msg)

        # Update dynamic costmap
        self.update_dynamic_costmap(obstacles)

    def obstacle_callback(self, msg):
        """Process perception data for dynamic obstacles"""
        # Process perception results for moving obstacles
        dynamic_obstacles = self.process_perception_data(msg)

        # Predict obstacle movement
        predicted_obstacles = self.predict_obstacle_movement(dynamic_obstacles)

        # Update navigation plan
        self.update_navigation_plan(predicted_obstacles)

    def process_lidar_scan(self, scan_msg):
        """Process LIDAR scan to detect obstacles"""
        obstacles = []
        for i, range_val in enumerate(scan_msg.ranges):
            if range_val < scan_msg.range_min or range_val > scan_msg.range_max:
                continue

            angle = scan_msg.angle_min + i * scan_msg.angle_increment
            x = range_val * math.cos(angle)
            y = range_val * math.sin(angle)

            if range_val < 1.0:  # Threshold for obstacle detection
                obstacles.append(Point(x=x, y=y, z=0.0))

        return obstacles

    def update_dynamic_costmap(self, obstacles):
        """Update dynamic costmap with detected obstacles"""
        # Create occupancy grid with obstacle information
        costmap = OccupancyGrid()
        costmap.header.stamp = self.get_clock().now().to_msg()
        costmap.header.frame_id = 'map'

        # Fill costmap with obstacle information
        # Implementation details...

        self.dynamic_costmap_pub.publish(costmap)

def main(args=None):
    rclpy.init(args=args)
    node = HumanoidObstacleAvoider()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Humanoid-Specific Navigation Challenges

### Bipedal Locomotion Constraints
Humanoid robots have unique navigation constraints:

- **Step Planning**: Planning where to place each foot
- **Balance Maintenance**: Keeping the robot stable during movement
- **Turning Radius**: Limited turning capabilities compared to wheeled robots
- **Obstacle Height**: Can step over low obstacles but not high ones

### Human-Scale Navigation
Humanoid robots operate in human environments:

- **Doorway Navigation**: Navigating through doorways
- **Furniture Avoidance**: Avoiding tables, chairs, and other furniture
- **Human Interaction**: Navigating around people safely
- **Stair Navigation**: Handling stairs and steps

## Integration with Isaac ROS Perception

### Perception-Based Navigation
Isaac ROS perception enhances navigation capabilities:

```python
class PerceptionBasedNavigator(Node):
    def __init__(self):
        super().__init__('perception_based_navigator')

        # Perception data subscribers
        self.detection_sub = self.create_subscription(
            Detection2DArray, '/perception/detections',
            self.detection_callback, 10)
        self.segmentation_sub = self.create_subscription(
            Image, '/perception/segmentation',
            self.segmentation_callback, 10)

        # Navigation action client
        self.nav_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

    def detection_callback(self, msg):
        """Process object detections for navigation"""
        for detection in msg.detections:
            if detection.results[0].hypothesis.class_id == 'person':
                # Handle person detection
                self.handle_person_obstacle(detection)
            elif detection.results[0].hypothesis.class_id == 'obstacle':
                # Handle general obstacle
                self.handle_static_obstacle(detection)

    def handle_person_obstacle(self, detection):
        """Handle person as dynamic obstacle"""
        # Predict person movement
        # Adjust navigation plan accordingly
        # Maintain safe distance from person
        pass
```

## Safety Considerations

### Collision Avoidance
Critical safety measures for navigation:

- **Minimum Safe Distance**: Maintain safe distance from obstacles
- **Emergency Stop**: Stop immediately when collision is imminent
- **Safe Velocity**: Limit speeds to allow for stopping
- **Redundant Sensors**: Multiple sensors for obstacle detection

### Human Safety
When navigating around humans:

- **Right of Way**: Yield to humans in shared spaces
- **Predictable Motion**: Use predictable navigation patterns
- **Safe Distance**: Maintain appropriate social distance
- **Emergency Protocols**: Stop immediately if humans are in danger

## Best Practices

### For Path Planning
- Use appropriate planning algorithms for your environment
- Configure parameters for humanoid-specific constraints
- Implement proper error handling and recovery
- Test with diverse obstacle configurations

### For Obstacle Avoidance
- Use multiple sensor modalities for robust detection
- Implement predictive algorithms for dynamic obstacles
- Configure appropriate safety margins
- Monitor system performance and adjust parameters

### For Safety
- Implement comprehensive emergency stop procedures
- Validate navigation in diverse environments
- Test with unexpected obstacle configurations
- Ensure proper human-robot interaction protocols

```mdx-code-block
import IsaacDiagram from '@site/src/components/isaac-diagram/IsaacDiagram';

<div className="isaac-section">
  <IsaacDiagram
    title="Path Planning and Obstacle Avoidance"
    description="Architecture of path planning and obstacle avoidance for humanoid robots"
    type="nav2"
  />
</div>
```

## Next Steps

In the next section, we'll explore how to coordinate perception and movement systems for effective navigation.

## Assessment Questions

1. What are the main differences between global and local path planning?
2. Explain how humanoid robots differ from wheeled robots in obstacle avoidance.
3. What are the key parameters to configure for humanoid-specific navigation?
4. How does perception data enhance navigation capabilities?
5. List three safety considerations for humanoid robot navigation.