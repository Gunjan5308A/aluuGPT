import numpy as np
import pygame
import math
import copy
from utils.color import Color, WHITE, ORIGIN
from core.config import Config


class Mobject:
    def __init__(self, color=None, fill_color=None, fill_opacity=0.0,
                 stroke_width=None, opacity=1.0, z_index=0):
        self.position = np.array([0.0, 0.0])
        self.color = color if color is not None else Config.DEFAULT_MOBJECT_COLOR
        self.fill_color = fill_color if fill_color is not None else self.color
        self.fill_opacity = fill_opacity
        self.stroke_width = stroke_width if stroke_width is not None else Config.DEFAULT_STROKE_WIDTH
        self.opacity = opacity
        self.z_index = z_index
        self.stroke_proportion = 1.0
        self.submobjects = []
        self._angle = 0.0
        self._scale_factor = 1.0

    @property
    def color(self):
        return getattr(self, '_color', Config.DEFAULT_MOBJECT_COLOR)

    @color.setter
    def color(self, value):
        self._color = value
        for sub in getattr(self, 'submobjects', []):
            sub.color = value

    @property
    def fill_color(self):
        return getattr(self, '_fill_color', self.color)

    @fill_color.setter
    def fill_color(self, value):
        self._fill_color = value
        for sub in getattr(self, 'submobjects', []):
            sub.fill_color = value

    @property
    def fill_opacity(self):
        return getattr(self, '_fill_opacity', 0.0)

    @fill_opacity.setter
    def fill_opacity(self, value):
        self._fill_opacity = value
        for sub in getattr(self, 'submobjects', []):
            sub.fill_opacity = value

    @property
    def stroke_width(self):
        return getattr(self, '_stroke_width', Config.DEFAULT_STROKE_WIDTH)

    @stroke_width.setter
    def stroke_width(self, value):
        self._stroke_width = value
        for sub in getattr(self, 'submobjects', []):
            sub.stroke_width = value

    @property
    def opacity(self):
        return getattr(self, '_opacity', 1.0)

    @opacity.setter
    def opacity(self, value):
        self._opacity = value
        for sub in getattr(self, 'submobjects', []):
            sub.opacity = value

    @property
    def stroke_proportion(self):
        return getattr(self, '_stroke_proportion', 1.0)

    @stroke_proportion.setter
    def stroke_proportion(self, value):
        self._stroke_proportion = value
        for sub in getattr(self, 'submobjects', []):
            sub.stroke_proportion = value

    def draw(self, surface, camera):
        for sub in self.submobjects:
            sub.draw(surface, camera)

    def copy(self):
        return copy.deepcopy(self)

    def move_to(self, point):
        point = np.array(point, dtype=float)
        shift_vec = point - self.get_center()
        self.shift(shift_vec)
        return self

    def shift(self, vector):
        vector = np.array(vector, dtype=float)
        self.position += vector
        for sub in self.submobjects:
            sub.shift(vector)
        return self

    def scale(self, factor, about_point=None):
        if about_point is None:
            about_point = self.get_center()
        about_point = np.array(about_point, dtype=float)
        self.position = about_point + factor * (self.position - about_point)
        self._scale_factor *= factor
        self._apply_scale(factor, about_point)
        for sub in self.submobjects:
            sub.scale(factor, about_point)
        return self

    def _apply_scale(self, factor, about_point):
        pass

    def rotate(self, angle, about_point=None):
        if about_point is None:
            about_point = self.get_center()
        about_point = np.array(about_point, dtype=float)
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        offset = self.position - about_point
        self.position = about_point + np.array([
            cos_a * offset[0] - sin_a * offset[1],
            sin_a * offset[0] + cos_a * offset[1],
        ])
        self._angle += angle
        self._apply_rotation(angle, about_point)
        for sub in self.submobjects:
            sub.rotate(angle, about_point)
        return self

    def _apply_rotation(self, angle, about_point):
        pass

    def set_color(self, color):
        self.color = color
        for sub in self.submobjects:
            sub.set_color(color)
        return self

    def set_fill(self, color=None, opacity=None):
        if color is not None:
            self.fill_color = color
        if opacity is not None:
            self.fill_opacity = opacity
        return self

    def set_stroke(self, color=None, width=None, opacity=None):
        if color is not None:
            self.color = color
        if width is not None:
            self.stroke_width = width
        if opacity is not None:
            self.opacity = opacity
        return self

    def set_opacity(self, opacity):
        self.opacity = opacity
        for sub in self.submobjects:
            sub.set_opacity(opacity)
        return self

    def get_center(self):
        return self.position.copy()

    def get_top(self):
        bb = self.get_bounding_box()
        return np.array([(bb[0][0] + bb[1][0]) / 2, bb[1][1]])

    def get_bottom(self):
        bb = self.get_bounding_box()
        return np.array([(bb[0][0] + bb[1][0]) / 2, bb[0][1]])

    def get_left(self):
        bb = self.get_bounding_box()
        return np.array([bb[0][0], (bb[0][1] + bb[1][1]) / 2])

    def get_right(self):
        bb = self.get_bounding_box()
        return np.array([bb[1][0], (bb[0][1] + bb[1][1]) / 2])

    def get_bounding_box(self):
        return (self.position - 0.5, self.position + 0.5)

    def get_width(self):
        bb = self.get_bounding_box()
        return bb[1][0] - bb[0][0]

    def get_height(self):
        bb = self.get_bounding_box()
        return bb[1][1] - bb[0][1]

    def align_to(self, other, direction):
        direction = np.array(direction, dtype=float)
        if isinstance(other, Mobject):
            other_bb = other.get_bounding_box()
        else:
            other_bb = (np.array(other), np.array(other))
        self_bb = self.get_bounding_box()
        if direction[0] > 0:
            shift_x = other_bb[1][0] - self_bb[1][0]
        elif direction[0] < 0:
            shift_x = other_bb[0][0] - self_bb[0][0]
        else:
            shift_x = 0
        if direction[1] > 0:
            shift_y = other_bb[1][1] - self_bb[1][1]
        elif direction[1] < 0:
            shift_y = other_bb[0][1] - self_bb[0][1]
        else:
            shift_y = 0
        self.shift(np.array([shift_x, shift_y]))
        return self

    def next_to(self, other, direction, buff=0.25):
        direction = np.array(direction, dtype=float)
        if isinstance(other, Mobject):
            target = other.get_center()
            other_bb = other.get_bounding_box()
        else:
            target = np.array(other, dtype=float)
            other_bb = (target, target)
        self_bb = self.get_bounding_box()
        self_half = (self_bb[1] - self_bb[0]) / 2
        other_half = (other_bb[1] - other_bb[0]) / 2
        offset = np.zeros(2)
        for i in range(2):
            if direction[i] > 0:
                offset[i] = other_half[i] + self_half[i] + buff
            elif direction[i] < 0:
                offset[i] = -(other_half[i] + self_half[i] + buff)
        target_pos = (other.get_center() if isinstance(other, Mobject) else np.array(other, dtype=float))
        self.move_to(target_pos + offset * direction / np.maximum(np.abs(direction), 1e-10) * np.abs(direction))
        return self

    def to_edge(self, direction, buff=0.25):
        direction = np.array(direction, dtype=float)
        from core.config import Config

        frame_x = Config.FRAME_X_RADIUS
        frame_y = Config.FRAME_Y_RADIUS
        bb = self.get_bounding_box()
        shift = np.zeros(2)

        if direction[0] > 0:
            shift[0] = frame_x - buff - bb[1][0]
        elif direction[0] < 0:
            shift[0] = -frame_x + buff - bb[0][0]

        if direction[1] > 0:
            shift[1] = frame_y - buff - bb[1][1]
        elif direction[1] < 0:
            shift[1] = -frame_y + buff - bb[0][1]

        self.shift(shift)
        return self

    def add(self, *mobjects):
        for m in mobjects:
            if m not in self.submobjects:
                self.submobjects.append(m)
        return self

    def remove(self, *mobjects):
        for m in mobjects:
            if m in self.submobjects:
                self.submobjects.remove(m)
        return self

    def _get_effective_color(self):
        c = self.color
        return (c.r, c.g, c.b, int(c.a * self.opacity))

    def _get_effective_fill_color(self):
        c = self.fill_color
        return (c.r, c.g, c.b, int(c.a * self.fill_opacity * self.opacity))

    def _make_alpha_surface(self, width, height):
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        return surf
