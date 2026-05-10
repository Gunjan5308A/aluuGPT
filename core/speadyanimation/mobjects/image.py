import pygame
import numpy as np
from mobjects.mobject import Mobject
from utils.color import WHITE
from core.config import Config


class ImageMobject(Mobject):
    def __init__(self, filename, width=None, height=None, **kwargs):
        super().__init__(**kwargs)
        self.filename = filename
        self._original_surface = None
        self._display_surface = None
        self._target_width = width
        self._target_height = height
        self._load()

    def _load(self):
        try:
            self._original_surface = pygame.image.load(self.filename).convert_alpha()
            if self._target_width or self._target_height:
                ow, oh = self._original_surface.get_size()
                if self._target_width and not self._target_height:
                    scale = (self._target_width * Config.PIXEL_PER_UNIT) / ow
                    nw = int(ow * scale)
                    nh = int(oh * scale)
                elif self._target_height and not self._target_width:
                    scale = (self._target_height * Config.PIXEL_PER_UNIT) / oh
                    nw = int(ow * scale)
                    nh = int(oh * scale)
                else:
                    nw = int(self._target_width * Config.PIXEL_PER_UNIT)
                    nh = int(self._target_height * Config.PIXEL_PER_UNIT)
                self._display_surface = pygame.transform.smoothscale(self._original_surface, (nw, nh))
            else:
                self._display_surface = self._original_surface
        except (pygame.error, FileNotFoundError) as e:
            print(f"[ImageMobject] Could not load {self.filename}: {e}")
            self._display_surface = pygame.Surface((64, 64), pygame.SRCALPHA)
            self._display_surface.fill((255, 0, 255, 128))

    def draw(self, surface, camera):
        if self._display_surface is None:
            return
        px = camera.to_pixels(self.position)
        disp = self._display_surface
        if self.opacity < 1.0:
            disp = disp.copy()
            disp.set_alpha(int(255 * self.opacity))
        rect = disp.get_rect(center=px)
        surface.blit(disp, rect)
        super().draw(surface, camera)

    def get_bounding_box(self):
        if self._display_surface is None:
            return (self.position - 0.5, self.position + 0.5)
        w = self._display_surface.get_width() / Config.PIXEL_PER_UNIT
        h = self._display_surface.get_height() / Config.PIXEL_PER_UNIT
        half = np.array([w / 2, h / 2])
        return (self.position - half, self.position + half)
