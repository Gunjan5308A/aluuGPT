import numpy as np


def bezier(points, t):
    n = len(points) - 1
    if n == 0:
        return np.array(points[0], dtype=float)
    result = np.zeros_like(points[0], dtype=float)
    for i, p in enumerate(points):
        coeff = _binomial(n, i) * ((1 - t) ** (n - i)) * (t ** i)
        result += coeff * np.array(p, dtype=float)
    return result


def quadratic_bezier(p0, p1, p2, t):
    p0, p1, p2 = np.array(p0, dtype=float), np.array(p1, dtype=float), np.array(p2, dtype=float)
    return (1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t ** 2 * p2


def cubic_bezier(p0, p1, p2, p3, t):
    p0 = np.array(p0, dtype=float)
    p1 = np.array(p1, dtype=float)
    p2 = np.array(p2, dtype=float)
    p3 = np.array(p3, dtype=float)
    return (
        (1 - t) ** 3 * p0
        + 3 * (1 - t) ** 2 * t * p1
        + 3 * (1 - t) * t ** 2 * p2
        + t ** 3 * p3
    )


def bezier_path(points, num_samples=100):
    points = [np.array(p, dtype=float) for p in points]
    return np.array([bezier(points, t / (num_samples - 1)) for t in range(num_samples)])


def partial_bezier_points(points, a, b):
    if a == 0:
        return _split_bezier(points, b)[0]
    a_split = _split_bezier(points, a)
    remainder = a_split[1]
    new_b = (b - a) / (1 - a) if a < 1 else 0
    return _split_bezier(remainder, new_b)[0]


def interpolate_bezier(points1, points2, t):
    return [
        (1 - t) * np.array(p1, dtype=float) + t * np.array(p2, dtype=float)
        for p1, p2 in zip(points1, points2)
    ]


def _split_bezier(points, t):
    points = [np.array(p, dtype=float) for p in points]
    n = len(points)
    left = []
    right = []
    work = [p.copy() for p in points]
    left.append(work[0].copy())
    right.append(work[-1].copy())
    for level in range(1, n):
        new_work = []
        for i in range(n - level):
            new_work.append((1 - t) * work[i] + t * work[i + 1])
        work = new_work
        left.append(work[0].copy())
        right.append(work[-1].copy())
    right.reverse()
    return left, right


def _binomial(n, k):
    if k < 0 or k > n:
        return 0
    if k == 0 or k == n:
        return 1
    result = 1
    for i in range(min(k, n - k)):
        result = result * (n - i) // (i + 1)
    return result
