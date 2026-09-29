# Project Report: Isaac Sim Mecanum Drive Control

## 1. Project Title

**Joystick-Based Mecanum Drive Control in NVIDIA Isaac Sim Using ROS 2**

## 2. Project Summary

This project demonstrates teleoperation of a mecanum-wheel mobile robot in NVIDIA Isaac Sim using a physical joystick.

The system combines three main components:

1. A Python joystick teleoperation program.
2. A ROS 2 communication interface using `geometry_msgs/msg/Twist`.
3. An Isaac Sim OmniGraph that receives the Twist command and drives the robot wheel articulation.

The supplied Isaac Sim stage contains a robot and an OmniGraph named `Mecanum_Drive_01`. The graph includes ROS 2 nodes, vector-processing nodes, a differential controller, and an articulation controller.

The objective is to create a complete command path from a human-operated joystick to simulated mecanum-wheel motion.

---

## 3. Objectives

The main objectives of the project are:

- Control a mecanum-wheel robot inside Isaac Sim.
- Read a physical joystick from Python.
- Convert joystick input into ROS 2 `Twist` messages.
- Publish commands on `/cmd_vel`.
- Receive `/cmd_vel` inside Isaac Sim.
- Process linear and angular velocity vectors.
- Feed the processed command into a mecanum/differential controller.
- Send the resulting command to the robot articulation.
- Demonstrate forward/backward motion, strafing, and rotation.

---

## 4. System Architecture

The complete control pipeline is:

```text
+-------------------+
| Physical Joystick |
+---------+---------+
          |
          v
+---------------------------+
| Python Teleop Program     |
| Pygame + rclpy            |
+-------------+-------------+
              |
              | geometry_msgs/msg/Twist
              v
        +-----------+
        | /cmd_vel  |
        +-----+-----+
              |
              v
+---------------------------+
| Isaac Sim ROS 2 Bridge    |
| ROS2 Context              |
| ROS2 Subscribe Twist      |
+-------------+-------------+
              |
              v
+---------------------------+
| Vector Processing         |
| Break 3-Vector            |
| Scale To/From Stage Units |
+-------------+-------------+
              |
              v
+---------------------------+
| Differential Controller   |
+-------------+-------------+
              |
              v
+---------------------------+
| Articulation Controller   |
+-------------+-------------+
              |
              v
+---------------------------+
| Mecanum Wheel Joints      |
| / Robot Motion             |
+---------------------------+
```

---

## 5. Isaac Sim Environment

The project was developed around an Isaac Sim stage containing a wheeled mecanum-style robot.

The supplied screenshots show **Isaac Sim Full 5.0.0**.

The stage file supplied with the project is:

```text
Mecanum_Drive_Control.usd
```

The main control graph visible in the stage is:

```text
Mecanum_Drive_01
```

### Main graph elements visible in the supplied project

- On Playback Tick
- ROS2 Context
- ROS2 Subscribe Twist
- Break 3-Vector
- Scale To/From Stage Units
- Differential Controller
- Make Array
- Articulation Controller

These nodes form the simulation-side command-processing path.

---

## 6. ROS 2 Joystick Program

The teleoperation program uses:

```python
from geometry_msgs.msg import Twist
```

and creates a publisher:

```python
self.cmd_vel_pub = self.create_publisher(Twist, "/cmd_vel", 10)
```

Therefore the Python program sends joystick commands to:

```text
/cmd_vel
```

The program uses Pygame to access the first connected joystick:

```python
self.joystick = pygame.joystick.Joystick(0)
```

It also checks whether a joystick is connected before starting.

---

## 7. Joystick Deadzone

A deadzone of:

```text
0.05
```

is applied.

The purpose is to prevent small joystick noise or mechanical drift from generating unwanted robot commands.

The relevant logic is:

```python
def dz(self, value):
    return value if abs(value) >= self.deadzone else 0.0
```

---

## 8. Command Update Rate

The joystick loop uses:

```python
rate = 0.05
```

which corresponds to:

```text
1 / 0.05 = 20 Hz
```

Therefore, the program attempts to publish joystick commands at approximately 20 Hz.

---

## 9. Joystick Axis Mapping

The supplied program reads:

