from animation.animation import Animation
from utils.rate_functions import smooth, linear
import numpy as np


class Create(Animation):
    def __init__(self, mobject, run_time=1.0, rate_func=smooth):
        super().__init__(mobject, run_time=run_time, rate_func=rate_func)
        self._target_opacity = None
        self._target_fill_opacity = None

    def begin(self):
        super().begin()
        self._target_opacity = self.mobject.opacity
        self._target_fill_opacity = self.mobject.fill_opacity
        self.mobject.stroke_proportion = 0.0
        self.mobject.fill_opacity = 0.0

    def interpolate_mobject(self, t):
        if t < 0.8:
            # First 80% of time: draw the stroke
            stroke_t = t / 0.8
            self.mobject.stroke_proportion = stroke_t
            self.mobject.opacity = self._target_opacity
            self.mobject.fill_opacity = 0.0
        else:
            # Last 20% of time: fade in the fill
            self.mobject.stroke_proportion = 1.0
            fill_t = (t - 0.8) / 0.2
            self.mobject.fill_opacity = self._target_fill_opacity * fill_t

    def finish(self):
        self.mobject.stroke_proportion = 1.0
        self.mobject.opacity = self._target_opacity
        self.mobject.fill_opacity = self._target_fill_opacity
        self._is_finished = True


class Uncreate(Animation):
    def __init__(self, mobject, run_time=1.0, rate_func=smooth):
        super().__init__(mobject, run_time=run_time, rate_func=rate_func)
        self._original_opacity = None
        self._original_fill_opacity = None
        self._remove_on_finish = True

    def begin(self):
        super().begin()
        self._original_opacity = self.mobject.opacity
        self._original_fill_opacity = self.mobject.fill_opacity

    def interpolate_mobject(self, t):
        if t < 0.5:
            fill_t = 1 - t * 2
            self.mobject.fill_opacity = self._original_fill_opacity * fill_t
            self.mobject.opacity = self._original_opacity
        else:
            self.mobject.fill_opacity = 0.0
            stroke_t = 1 - (t - 0.5) * 2
            self.mobject.opacity = self._original_opacity * stroke_t

    def clean_up(self):
        self.mobject.opacity = 0.0
        self.mobject.fill_opacity = 0.0


class DrawBorderThenFill(Animation):
    def __init__(self, mobject, run_time=1.5, rate_func=smooth,
                 stroke_color=None):
        super().__init__(mobject, run_time=run_time, rate_func=rate_func)
        self.stroke_color = stroke_color
        self._target_opacity = None
        self._target_fill_opacity = None
        self._original_color = None

    def begin(self):
        super().begin()
        self._target_opacity = self.mobject.opacity
        self._target_fill_opacity = self.mobject.fill_opacity
        self._original_color = self.mobject.color
        if self.stroke_color:
            self.mobject.color = self.stroke_color
        self.mobject.opacity = 0.0
        self.mobject.fill_opacity = 0.0

    def interpolate_mobject(self, t):
        if t < 0.5:
            stroke_t = t * 2
            self.mobject.opacity = self._target_opacity * stroke_t
            self.mobject.fill_opacity = 0.0
        else:
            fill_t = (t - 0.5) * 2
            self.mobject.opacity = self._target_opacity
            self.mobject.fill_opacity = self._target_fill_opacity * fill_t
            if self.stroke_color:
                from utils.color import interpolate_color
                self.mobject.color = interpolate_color(self.stroke_color, self._original_color, fill_t)

    def finish(self):
        self.mobject.opacity = self._target_opacity
        self.mobject.fill_opacity = self._target_fill_opacity
        self.mobject.color = self._original_color
        self._is_finished = True


class Write(Animation):
    def __init__(self, mobject, run_time=1.0, rate_func=smooth):
        super().__init__(mobject, run_time=run_time, rate_func=rate_func)
        self._target_opacity = None

    def begin(self):
        super().begin()
        self._target_opacity = self.mobject.opacity
        self.mobject.opacity = 0.0

    def interpolate_mobject(self, t):
        self.mobject.opacity = self._target_opacity * t

    def finish(self):
        self.mobject.opacity = self._target_opacity
        self._is_finished = True


class ShowPassingFlash(Animation):
    def __init__(self, mobject, time_width=0.3, run_time=1.0, rate_func=linear):
        super().__init__(mobject, run_time=run_time, rate_func=rate_func)
        self.time_width = time_width
        self._target_opacity = None

    def begin(self):
        super().begin()
        self._target_opacity = self.mobject.opacity
        self.mobject.opacity = 0.0

    def interpolate_mobject(self, t):
        lower = t - self.time_width / 2
        upper = t + self.time_width / 2
        if lower <= 0.5 <= upper:
            brightness = 1.0
        else:
            dist = min(abs(0.5 - lower), abs(0.5 - upper))
            brightness = max(0, 1 - dist * 4)
        self.mobject.opacity = self._target_opacity * brightness

    def clean_up(self):
        self.mobject.opacity = 0.0
