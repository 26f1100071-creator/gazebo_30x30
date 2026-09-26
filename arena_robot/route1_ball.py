#!/usr/bin/env python3

import math
import subprocess
import time


WORLD = "arena_30x30"
BALL = "moving_ball_route1"

RADIUS = 0.35


# x, y, z, time
WAYPOINTS = [
    (0.0,  10.0, 0.40, 0.0),

    # Ascending ramp
    (0.0,   8.5, 0.75, 4.0),
    (0.0,   7.0, 1.10, 8.0),
    (0.0,   5.5, 1.45, 12.0),

    # Elevated platform
    (0.0,   3.5, 1.85, 17.0),
    (0.0,   1.0, 1.85, 22.0),

    # Descending ramp
    (0.0,  -1.5, 1.85, 27.0),
    (0.0,  -3.0, 1.55, 31.0),
    (0.0,  -4.5, 1.20, 35.0),
    (0.0,  -6.0, 0.85, 39.0),
    (0.0,  -7.5, 0.40, 43.0),

    # Point B
    (0.0, -10.0, 0.40, 48.0),
]


def quaternion_from_roll(roll):
    """
    Rotation around X axis.

    The ball rolls around the X axis because
    Route 1 moves mainly in the Y direction.
    """

    return (
        math.cos(roll / 2.0),
        math.sin(roll / 2.0),
        0.0,
        0.0
    )


def set_ball_pose(x, y, z, roll):

    qw, qx, qy, qz = quaternion_from_roll(roll)

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


def segment_distance(p1, p2, ratio):

    x1, y1, z1, _ = p1
    x2, y2, z2, _ = p2

    dx = x2 - x1
    dy = y2 - y1
    dz = z2 - z1

    distance = math.sqrt(
        dx * dx +
        dy * dy +
        dz * dz
    )

    return distance * ratio


def interpolate(p1, p2, current_time):

    x1, y1, z1, t1 = p1
    x2, y2, z2, t2 = p2

    ratio = (current_time - t1) / (t2 - t1)

    ratio = max(0.0, min(1.0, ratio))

    # Smooth movement
    smooth = ratio * ratio * (3.0 - 2.0 * ratio)

    x = x1 + (x2 - x1) * smooth
    y = y1 + (y2 - y1) * smooth
    z = z1 + (z2 - z1) * smooth

    return x, y, z, smooth


def calculate_total_distance():

    total = 0.0

    for i in range(len(WAYPOINTS) - 1):

        x1, y1, z1, _ = WAYPOINTS[i]
        x2, y2, z2, _ = WAYPOINTS[i + 1]

        total += math.sqrt(
            (x2 - x1) ** 2 +
            (y2 - y1) ** 2 +
            (z2 - z1) ** 2
        )

    return total


def calculate_distance_to_segment(segment_index, ratio):

    distance = 0.0

    # Full previous segments
    for i in range(segment_index):

        x1, y1, z1, _ = WAYPOINTS[i]
        x2, y2, z2, _ = WAYPOINTS[i + 1]

        distance += math.sqrt(
            (x2 - x1) ** 2 +
            (y2 - y1) ** 2 +
            (z2 - z1) ** 2
        )

    # Current segment
    x1, y1, z1, _ = WAYPOINTS[segment_index]
    x2, y2, z2, _ = WAYPOINTS[segment_index + 1]

    segment_length = math.sqrt(
        (x2 - x1) ** 2 +
        (y2 - y1) ** 2 +
        (z2 - z1) ** 2
    )

    distance += segment_length * ratio

    return distance


def main():

    print()
    print("======================================")
    print("  ROUTE 1 ROLLING BALL")
    print("======================================")
    print("A -> Ascending Ramp")
    print("  -> Elevated Platform")
    print("  -> Descending Ramp")
    print("  -> B")
    print()
    print("Ball rotation enabled")
    print()

    total_distance = calculate_total_distance()

    start_time = time.monotonic()

    while True:

        elapsed = time.monotonic() - start_time

        total_time = WAYPOINTS[-1][3]

        route_time = elapsed % total_time

        # Find current segment
        for i in range(len(WAYPOINTS) - 1):

            p1 = WAYPOINTS[i]
            p2 = WAYPOINTS[i + 1]

            if p1[3] <= route_time <= p2[3]:

                x, y, z, ratio = interpolate(
                    p1,
                    p2,
                    route_time
                )

                distance = calculate_distance_to_segment(
                    i,
                    ratio
                )

                # Rolling condition:
                #
                # distance = radius * angle
                #
                # Therefore:
                #
                # angle = distance / radius

                roll = distance / RADIUS

                set_ball_pose(
                    x,
                    y,
                    z,
                    roll
                )

                break

        time.sleep(0.05)


if __name__ == "__main__":
    main()
