import numpy as np
import copy
from animation.animation import Animation
from utils.rate_functions import smooth
from utils.color import interpolate_color


class Transform(Animation):
    def __init__(self, source, target, run_time=1.0, rate_func=smooth):
        super().__init__(source, run_time=run_time, rate_func=rate_func)
        self.source = source
        self.target = target
        self._source_snapshot = None

    def begin(self):
        super().begin()
        self._source_snapshot = self.source.copy()

    def interpolate_mobject(self, t):
        src = self._source_snapshot
        tgt = self.target
        self.source.position = src.position + (tgt.position - src.position) * t
        self.source.color = interpolate_color(src.color, tgt.color, t)
        self.source.fill_color = interpolate_color(src.fill_color, tgt.fill_color, t)
        self.source.opacity = src.opacity + (tgt.opacity - src.opacity) * t
        self.source.fill_opacity = src.fill_opacity + (tgt.fill_opacity - src.fill_opacity) * t
        self.source.stroke_width = src.stroke_width + (tgt.stroke_width - src.stroke_width) * t
        if hasattr(src, 'radius') and hasattr(tgt, 'radius'):
            self.source.radius = src.radius + (tgt.radius - src.radius) * t
        if hasattr(src, 'width') and hasattr(tgt, 'width'):
            self.source.width = src.width + (tgt.width - src.width) * t
        if hasattr(src, 'height') and hasattr(tgt, 'height'):
            self.source.height = src.height + (tgt.height - src.height) * t
        if hasattr(src, 'vertices') and hasattr(tgt, 'vertices'):
            sv = src.vertices
            tv = tgt.vertices
            min_len = min(len(sv), len(tv))
            if min_len > 0:
                interp = sv[:min_len] + (tv[:min_len] - sv[:min_len]) * t
                self.source.vertices = interp

    def finish(self):
        self.interpolate_mobject(1.0)
        self._is_finished = True


class ReplacementTransform(Transform):
    def __init__(self, source, target, run_time=1.0, rate_func=smooth):
        super().__init__(source, target, run_time=run_time, rate_func=rate_func)
        self._replace_on_finish = True

    def finish(self):
        super().finish()

    def get_all_mobjects(self):
        return [self.source]

    def clean_up(self):
        pass


class CounterclockwiseTransform(Transform):
    def __init__(self, source, target, run_time=1.0, rate_func=smooth):
        super().__init__(source, target, run_time=run_time, rate_func=rate_func)
        self._angle_offset = 0

    def begin(self):
        super().begin()
        import math
        src_angle = getattr(self._source_snapshot, '_angle', 0)
        tgt_angle = getattr(self.target, '_angle', 0)
        diff = tgt_angle - src_angle
        if diff < 0:
            diff += 2 * math.pi
        self._angle_offset = diff

    def interpolate_mobject(self, t):
        super().interpolate_mobject(t)
        delta = self._angle_offset * t
        self.source._angle = getattr(self._source_snapshot, '_angle', 0) + delta


class TransformFromCopy(Transform):
    def __init__(self, source, target, run_time=1.0, rate_func=smooth):
        source_copy = source.copy()
        super().__init__(source_copy, target, run_time=run_time, rate_func=rate_func)
        self._original_source = source

    def get_all_mobjects(self):
        return [self.source, self.target]