```python
forward = self.dz(-self.joystick.get_axis(1))
rotate = self.dz(self.joystick.get_axis(4))
strafe = self.dz(self.joystick.get_axis(3))
```

### Axis 1 - Forward / Backward

Axis 1 is inverted:

```python
forward = self.dz(-self.joystick.get_axis(1))
```

This is normally used to make pushing the stick forward produce a positive forward command.

### Axis 4 - Rotation

Axis 4 is read directly:

```python
rotate = self.dz(self.joystick.get_axis(4))
```

### Axis 3 - Strafing

Axis 3 is read directly:

```python
strafe = self.dz(self.joystick.get_axis(3))
```

---

## 10. Twist Command Generation

The program creates an empty Twist message:

```python
twist = Twist()
```

Then it fills fields according to the joystick action.

### Rotation

The supplied mapping is:

```python
twist.linear.x = 1.0 * rotate
twist.linear.y = 1.0 * rotate
```

### Forward / Backward

The supplied mapping is:

```python
twist.angular.y = -5.0 * forward
twist.angular.z = -5.0 * forward
```

### Strafing

The supplied mapping is:

```python
twist.linear.x = 2.0 * strafe
twist.linear.y = -2.0 * strafe
```

This is an important project-specific detail. It is not the conventional planar mobile-base Twist mapping. The Isaac Sim graph must therefore be configured consistently with this command structure.

---

## 11. Isaac Sim OmniGraph Procedure

### Step 1 - Open the stage

Open:

```text
Mecanum_Drive_Control.usd
```

in Isaac Sim.

### Step 2 - Locate the graph

Open the Action Graph / OmniGraph editor and select:

```text
Mecanum_Drive_01
```

### Step 3 - ROS 2 context

The graph contains a ROS 2 Context node. This provides the ROS 2 environment used by the Isaac Sim ROS 2 nodes.

### Step 4 - Subscribe to Twist

The graph contains a:

```text
ROS2 Subscribe Twist
```

node.

Its purpose is to receive the Twist command published to `/cmd_vel`.

### Step 5 - Process vectors

The graph contains `Break 3-Vector` nodes for separating vector components.

A `Scale To/From Stage Units` node is also visible in the supplied graph.

### Step 6 - Differential controller

The processed velocity command is passed into the:

```text
Differential Controller
```

This node produces a wheel velocity command.

The supplied graph exposes controller parameters including:

- Desired Angular Velocity
- Desired Linear Velocity
- Time step
- Maximum acceleration
- Maximum angular acceleration
- Maximum angular speed
- Maximum deceleration
- Maximum linear speed
- Maximum wheel speed
- Wheel distance
- Wheel radius

### Step 7 - Articulation controller

The differential controller's velocity output is connected to the:

```text
Articulation Controller
```

The articulation controller sends the command to the robot's wheel joints.

---

## 12. End-to-End Working Procedure

Use the following sequence when reproducing the project.

### Phase A - Hardware

1. Connect the joystick.
2. Confirm that the operating system detects it.
3. Keep the joystick centered.

### Phase B - ROS 2

1. Source the ROS 2 environment.
2. Confirm `rclpy` and `geometry_msgs` are available.
3. Run the teleoperation script.
4. Confirm that the joystick name is printed.

### Phase C - Isaac Sim

1. Launch Isaac Sim.
2. Open `Mecanum_Drive_Control.usd`.
3. Open `Mecanum_Drive_01`.
4. Confirm the ROS 2 nodes are present.
5. Press Play.

### Phase D - Communication Test

Run:

```bash
ros2 topic echo /cmd_vel
```

Move the joystick.

If the Twist values change, the joystick-to-ROS portion is operating.

### Phase E - Robot Motion Test

Test one motion at a time:

```text
1. Forward
2. Backward
3. Strafe left
4. Strafe right
5. Rotate
```

Only after individual motions are working should combined joystick inputs be tested.

---

## 13. Testing and Verification

### Test 1 - Joystick detection

Expected result:

```text
Joystick detected: <controller name>
```

### Test 2 - ROS 2 topic

Expected topic:

```text
/cmd_vel
```

### Test 3 - Twist data

Run:

```bash
ros2 topic echo /cmd_vel
```

Move the joystick and verify that the message changes.

