# PaveWay Project

PaveWay is an autonomous pothole detection and mapping robot based on the TurtleBot3 platform. The project includes a simulation environment and a web app for visualization.

## Workspace Setup

### Building the PaveWay Workspace

After cloning the PaveWay repository, install the dependencies (TurtleBot3, Nav2, Gazebo, etc.) and build the workspace with:

```sh
cd ~/paveway_ws
sudo apt install ros-$ROS_DISTRO-turtlebot3* ros-$ROS_DISTRO-nav2-bringup
rosdep install --from-paths src --ignore-src -y
pip install ultralytics
colcon build --symlink-install
```

### Sourcing the Workspace

After building the workspace, source and define Turtlebot model:

```sh
source install/setup.bash #or setup.zsh
export TURTLEBOT3_MODEL="burger" # or "waffle"
```

## Running the Packages

### Running Gazebo Simulation

```sh
ros2 launch paveway_sim paveway_sim.launch.py
```

### Running Navigation Node

```sh
ros2 launch paveway_nav paveway_nav.launch.py
```

### Running Server Node

After running the server node, the web dashboard can be found at [Foxglove](https://app.foxglove.dev/ecte351/view)

```sh
ros2 launch paveway_web web.launch.py
```

## Repository Structure

```
📂 paveway_ws
├── 📂 src
│   ├── 📂 paveway_sim
│   ├── 📂 paveway_nav
│   ├── 📂 paveway_vision
│   ├── 📂 paveway_web
│   ├── 📂 paveway_bringup
│   └── ...
└── colcon.meta
```
