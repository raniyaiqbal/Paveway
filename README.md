# PaveWay Project

PaveWay is an autonomous pothole detection and mapping robot based on the TurtleBot3 platform. The project includes a simulation environment and a web app for visualization.

## Workspace Setup

### Installing Dependencies

PaveWay relies on the TurtleBot3 ROS 2 packages. To install the required dependencies, run the following commands:

```sh
mkdir -p ~/turtlebot3_ws/src
cd ~/turtlebot3_ws/src/
git clone -b humble https://github.com/ROBOTIS-GIT/DynamixelSDK.git
git clone -b humble https://github.com/ROBOTIS-GIT/turtlebot3_msgs.git
git clone -b humble https://github.com/ROBOTIS-GIT/turtlebot3.git
git clone -b humble https://github.com/ROBOTIS-GIT/turtlebot3_simulations.git
cd ~/turtlebot3_ws && colcon build --symlink-install
```

### Building the PaveWay Workspace

After cloning the PaveWay repository, build the workspace with:

```sh
cd ~/paveway_ws
colcon build --symlink-install
```

## Running the Simulation

To launch the PaveWay simulation, use the following command:

```sh
export TURTLEBOT3_MODEL="burger"
ros2 launch paveway_sim paveway_sim.launch.py
```

## Repository Structure

```
📂 paveway_ws
├── 📂 src
│   ├── 📂 paveway_sim
│   ├── 📂 paveway_navigation
│   ├── 📂 paveway_detection
│   ├── 📂 paveway_web
│   └── ...
└── colcon.meta
```
