import math
import numpy as np
from animation.animation import Animation
from utils.rate_functions import smooth, there_and_back
from utils.color import Color, YELLOW, interpolate_color


class Indicate(Animation):
    def __init__(self, mobject, scale_factor=1.2, color=None,
                 run_time=0.8, rate_func=there_and_back):
        super().__init__(mobject, run_time=run_time, rate_func=rate_func)
        self.scale_factor = scale_factor
        self.indicate_color = color or YELLOW
        self._original_color = None
        self._last_t = 0

    def begin(self):
        super().begin()
        self._original_color = self.mobject.color.copy()
        self._last_t = 0

    def interpolate_mobject(self, t):
        self.mobject.color = interpolate_color(self._original_color, self.indicate_color, t)
        target_scale = 1 + (self.scale_factor - 1) * t
        last_scale = 1 + (self.scale_factor - 1) * self._last_t
        if last_scale > 0.001:
            self.mobject.scale(target_scale / last_scale)
        self._last_t = t

    def finish(self):
        self.mobject.color = self._original_color
        self._is_finished = True


class Flash(Animation):
    def __init__(self, point, color=None, num_lines=12, line_length=0.3,
                 flash_radius=0.5, run_time=0.5, rate_func=smooth):
        from mobjects.geometry import Line
        self.point = np.array(point if not hasattr(point, 'get_center') else point.get_center(), dtype=float)
        self.flash_color = color or YELLOW
        self.num_lines = num_lines
        self.line_length = line_length
        self.flash_radius = flash_radius
        self.lines = []
        for i in range(num_lines):
            angle = 2 * math.pi * i / num_lines
            direction = np.array([math.cos(angle), math.sin(angle)])
            start = self.point + direction * flash_radius
            end = start + direction * line_length
            line = Line(start=start, end=end, color=self.flash_color)
            self.lines.append(line)
        from mobjects.group import Group
        self.group = Group(*self.lines)
        super().__init__(self.group, run_time=run_time, rate_func=rate_func)

    def begin(self):
        super().begin()

    def interpolate_mobject(self, t):
        for line in self.lines:
            if t < 0.5:
                line.opacity = t * 2
            else:
                line.opacity = (1 - t) * 2

    def get_all_mobjects(self):
        return self.lines

    def clean_up(self):
        for line in self.lines:
            line.opacity = 0.0


class Circumscribe(Animation):
    def __init__(self, mobject, shape="rectangle", color=None, buff=0.15,
                 run_time=1.0, rate_func=smooth, fade_out=True):
        super().__init__(mobject, run_time=run_time, rate_func=rate_func)
        self.shape_type = shape
        self.circumscribe_color = color or YELLOW
        self.buff = buff
        self.fade_out = fade_out
        self._outline = None

    def begin(self):
        super().begin()
        bb = self.mobject.get_bounding_box()
        w = bb[1][0] - bb[0][0] + 2 * self.buff
        h = bb[1][1] - bb[0][1] + 2 * self.buff
        center = (bb[0] + bb[1]) / 2
        if self.shape_type == "circle":
            from mobjects.geometry import Circle
            radius = max(w, h) / 2
            self._outline = Circle(radius=radius, color=self.circumscribe_color)
            self._outline.move_to(center)
        else:
            from mobjects.geometry import Rectangle
            self._outline = Rectangle(width=w, height=h, color=self.circumscribe_color)
            self._outline.move_to(center)
        self._outline.opacity = 0.0
        self._outline.stroke_width = 3

    def interpolate_mobject(self, t):
        if self._outline is None:
            return
        if t < 0.3:
            self._outline.opacity = t / 0.3
        elif t > 0.7 and self.fade_out:
            self._outline.opacity = (1 - t) / 0.3
        else:
            self._outline.opacity = 1.0

    def get_all_mobjects(self):
        if self._outline:
            return [self.mobject, self._outline]
        return [self.mobject]

    def clean_up(self):
        if self._outline:
            self._outline.opacity = 0.0


class Wiggle(Animation):
    def __init__(self, mobject, scale_value=1.1, rotation_angle=0.05,
                 n_wiggles=6, run_time=1.0, rate_func=smooth):
        super().__init__(mobject, run_time=run_time, rate_func=rate_func)
        self.scale_value = scale_value
        self.rotation_angle = rotation_angle
        self.n_wiggles = n_wiggles
        self._last_t = 0
        self._last_angle = 0

    def begin(self):
        super().begin()
        self._last_t = 0
        self._last_angle = 0

    def interpolate_mobject(self, t):
        wiggle = math.sin(2 * math.pi * self.n_wiggles * t)
        envelope = math.sin(math.pi * t)
        angle = self.rotation_angle * wiggle * envelope
        delta_angle = angle - self._last_angle
        self.mobject.rotate(delta_angle)
        self._last_angle = angle
        target_scale = 1 + (self.scale_value - 1) * envelope
        last_envelope = math.sin(math.pi * self._last_t)
        last_scale_val = 1 + (self.scale_value - 1) * last_envelope
        if last_scale_val > 0.001:
            self.mobject.scale(target_scale / last_scale_val)
        self._last_t = t

    def finish(self):
        if self._last_angle != 0:
            self.mobject.rotate(-self._last_angle)
        self._is_finished = True
