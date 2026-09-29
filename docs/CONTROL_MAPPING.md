# Control Mapping

## Joystick input

The supplied Python program reads three joystick axes.

| Input | Code | Meaning |
|---|---|---|
| Axis 1 | `-get_axis(1)` | Forward/backward |
| Axis 4 | `get_axis(4)` | Rotation |
| Axis 3 | `get_axis(3)` | Strafing |

## Deadzone

```text
0.05
```

Values whose absolute magnitude is below the deadzone are replaced with zero.

## Publish frequency

```text
0.05 s loop period
20 Hz nominal update rate
```

## Current project-specific Twist mapping

### Rotation

```python
twist.linear.x = 1.0 * rotate
twist.linear.y = 1.0 * rotate
```

### Forward/backward

```python
twist.angular.y = -5.0 * forward
twist.angular.z = -5.0 * forward
```

### Strafing

```python
twist.linear.x = 2.0 * strafe
twist.linear.y = -2.0 * strafe
```

This mapping is intentionally documented as supplied. It should not be replaced by a conventional `/cmd_vel` mapping unless the Isaac Sim OmniGraph is changed at the same time.
