import numpy as np
import math


def normalize(v):
    v = np.array(v, dtype=float)
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm


def angle_of_vector(v):
    return math.atan2(v[1], v[0])


def angle_between(v1, v2):
    v1 = normalize(v1)
    v2 = normalize(v2)
    dot = np.clip(np.dot(v1, v2), -1.0, 1.0)
    return math.acos(dot)


def rotate_vector(v, angle):
    v = np.array(v, dtype=float)
    c, s = math.cos(angle), math.sin(angle)
    return np.array([c * v[0] - s * v[1], s * v[0] + c * v[1]])


def rotation_matrix(angle):
    c, s = math.cos(angle), math.sin(angle)
    return np.array([[c, -s], [s, c]])


def lerp(a, b, t):
    return a + (b - a) * t


def inverse_lerp(a, b, v):
    if a == b:
        return 0.0
    return (v - a) / (b - a)


def remap(v, in_min, in_max, out_min, out_max):
    t = inverse_lerp(in_min, in_max, v)
    return lerp(out_min, out_max, t)


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def distance(p1, p2):
    return np.linalg.norm(np.array(p2, dtype=float) - np.array(p1, dtype=float))


def midpoint(p1, p2):
    return (np.array(p1, dtype=float) + np.array(p2, dtype=float)) / 2


def line_intersection(p1, d1, p2, d2):
    p1 = np.array(p1, dtype=float)
    d1 = np.array(d1, dtype=float)
    p2 = np.array(p2, dtype=float)
    d2 = np.array(d2, dtype=float)
    cross = d1[0] * d2[1] - d1[1] * d2[0]
    if abs(cross) < 1e-10:
        return None
    dp = p2 - p1
    t = (dp[0] * d2[1] - dp[1] * d2[0]) / cross
    return p1 + t * d1


def points_on_circle(n, radius=1.0, center=None, start_angle=0.0):
    if center is None:
        center = np.array([0.0, 0.0])
    else:
        center = np.array(center, dtype=float)
    angles = [start_angle + 2 * math.pi * i / n for i in range(n)]
    return [center + radius * np.array([math.cos(a), math.sin(a)]) for a in angles]


def linspace_2d(start, end, n):
    start = np.array(start, dtype=float)
    end = np.array(end, dtype=float)
    return [start + (end - start) * i / max(n - 1, 1) for i in range(n)]
