# Gazebo 30×30 Arena

This project contains a 30 m × 30 m Gazebo arena with two routes:

* **Route 1:** Direct inclined ramp
* **Route 2:** Flat zig-zag corridor
* **Moving Ball 1:** Follows Route 1
* **Moving Ball 2:** Follows Route 2

## Project Structure

```text
gazebo_30x30/
├── worlds/
│   └── arena_30x30.sdf
│
├── arena_robot/
│   ├── route1_ball.py
│   └── route2_ball.py
│
└── README.md
```

## Requirements

Make sure the following are installed:

* Ubuntu
* ROS 2 Jazzy
* Gazebo
* Python 3

Check ROS 2:

```bash
source /opt/ros/jazzy/setup.bash
ros2 --version
```

Check Gazebo:

```bash
gz sim --version
```

## Running the Arena

Open **3 terminals**.

### Terminal 1 — Start Gazebo

First source ROS 2 Jazzy:

```bash
source /opt/ros/jazzy/setup.bash
```

Then start the Gazebo world:

```bash
gz sim ~/gazebo_30x30/worlds/arena_30x30.sdf
```

Wait until the arena is completely loaded.

---

### Terminal 2 — Run Route 1 Ball

Source ROS 2 Jazzy:

```bash
source /opt/ros/jazzy/setup.bash
```

Run the Route 1 ball:

```bash
python3 ~/gazebo_30x30/arena_robot/route1_ball.py
```

The first ball follows
