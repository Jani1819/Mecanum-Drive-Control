# ROS 2 Verification Commands

## Source ROS 2

```bash
source /opt/ros/<your_ros_distribution>/setup.bash
```

## Check the joystick device

```bash
ls /dev/input/js*
```

## Run teleoperation

```bash
python3 scripts/teleop_mecanum.py
```

## Check ROS 2 topics

```bash
ros2 topic list | grep cmd_vel
```

## Monitor Twist messages

```bash
ros2 topic echo /cmd_vel
```

## Inspect publisher information

```bash
ros2 topic info /cmd_vel
```

## Measure publication rate

```bash
ros2 topic hz /cmd_vel
```

The program is designed for a nominal 20 Hz loop.
