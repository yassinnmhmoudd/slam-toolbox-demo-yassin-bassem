SLAM Mapping & Localization — TurtleBot3 (turtlebot3_world)

This package implements a two-phase SLAM Toolbox workflow on the turtlebot3_world simulation in ROS 2 Jazzy:

Mapping — build a live occupancy grid map using SLAM Toolbox's async mapping mode while driving the robot with keyboard/topic teleop.
Localization — reload the saved map and serialized pose graph, then localize the robot within it using RViz's 2D Pose Estimate tool.
Package Structure
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
Setup Instructions
1. Clone into your ROS 2 Jazzy workspace
bash
cd ~/ros2_ws/src
git clone https://github.com/yassinnmhmoudd/slam-toolbox-demo-yassin-bassem.git slam_toolbox_demo
2. Install dependencies
bash
sudo apt update
sudo apt install ros-jazzy-slam-toolbox ros-jazzy-turtlebot3* ros-jazzy-nav2-map-server ros-jazzy-turtlebot3-teleop

Set the TurtleBot3 model (required by turtlebot3_gazebo):

bash
echo 'export TURTLEBOT3_MODEL=burger' >> ~/.bashrc
source ~/.bashrc
3. Build the package
bash
cd ~/ros2_ws
colcon build --packages-select slam_toolbox_demo
source install/setup.bash
How to Run
Mapping Phase
bash
ros2 launch slam_toolbox_demo mapping.launch.py

This launches:

turtlebot3_world in Gazebo
robot_state_publisher
async_slam_toolbox_node in mapping mode

slam_toolbox runs as a lifecycle node. This package's launch file automatically transitions it through configure → activate a few seconds after startup. If it doesn't activate automatically, trigger it manually:

bash
ros2 lifecycle set /slam_toolbox configure
ros2 lifecycle set /slam_toolbox activate

Drive the robot to explore the world:

bash
ros2 run turtlebot3_teleop teleop_keyboard

or, if keyboard teleop isn't available in your environment, publish directly to /cmd_vel:

bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.15, y: 0.0, z: 0.0}, angular: {z: 0.0}}" --rate 5

Open RViz2 and set:

Fixed Frame → map
Add displays: RobotModel, LaserScan (/scan), Map (/map)

Drive until the occupancy grid covers the whole world and at least one loop has been closed (revisit an already-mapped area) to correct drift.

Save the map:

bash
ros2 run nav2_map_server map_saver_cli -f ~/ros2_ws/src/slam_toolbox_demo/map/turtlebot3_world_map

Serialize the pose graph:

bash
ros2 service call /slam_toolbox/serialize_map slam_toolbox/srv/SerializePoseGraph \
  "{filename: '/ABSOLUTE/PATH/TO/slam_toolbox_demo/posegraph/turtlebot3_world_posegraph'}"

Rebuild so the saved map/posegraph get installed:

bash
cd ~/ros2_ws
colcon build --packages-select slam_toolbox_demo
source install/setup.bash
Localization Phase
bash
ros2 launch slam_toolbox_demo localization.launch.py

This loads the saved pose graph and runs slam_toolbox in localization mode.

In RViz2:

Add the Map display (/map) — the saved map should load immediately.
Use 2D Pose Estimate and click a deliberately wrong location/orientation. Observe the laser scan not aligning with the map's walls.
Use 2D Pose Estimate again with the robot's actual position and heading. Observe the laser scan snapping into alignment with the map.
Drive the robot around and confirm the map stays fixed in place — only the robot's pose/TF updates as it moves.
Expected Output
Mapping: a live occupancy grid builds in RViz as the robot explores turtlebot3_world, with walls and obstacles becoming clearly defined and no major misalignment after loop closure.
Localization: the previously saved map loads instantly on launch. An incorrect pose estimate visibly mismatches the laser scan against the map; a correct estimate aligns them. As the robot drives, the map remains static while the robot's estimated pose tracks its movement correctly.
Notes / Troubleshooting
slam_toolbox is a lifecycle node in current versions — it will not subscribe to /scan or publish /map until it is configured and activated.
Ensure use_sim_time: true is set for slam_toolbox when running in Gazebo, or timestamps between simulation time and wall-clock time will mismatch and scans will be silently dropped.
The map_file_name parameter for localization is injected at launch time (via get_package_share_directory) rather than hardcoded in localization.yaml, so the package remains portable across machines/users.
Demo

(To be added — demo recording pending final localization verification.)
