import numpy as np
import math
from animation.animation import Animation
from utils.rate_functions import smooth


class Shift(Animation):
    def __init__(self, mobject, direction, run_time=1.0, rate_func=smooth):
        super().__init__(mobject, run_time=run_time, rate_func=rate_func)
        self.direction = np.array(direction, dtype=float)
        self._start_pos = None
        self._target_pos = None

    def begin(self):
        super().begin()
        self._start_pos = self.mobject.position.copy()
        self._target_pos = self._start_pos + self.direction

    def interpolate_mobject(self, t):
        new_pos = self._start_pos + (self._target_pos - self._start_pos) * t
        shift_vec = new_pos - self.mobject.position
        self.mobject.shift(shift_vec)


class MoveTo(Animation):
    def __init__(self, mobject, target_point, run_time=1.0, rate_func=smooth):
        super().__init__(mobject, run_time=run_time, rate_func=rate_func)
        self.target_point = np.array(target_point, dtype=float)
        self._start_pos = None

    def begin(self):
        super().begin()
        self._start_pos = self.mobject.get_center().copy()

    def interpolate_mobject(self, t):
        new_pos = self._start_pos + (self.target_point - self._start_pos) * t
        shift_vec = new_pos - self.mobject.get_center()
        self.mobject.shift(shift_vec)


class Rotate(Animation):
    def __init__(self, mobject, angle=math.pi, about_point=None,
                 run_time=1.0, rate_func=smooth):
        super().__init__(mobject, run_time=run_time, rate_func=rate_func)
        self.angle = angle
        self.about_point = about_point
        self._last_t = 0

    def begin(self):
        super().begin()
        self._last_t = 0
        if self.about_point is None:
            self.about_point = self.mobject.get_center().copy()
        else:
            self.about_point = np.array(self.about_point, dtype=float)

    def interpolate_mobject(self, t):
        delta_angle = self.angle * (t - self._last_t)
        self.mobject.rotate(delta_angle, about_point=self.about_point)
        self._last_t = t


class ScaleInPlace(Animation):
    def __init__(self, mobject, scale_factor, run_time=1.0, rate_func=smooth):
        super().__init__(mobject, run_time=run_time, rate_func=rate_func)
        self.scale_factor = scale_factor
        self._last_t = 0

    def begin(self):
        super().begin()
        self._last_t = 0

    def interpolate_mobject(self, t):
        target_scale = 1 + (self.scale_factor - 1) * t
        last_scale = 1 + (self.scale_factor - 1) * self._last_t
        if last_scale != 0:
            delta = target_scale / last_scale
            self.mobject.scale(delta)
        self._last_t = t


class MoveAlongPath(Animation):
    def __init__(self, mobject, path_points, run_time=1.0, rate_func=smooth):
        super().__init__(mobject, run_time=run_time, rate_func=rate_func)
        self.path_points = [np.array(p, dtype=float) for p in path_points]

    def begin(self):
        super().begin()

    def interpolate_mobject(self, t):
        if not self.path_points:
            return
        n = len(self.path_points) - 1
        if n <= 0:
            target = self.path_points[0]
        else:
            scaled = t * n
            idx = int(scaled)
            frac = scaled - idx
            if idx >= n:
                target = self.path_points[-1]
            else:
                target = self.path_points[idx] + frac * (self.path_points[idx + 1] - self.path_points[idx])
        shift_vec = target - self.mobject.get_center()
        self.mobject.shift(shift_vec)
