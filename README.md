# SLAM Mapping & Localization

## Project Overview

This project demonstrates a full SLAM Toolbox workflow on `turtlebot3_world` in ROS 2 Jazzy:

1. **Mapping** — build a live occupancy grid map using SLAM Toolbox's async mapping mode while driving the robot.
2. **Localization** — reload the saved map and serialized pose graph, then localize the robot within it using RViz's 2D Pose Estimate tool.

## Package Structure

```
slam_toolbox_demo/
├── config/
│   ├── mapping.yaml
│   └── localization.yaml
├── launch/
│   ├── mapping.launch.py
│   └── localization.launch.py
├── map/
│   └── turtlebot3_world_map.yaml / .pgm
├── posegraph/
│   └── turtlebot3_world_posegraph.posegraph / .data
├── CMakeLists.txt
├── package.xml
└── README.md
```

## Setup

### 1. Create/clone workspace

```bash
cd ~/ros2_ws/src
git clone https://github.com/yassinnmhmoudd/slam-toolbox-demo-yassin-bassem.git slam_toolbox_demo
```

### 2. Install dependencies

```bash
sudo apt update
sudo apt install ros-jazzy-slam-toolbox ros-jazzy-turtlebot3* ros-jazzy-nav2-map-server ros-jazzy-turtlebot3-teleop
```

Set the TurtleBot3 model (required by `turtlebot3_gazebo`):

```bash
echo 'export TURTLEBOT3_MODEL=burger' >> ~/.bashrc
source ~/.bashrc
```

### 3. Build and source

```bash
cd ~/ros2_ws
colcon build --packages-select slam_toolbox_demo
source install/setup.bash
```

## Mapping

### 1. Launch simulation and SLAM

```bash
ros2 launch slam_toolbox_demo mapping.launch.py
```

This launches `turtlebot3_world` in Gazebo, `robot_state_publisher`, and `async_slam_toolbox_node` in mapping mode.

`slam_toolbox` runs as a lifecycle node. The launch file automatically transitions it through `configure` → `activate` a few seconds after startup. If it doesn't activate automatically, trigger it manually:

```bash
ros2 lifecycle set /slam_toolbox configure
ros2 lifecycle set /slam_toolbox activate
```

### 2. Launch teleop

```bash
ros2 run turtlebot3_teleop teleop_keyboard
```

If keyboard teleop isn't available in your environment, publish directly to `/cmd_vel`:

```bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.1, y: 0.0, z: 0.0}, angular: {z: 0.0}}" --rate 5
```

Drive slowly, cover the whole world, and cross your own path at least once so SLAM Toolbox can perform loop closure.

### 3. Configure RViz

Open RViz2 and set:

- Fixed Frame → `map`
- Add displays: `RobotModel`, `LaserScan` (`/scan`), `Map` (`/map`)

Watch the occupancy grid build live as you drive.

### 4. Save the map

```bash
ros2 run nav2_map_server map_saver_cli -f ~/ros2_ws/src/slam_toolbox_demo/map/turtlebot3_world_map
```

### 5. Serialize the pose graph

```bash
ros2 service call /slam_toolbox/serialize_map slam_toolbox/srv/SerializePoseGraph \
  "{filename: '/ABSOLUTE/PATH/TO/slam_toolbox_demo/posegraph/turtlebot3_world_posegraph'}"
```

Rebuild so the saved map/posegraph get installed:

```bash
cd ~/ros2_ws
colcon build --packages-select slam_toolbox_demo
source install/setup.bash
```

## Localization

### 1. Launch localization

```bash
ros2 launch slam_toolbox_demo localization.launch.py
```

This loads the saved pose graph and runs `slam_toolbox` in localization mode. As with mapping, the lifecycle node activates automatically a few seconds after launch (or manually via `configure`/`activate` if needed).

In RViz2, add the `Map` display (`/map`) — the saved map should load immediately.

### 2. Set a wrong initial pose

Use **2D Pose Estimate** and click a deliberately wrong location/orientation. Observe the laser scan failing to align with the map's walls.

### 3. Set the correct pose

Use **2D Pose Estimate** again with the robot's actual position and heading. Observe the laser scan snapping into alignment with the map.

### 4. Drive and verify localization

Drive the robot around and confirm the map stays fixed in place — only the robot's pose/TF updates as it moves, and the laser scan continues tracking the map's walls correctly.

## Expected Results

- **Mapping:** a live occupancy grid builds in RViz as the robot explores `turtlebot3_world`, with walls and obstacles becoming clearly defined and no major misalignment after loop closure.
- **Localization:** the previously saved map loads instantly on launch. An incorrect pose estimate visibly mismatches the laser scan against the map; a correct estimate aligns them. As the robot drives, the map remains static while the robot's estimated pose tracks its movement correctly.

**Notes:**
- `slam_toolbox` is a lifecycle node in current versions — it will not subscribe to `/scan` or publish `/map` until it is `configured` and `activated`.
- `use_sim_time: true` must be set for `slam_toolbox` when running in Gazebo, or timestamps between simulation time and wall-clock time will mismatch and scans will be silently dropped.
- The `map_file_name` parameter for localization is injected at launch time (via `get_package_share_directory`) rather than hardcoded in `localization.yaml`, so the package stays portable across machines/users.

## Screenshots and Demo

**Mapping:**

<img width="758" height="381" alt="Localization demo" src="https://github.com/user-attachments/assets/991eb50e-3f06-409d-9c55-ed4cf2742a71" />

<img width="1365" height="588" alt="Screenshot 2026-09-12 001715" src="https://github.com/user-attachments/assets/7fd13593-a363-4915-8416-8d1eeed95818" />

**Localization**:


https://github.com/user-attachments/assets/04a3740b-864c-4a14-a4e7-7a282c1371a7