### Test 4 - Isaac Sim reception

With Isaac Sim playing, the ROS 2 subscriber should receive the command.

### Test 5 - Wheel control

The controller chain should pass the command to the articulation controller.

### Test 6 - Robot motion

Verify the corresponding physical/simulated motion for each joystick axis.

---

## 14. Troubleshooting

### Problem: No joystick detected

Check:

```bash
ls /dev/input/js*
```

If no device is visible:

- reconnect the controller,
- check USB permissions,
- verify that the controller works with the operating system,
- restart the teleoperation program.

### Problem: `/cmd_vel` has no messages

Check:

```bash
ros2 topic list | grep cmd_vel
```

Then:

```bash
ros2 topic echo /cmd_vel
```

If the topic does not exist, check that the Python program is running.

### Problem: `/cmd_vel` changes but the robot does not move

Inspect the Isaac Sim graph in this order:

```text
ROS2 Subscribe Twist
        |
        v
Break 3-Vector
        |
        v
Differential Controller
        |
        v
Articulation Controller
        |
        v
Wheel joints
```

### Problem: Direction is reversed

Joystick axis polarity can differ between controllers.

Change the sign of the relevant joystick axis only after confirming the current values.

### Problem: Strafe direction is reversed

Check the signs used for:

```python
twist.linear.x
twist.linear.y
```

and verify the mecanum wheel configuration.

### Problem: Motion is too fast

Reduce the command scale factors in the Python node and retest.

---

## 15. Important Implementation Notes

### Node name

The supplied original program used the class/node naming:

```text
TurtleBotDualDifferential
turtlebot_dual_diff_drive
```

The cleaned repository version uses names associated with the actual mecanum project:

```text
MecanumJoystickTeleop
mecanum_joystick_teleop
```

The command behavior and `/cmd_vel` interface are preserved.

### Threading

The joystick loop runs in a separate thread while ROS 2 spins the node.

The thread is stopped during `destroy_node()` and Pygame is shut down cleanly.

---

## 16. Limitations

The supplied source files do not provide a complete ROS 2 package (`package.xml`, `setup.py`, launch files, controller YAML, etc.). Therefore this repository documents and packages the working assets that were actually supplied rather than inventing missing package configuration.

The project-specific Twist field mapping is also unconventional for a standard planar mobile robot. Any future refactoring should update both the Python publisher and Isaac Sim graph together.

The exact joystick button/axis numbering can vary by controller model.

---

## 17. Future Improvements

Possible extensions include:

- Convert the joystick program into a complete ROS 2 Python package.
- Add configurable ROS parameters for deadzone and speed scaling.
- Add a joystick diagnostic mode.
- Add a launch file for the teleoperation node.
- Add automatic emergency-stop/zero-command handling when the joystick disconnects.
- Add acceleration limiting in the teleoperation node.
- Standardize the command interface around conventional planar `Twist` fields if the Isaac Sim graph is redesigned accordingly.
- Add wheel-joint state feedback.
- Add odometry publishing.
- Add automated motion tests.
- Add a proper open-source license and third-party attribution file.

---

## 18. Files Delivered With This Report

### Isaac Sim

```text
isaac_sim/Mecanum_Drive_Control.usd
```

### ROS 2 / joystick control

```text
scripts/teleop_mecanum.py
```

### Documentation

```text
README.md
docs/PROJECT_REPORT.md
docs/CONTROL_MAPPING.md
```

### Visual documentation

```text
docs/images/isaac_sim_robot.png
docs/images/omnigraph_mecanum_drive.png
docs/images/omnigraph_controller.png
```

### Demonstration

```text
media/mecanum_drive_demo.mp4
```

---

## 19. Conclusion

The project establishes a complete joystick-to-simulation control pipeline:

```text
Joystick
   ↓
Pygame
   ↓
Python ROS 2 node
   ↓
/cmd_vel
   ↓
ROS 2 Subscribe Twist
   ↓
Isaac Sim OmniGraph
   ↓
Differential Controller
   ↓
Articulation Controller
   ↓
Mecanum Robot
```

The supplied files and screenshots provide the core implementation and evidence of the Isaac Sim control graph. This repository packages those materials into a GitHub-ready structure with reproducible operating instructions and a technical project report.
