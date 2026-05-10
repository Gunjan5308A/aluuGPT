import pygame
from core.config import Config


class Renderer:
    def __init__(self, camera):
        self.camera = camera
        self._background_color = Config.BACKGROUND_COLOR.rgb

    @property
    def background_color(self):
        return self._background_color

    @background_color.setter
    def background_color(self, color):
        if hasattr(color, 'rgb'):
            self._background_color = color.rgb
        else:
            self._background_color = tuple(color[:3])

    def render_frame(self, surface, mobjects):
        surface.fill(self._background_color)
        sorted_mobjects = sorted(mobjects, key=lambda m: m.z_index)
        for mobject in sorted_mobjects:
            mobject.draw(surface, self.camera)

    def capture_frame(self, surface):
        return pygame.image.tobytes(surface, 'RGB')
