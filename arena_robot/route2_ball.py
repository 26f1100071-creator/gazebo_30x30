#!/usr/bin/env python3

import math
import subprocess
import time

WORLD = "arena_30x30"
BALL = "moving_ball_route2"
RADIUS = 0.35

# Route taken from the actual zig-zag geometry
#
# Start
#   ↓
# East side of Barrier 1
#   ↓
# West side of Barrier 2
#   ↓
# East side of Barrier 3
#   ↓
# West side of Barrier 4
#   ↓
# South exit
#
WAYPOINTS = [
    # Start / north entry
    (-1.5,  9.0, 0.40, 0.0),

    # Enter corridor through east side
    (-3.5,  8.0, 0.40, 3.0),

    # Go down toward Barrier 1
    (-3.5,  6.2, 0.40, 5.5),

    # Barrier 1 -> EAST GAP
    (-3.5,  6.0, 0.40, 6.0),

    # Move across to WEST side for Barrier 2
    (-12.5, 6.0, 0.40, 11.0),

    # Go down toward Barrier 2
    (-10.5, 3.8, 0.40, 13.0),

    # Barrier 2 -> WEST GAP
    (-12.5, 2.7, 0.40, 14.0),

    # Move across to EAST side for Barrier 3
    (-3.5,  2.7, 0.40, 19.0),

    # Go down toward Barrier 3
    (-3.5,  0.0, 0.40, 21.5),

    # Barrier 3 -> EAST GAP
    (-3.5, -1.3, 0.40, 22.5),

    # Move across to WEST side for Barrier 4
    (-12.5, -1.3, 0.40, 27.5),

    # Go down toward Barrier 4
    (-12.5, -4.0, 0.40, 30.0),

    # Barrier 4 -> WEST GAP
    (-12.5, -5.3, 0.40, 31.0),

    # Leave zig-zag corridor
    (-12.0, -7.0, 0.40, 33.0),
    (-8.0,  -7.5, 0.40, 35.0),
    (-4.0,  -8.0, 0.40, 37.0),

    # South exit
    (-1.5,  -8.0, 0.40, 39.0),

    # B
    (-1.5, -10.0, 0.40, 42.0),
]


def quaternion_multiply(q1, q2):
    w1, x1, y1, z1 = q1
    w2, x2, y2, z2 = q2

    return (
        w1*w2 - x1*x2 - y1*y2 - z1*z2,
        w1*x2 + x1*w2 + y1*z2 - z1*y2,
        w1*y2 - x1*z2 + y1*w2 + z1*x2,
        w1*z2 + x1*y2 - y1*x2 + z1*w2
    )


def quaternion_normalize(q):
    w, x, y, z = q

    length = math.sqrt(
        w*w + x*x + y*y + z*z
    )

    if length < 1e-12:
        return (1.0, 0.0, 0.0, 0.0)

    return (
        w / length,
        x / length,
        y / length,
        z / length
    )


def rotation_from_axis_angle(axis, angle):
    ax, ay, az = axis

    half = angle / 2.0

    s = math.sin(half)
    c = math.cos(half)

    return (
        c,
        ax * s,
        ay * s,
        az * s
    )


def set_ball_pose(x, y, z, q):

    qw, qx, qy, qz = q

    request = (
        f'name: "{BALL}" '
        f'position: {{x: {x:.4f}, y: {y:.4f}, z: {z:.4f}}} '
        f'orientation: {{'
        f'w: {qw:.6f}, '
        f'x: {qx:.6f}, '
        f'y: {qy:.6f}, '
        f'z: {qz:.6f}'
        f'}}'
    )

    command = [
        "gz",
        "service",
        "-s",
        f"/world/{WORLD}/set_pose",
        "--reqtype",
        "gz.msgs.Pose",
        "--reptype",
        "gz.msgs.Boolean",
        "--timeout",
        "1000",
        "--req",
        request,
    ]

    try:
        subprocess.run(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=1.5
        )
    except Exception:
        pass


def interpolate(p1, p2, current_time):

    x1, y1, z1, t1 = p1
    x2, y2, z2, t2 = p2

    if t2 == t1:
        ratio = 1.0
    else:
        ratio = (current_time - t1) / (t2 - t1)

    ratio = max(0.0, min(1.0, ratio))

    # Smooth movement
    smooth = ratio * ratio * (3.0 - 2.0 * ratio)

    x = x1 + (x2 - x1) * smooth
    y = y1 + (y2 - y1) * smooth
    z = z1 + (z2 - z1) * smooth

    return x, y, z


def main():

    print()
    print("======================================")
    print("     ROUTE 2 ZIG-ZAG BALL")
    print("======================================")
    print()
    print("Start")
    print("  -> Barrier 1 EAST gap")
    print("  -> Barrier 2 WEST gap")
    print("  -> Barrier 3 EAST gap")
    print("  -> Barrier 4 WEST gap")
    print("  -> South Exit")
    print("  -> B")
    print()
    print("Rolling rotation enabled")
    print()

    total_time = WAYPOINTS[-1][3]

    start_time = time.monotonic()

    orientation = (1.0, 0.0, 0.0, 0.0)

    previous_x = WAYPOINTS[0][0]
    previous_y = WAYPOINTS[0][1]

    previous_route_time = 0.0

    while True:

        elapsed = time.monotonic() - start_time

        route_time = elapsed % total_time

        # Restart orientation when route loops
        if route_time < previous_route_time:

            orientation = (
                1.0,
                0.0,
                0.0,
                0.0
            )

            previous_x = WAYPOINTS[0][0]
            previous_y = WAYPOINTS[0][1]

        for i in range(len(WAYPOINTS) - 1):

            p1 = WAYPOINTS[i]
            p2 = WAYPOINTS[i + 1]

            if p1[3] <= route_time <= p2[3]:

                x, y, z = interpolate(
                    p1,
                    p2,
                    route_time
                )

                # Distance travelled since previous update
                dx = x - previous_x
                dy = y - previous_y

                distance = math.sqrt(
                    dx * dx +
                    dy * dy
                )

                if distance > 0.00001:

                    # Direction of travel
                    vx = dx / distance
                    vy = dy / distance

                    # Rotation axis perpendicular to travel
                    axis_x = -vy
                    axis_y = vx
                    axis_z = 0.0

                    # Rolling angle
                    angle = distance / RADIUS

                    delta_rotation = rotation_from_axis_angle(
                        (
                            axis_x,
                            axis_y,
                            axis_z
                        ),
                        angle
                    )

                    orientation = quaternion_multiply(
                        delta_rotation,
                        orientation
                    )

                    orientation = quaternion_normalize(
                        orientation
                    )

                set_ball_pose(
                    x,
                    y,
                    z,
                    orientation
                )

                previous_x = x
                previous_y = y

                break

        previous_route_time = route_time

        time.sleep(0.08)


if __name__ == "__main__":
    main()

