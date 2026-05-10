import numpy as np
from core.config import Config


class Camera:
    def __init__(self, width=None, height=None, px_per_unit=None):
        self.width = width or Config.WIDTH
        self.height = height or Config.HEIGHT
        self.px_per_unit = px_per_unit or Config.PIXEL_PER_UNIT
        self.center_px = np.array([self.width / 2, self.height / 2])
        self._offset = np.array([0.0, 0.0])
        self._zoom = 1.0

    @property
    def zoom(self):
        return self._zoom

    @zoom.setter
    def zoom(self, value):
        self._zoom = max(0.01, value)

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, value):
        self._offset = np.array(value, dtype=float)

    @property
    def effective_px_per_unit(self):
        return self.px_per_unit * self._zoom

    def to_pixels(self, math_coords):
        math_coords = np.array(math_coords, dtype=float)
        adjusted = (math_coords - self._offset) * self._zoom
        px_x = self.center_px[0] + adjusted[0] * self.px_per_unit
        px_y = self.center_px[1] - adjusted[1] * self.px_per_unit
        return (int(px_x), int(px_y))

    def to_math(self, pixel_coords):
        px_x, px_y = pixel_coords
        math_x = (px_x - self.center_px[0]) / (self.px_per_unit * self._zoom) + self._offset[0]
        math_y = (self.center_px[1] - px_y) / (self.px_per_unit * self._zoom) + self._offset[1]
        return np.array([math_x, math_y])

    def math_to_pixel_length(self, math_length):
        return int(math_length * self.effective_px_per_unit)

    def get_frame_bounds(self):
        half_w = self.width / (2 * self.effective_px_per_unit)
        half_h = self.height / (2 * self.effective_px_per_unit)
        return {
            'x_min': self._offset[0] - half_w,
            'x_max': self._offset[0] + half_w,
            'y_min': self._offset[1] - half_h,
            'y_max': self._offset[1] + half_h,
        }

    def set_resolution(self, width, height):
        self.width = width
        self.height = height
        self.center_px = np.array([width / 2, height / 2])

    def pan(self, delta):
        self._offset += np.array(delta, dtype=float)

    def zoom_at(self, factor, math_point=None):
        if math_point is not None:
            math_point = np.array(math_point, dtype=float)
            self._offset = math_point + (self._offset - math_point) / factor
        self._zoom *= factor