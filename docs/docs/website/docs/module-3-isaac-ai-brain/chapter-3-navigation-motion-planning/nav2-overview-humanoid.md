---
title: "Nav2 Overview for Humanoid Robots"
---

# Nav2 Overview for Humanoid Robots

## Introduction

Navigation Stack 2 (Nav2) is ROS 2's navigation framework for path planning and obstacle avoidance. For humanoid robots, Nav2 requires specialized configurations to account for bipedal locomotion patterns, balance requirements, and human-scale navigation challenges. This section provides an overview of Nav2 concepts specifically tailored for humanoid robot applications.

## Core Concepts

### Navigation Architecture
Nav2 follows a layered architecture that enables safe and efficient navigation:

- **Global Planner**: Path planning across the full map
- **Local Planner**: Short-term path following and obstacle avoidance
- **Controller**: Robot motion control and trajectory execution
- **Recovery**: Behavior when navigation fails or gets stuck

### Humanoid-Specific Considerations
Humanoid robots have unique navigation requirements:

- **Bipedal Locomotion**: Different kinematics from wheeled robots
- **Balance Constraints**: Need to maintain center of gravity
- **Step Planning**: Ability to step over obstacles or navigate stairs
- **Human-Scale Navigation**: Operating in human environments and spaces

## Nav2 Components

### Global Planner
The global planner computes a path from the robot's current position to the goal:

- **A* Algorithm**: Standard path planning algorithm
- **Dijkstra**: Alternative path planning algorithm
- **Custom Planners**: Humanoid-specific path planning approaches

### Local Planner
The local planner executes the global plan while avoiding obstacles:

- **Teb Local Planner**: Time-elastic band for smooth navigation
- **DWB Local Planner**: Dynamic window approach for obstacle avoidance
- **Humanoid-Specific Planners**: Custom planners for bipedal locomotion

### Controllers
Controllers manage the robot's motion execution:

- **Follow the Gap**: Simple obstacle avoidance controller
- **Pure Pursuit**: Path following controller
- **Humanoid Controllers**: Custom controllers for bipedal robots

### Recovery Behaviors
Recovery behaviors handle navigation failures:

- **Clear Costmap**: Clear temporary obstacles
- **Rotate Recovery**: Rotate to clear local minima
- **Back Up Recovery**: Move backward to find better path
- **Humanoid Recovery**: Custom behaviors for humanoid robots

## Implementation in Nav2

### Launch Configuration
```bash
# Launch Nav2 with humanoid-specific parameters
ros2 launch nav2_bringup navigation_launch.py \
  use_sim_time:=True \
  params_file:=/path/to/humanoid_nav2_params.yaml

# Launch with specific planners
ros2 launch nav2_bringup navigation_launch.py \
  autostart:=True \
  use_composition:=False \
  use_respawn:=False
```

### Parameter Configuration
Humanoid robots require specialized Nav2 parameters:

```yaml
bt_navigator:
  ros__parameters:
    use_sim_time: True
    global_frame: map
    robot_base_frame: base_link
    odom_topic: /odom
    bt_loop_duration: 10
    default_server_timeout: 20
    enable_groot_monitoring: True
    groot_zmq_publisher_port: 1666
    groot_zmq_server_port: 1667
    # Specify the path where the BT XML files are located
    default_nav_through_poses_bt_xml: "navigate_w_replanning_and_recovery.xml"
    default_nav_to_pose_bt_xml: "navigate_w_replanning_and_recovery.xml"
    # Recovery nodes
    node_names: ["navigate_to_pose", "navigate_through_poses"]

controller_server:
  ros__parameters:
    use_sim_time: True
    controller_frequency: 20.0
    min_x_velocity_threshold: 0.001
    min_y_velocity_threshold: 0.5
    min_theta_velocity_threshold: 0.001
    # Humanoid-specific controller
    HumanoidController:
      plugin: "nav2_rotation_shim_controller::RotationShimController"
    progress_checker_plugin: "progress_checker"
    goal_checker_plugin: "goal_checker"
    controller_plugins: ["HumanoidController"]

    # Humanoid Controller parameters
    HumanoidController:
      plugin: "nav2_rotation_shim_controller::RotationShimController"
      # Bipedal-specific parameters
      max_linear_speed: 0.5  # m/s
      max_angular_speed: 0.7  # rad/s
      min_linear_speed: 0.1   # m/s
      min_angular_speed: 0.1  # rad/s

local_costmap:
  local_costmap:
    ros__parameters:
      update_frequency: 5.0
      publish_frequency: 2.0
      global_frame: odom
      robot_base_frame: base_link
      use_rollout_costs: true
      lethal_cost_threshold: 100
      # Humanoid-specific costmap parameters
      footprint: "[[-0.3, -0.2], [-0.3, 0.2], [0.3, 0.2], [0.3, -0.2]]"
      resolution: 0.05
      robot_radius: 0.3
      track_unknown_space: false
      transform_tolerance: 0.5
      footprint_padding: 0.01

global_costmap:
  global_costmap:
    ros__parameters:
      update_frequency: 1.0
      publish_frequency: 0.5
      global_frame: map
      robot_base_frame: base_link
      use_resolution_map: false
      lethal_cost_threshold: 100
      # Humanoid-specific global costmap parameters
      footprint: "[[-0.3, -0.2], [-0.3, 0.2], [0.3, 0.2], [0.3, -0.2]]"
      resolution: 0.05
      robot_radius: 0.3
      track_unknown_space: false
      transform_tolerance: 0.5
      footprint_padding: 0.01

planner_server:
  ros__parameters:
    expected_planner_frequency: 20.0
    planner_plugins: ["GridBased"]
    GridBased:
      plugin: "nav2_navfn_planner/NavfnPlanner"
      tolerance: 0.5
      use_astar: false
      allow_unknown: true
```

