from animation.animation import Animation
from utils.rate_functions import smooth
from utils.color import interpolate_color
import numpy as np


class FadeIn(Animation):
    def __init__(self, mobject, shift_direction=None, scale=1.0,
                 run_time=1.0, rate_func=smooth):
        super().__init__(mobject, run_time=run_time, rate_func=rate_func)
        self.shift_direction = np.array(shift_direction, dtype=float) if shift_direction is not None else None
        self.target_scale = scale
        self._original_opacity = None
        self._start_pos = None

    def begin(self):
        super().begin()
        self._original_opacity = self.mobject.opacity
        self.mobject.opacity = 0.0
        self._start_pos = self.mobject.position.copy()
        if self.shift_direction is not None:
            self.mobject.shift(-self.shift_direction)

    def interpolate_mobject(self, t):
        self.mobject.opacity = self._original_opacity * t
        if self.shift_direction is not None:
            target_pos = self._start_pos
            current_center = self.mobject.get_center()
            start_shifted = self._start_pos - self.shift_direction
            new_pos = start_shifted + (target_pos - start_shifted) * t
            self.mobject.shift(new_pos - current_center)

    def finish(self):
        self.mobject.opacity = self._original_opacity
        if self.shift_direction is not None:
            self.mobject.move_to(self._start_pos)
        self._is_finished = True


class FadeOut(Animation):
    def __init__(self, mobject, shift_direction=None, scale=1.0,
                 run_time=1.0, rate_func=smooth):
        super().__init__(mobject, run_time=run_time, rate_func=rate_func)
        self.shift_direction = np.array(shift_direction, dtype=float) if shift_direction is not None else None
        self.target_scale = scale
        self._original_opacity = None
        self._start_pos = None
        self._remove_on_finish = True

    def begin(self):
        super().begin()
        self._original_opacity = self.mobject.opacity
        self._start_pos = self.mobject.position.copy()

    def interpolate_mobject(self, t):
        self.mobject.opacity = self._original_opacity * (1 - t)
        if self.shift_direction is not None:
            target_pos = self._start_pos + self.shift_direction
            new_pos = self._start_pos + (target_pos - self._start_pos) * t
            current_center = self.mobject.get_center()
            self.mobject.shift(new_pos - current_center)

    def clean_up(self):
        self.mobject.opacity = 0.0


class FadeTransform(Animation):
    def __init__(self, source, target, run_time=1.0, rate_func=smooth):
        super().__init__(source, run_time=run_time, rate_func=rate_func)
        self.source = source
        self.target = target
        self._source_opacity = None
        self._target_opacity = None
        self._add_target = True

    def begin(self):
        super().begin()
        self._source_opacity = self.source.opacity
        self._target_opacity = self.target.opacity
        self.target.opacity = 0.0

    def interpolate_mobject(self, t):
        self.source.opacity = self._source_opacity * (1 - t)
        self.target.opacity = self._target_opacity * t

    def finish(self):
        self.source.opacity = 0.0
        self.target.opacity = self._target_opacity
        self._is_finished = True

    def get_all_mobjects(self):
        return [self.source, self.target]


class GrowFromCenter(Animation):
    def __init__(self, mobject, run_time=1.0, rate_func=smooth):
        super().__init__(mobject, run_time=run_time, rate_func=rate_func)
        self._original_opacity = None
        self._last_t = 0

    def begin(self):
        super().begin()
        self._original_opacity = self.mobject.opacity
        self.mobject.opacity = 0.0
        self.mobject.scale(0.001)
        self._last_t = 0

    def interpolate_mobject(self, t):
        self.mobject.opacity = self._original_opacity * t
        if self._last_t > 0.001:
            scale_ratio = max(t, 0.001) / self._last_t
            self.mobject.scale(scale_ratio)
        elif t > 0:
            self.mobject.scale(t / 0.001)
        self._last_t = max(t, 0.001)

    def finish(self):
        self.mobject.opacity = self._original_opacity
        self._is_finished = True