## Practical Example: Humanoid Navigation

### Basic Navigation Node
```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient

class HumanoidNavigationNode(Node):
    def __init__(self):
        super().__init__('humanoid_navigation_node')

        # Action client for navigation
        self.nav_to_pose_client = ActionClient(
            self, NavigateToPose, 'navigate_to_pose')

        # Publish navigation goals
        self.nav_publisher = self.create_publisher(
            PoseStamped, 'goal_pose', 10)

        self.get_logger().info('Humanoid Navigation Node initialized')

    def send_navigation_goal(self, x, y, theta):
        """Send a navigation goal to Nav2"""
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = x
        goal_msg.pose.pose.position.y = y
        goal_msg.pose.pose.position.z = 0.0

        # Convert theta to quaternion
        import math
        goal_msg.pose.pose.orientation.z = math.sin(theta / 2.0)
        goal_msg.pose.pose.orientation.w = math.cos(theta / 2.0)

        # Wait for action server
        self.nav_to_pose_client.wait_for_server()

        # Send goal
        future = self.nav_to_pose_client.send_goal_async(goal_msg)
        future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        """Handle navigation goal response"""
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected')
            return

        self.get_logger().info('Goal accepted')
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        """Handle navigation result"""
        result = future.result().result
        self.get_logger().info(f'Navigation result: {result}')

def main(args=None):
    rclpy.init(args=args)
    node = HumanoidNavigationNode()

    # Example: Send navigation goal
    node.send_navigation_goal(1.0, 1.0, 0.0)

    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Humanoid-Specific Challenges

### Balance and Stability
Humanoid robots must maintain balance during navigation:

- **ZMP Planning**: Zero Moment Point for stable walking
- **Footstep Planning**: Planning where to place feet
- **Balance Recovery**: Recovery from balance disturbances
- **Stair Navigation**: Special handling for steps and stairs

### Environment Interaction
Humanoid robots operate in human environments:

- **Door Navigation**: Opening and passing through doors
- **Elevator Navigation**: Using elevators safely
- **Crowd Navigation**: Moving through crowds of people
- **Furniture Interaction**: Navigating around furniture

## Integration with Isaac ROS

### Perception Integration
Nav2 integrates with Isaac ROS perception:

- **Obstacle Detection**: Using Isaac ROS perception for obstacle detection
- **Map Building**: Using Isaac Sim for map building and localization
- **Sensor Fusion**: Combining multiple sensor inputs for navigation
- **Dynamic Obstacle Avoidance**: Handling moving obstacles

### Simulation Integration
Isaac Sim provides testing environments for navigation:

- **Simulation Testing**: Testing navigation in safe simulated environments
- **Scenario Generation**: Creating diverse navigation scenarios
- **Performance Validation**: Validating navigation performance
- **Safety Verification**: Ensuring navigation safety

```mdx-code-block
import IsaacDiagram from '@site/src/components/isaac-diagram/IsaacDiagram';

<div className="isaac-section">
  <IsaacDiagram
    title="Nav2 Architecture for Humanoid Robots"
    description="The navigation stack architecture adapted for humanoid robots"
    type="nav2"
  />
</div>
```

## Best Practices

### For Implementation
- Configure appropriate robot footprints for humanoid dimensions
- Tune velocity limits for humanoid locomotion
- Implement proper recovery behaviors for humanoid robots
- Test navigation in diverse environments

### For Safety
- Implement proper collision avoidance
- Validate navigation in human environments
- Ensure robot stability during navigation
- Monitor navigation performance continuously

### For Performance
- Optimize costmap parameters for humanoid robots
- Use appropriate planning algorithms for bipedal locomotion
- Implement efficient obstacle detection and avoidance
- Monitor and adjust navigation parameters dynamically

## Next Steps

In the next section, we'll explore path planning and obstacle avoidance algorithms specifically for humanoid robots.

## Assessment Questions

1. What are the key components of the Nav2 navigation stack?
2. How do humanoid robots differ from wheeled robots in navigation?
3. What are the main Nav2 parameters that need to be adjusted for humanoid robots?
4. Explain the difference between global and local planners in Nav2.
5. List three humanoid-specific navigation challenges and their solutions.