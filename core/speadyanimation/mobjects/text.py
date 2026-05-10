import os
import tempfile

_MPLCONFIGDIR = os.path.join(tempfile.gettempdir(), "speadyanimation-mpl")
os.makedirs(_MPLCONFIGDIR, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", _MPLCONFIGDIR)

import pygame
import numpy as np
from mobjects.mobject import Mobject
from utils.color import Color, WHITE
from core.config import Config


class Text(Mobject):
    def __init__(self, text, font_size=None, color=None, font_name=None,
                 bold=False, italic=False, **kwargs):
        super().__init__(color=color or WHITE, **kwargs)
        self.text = text
        self.font_size = font_size or Config.DEFAULT_FONT_SIZE
        self.font_name = font_name
        self.bold = bold
        self.italic = italic
        self._cached_surface = None
        self._cache_key = None

    def _get_font(self):
        try:
            if self.font_name:
                return pygame.font.SysFont(self.font_name, self.font_size, bold=self.bold, italic=self.italic)
            return pygame.font.SysFont("dejavusans", self.font_size, bold=self.bold, italic=self.italic)
        except Exception:
            return pygame.font.Font(None, self.font_size)

    def _render_text(self):
        key = (self.text, self.font_size, self.font_name, self.bold, self.italic, self.color.rgb)
        if self._cache_key == key and self._cached_surface is not None:
            return self._cached_surface
        font = self._get_font()
        color_rgb = self.color.rgb
        self._cached_surface = font.render(self.text, True, color_rgb)
        self._cache_key = key
        return self._cached_surface

    def draw(self, surface, camera):
        text_surf = self._render_text()
        if self.opacity < 1.0:
            text_surf = text_surf.copy()
            text_surf.set_alpha(int(255 * self.opacity))
        px = camera.to_pixels(self.position)
        rect = text_surf.get_rect(center=px)
        surface.blit(text_surf, rect)
        super().draw(surface, camera)

    def get_bounding_box(self):
        text_surf = self._render_text()
        w = text_surf.get_width() / (Config.PIXEL_PER_UNIT)
        h = text_surf.get_height() / (Config.PIXEL_PER_UNIT)
        half = np.array([w / 2, h / 2])
        return (self.position - half, self.position + half)

    def set_text(self, text):
        self.text = text
        self._cache_key = None
        return self

    def __getstate__(self):
        state = self.__dict__.copy()
        state["_cached_surface"] = None
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)


class MathTex(Mobject):
    def __init__(self, tex_string, font_size=None, color=None, **kwargs):
        super().__init__(color=color or WHITE, **kwargs)
        self.tex_string = tex_string
        self.font_size = font_size or Config.DEFAULT_FONT_SIZE
        self._cached_surface = None
        self._cache_key = None

    def _render_tex(self):
        key = (self.tex_string, self.font_size, self.color.rgb)
        if self._cache_key == key and self._cached_surface is not None:
            return self._cached_surface
        try:
            from matplotlib import mathtext
            import matplotlib
            matplotlib.use('Agg')
            from io import BytesIO
            import matplotlib.pyplot as plt
            fig = plt.figure(figsize=(0.01, 0.01))
            fig.patch.set_alpha(0)
            fig.text(0, 0, f"${self.tex_string}$",
                     fontsize=self.font_size,
                     color=[c / 255.0 for c in self.color.rgb])
            buf = BytesIO()
            fig.savefig(buf, format='png', dpi=150, transparent=True,
                        bbox_inches='tight', pad_inches=0.05)
            plt.close(fig)
            buf.seek(0)
            self._cached_surface = pygame.image.load(buf, "png")
        except ImportError:
            font = pygame.font.Font(None, self.font_size)
            self._cached_surface = font.render(self.tex_string, True, self.color.rgb)
        self._cache_key = key
        return self._cached_surface

    def draw(self, surface, camera):
        tex_surf = self._render_tex()
        if self.opacity < 1.0:
            tex_surf = tex_surf.copy()
            tex_surf.set_alpha(int(255 * self.opacity))
        px = camera.to_pixels(self.position)
        rect = tex_surf.get_rect(center=px)
        surface.blit(tex_surf, rect)
        super().draw(surface, camera)

    def get_bounding_box(self):
        tex_surf = self._render_tex()
        w = tex_surf.get_width() / Config.PIXEL_PER_UNIT
        h = tex_surf.get_height() / Config.PIXEL_PER_UNIT
        half = np.array([w / 2, h / 2])
        return (self.position - half, self.position + half)

    def __getstate__(self):
        state = self.__dict__.copy()
        state["_cached_surface"] = None
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)


class Paragraph(Mobject):
    def __init__(self, *lines, font_size=None, color=None, line_spacing=1.5,
                 alignment="center", **kwargs):
        super().__init__(color=color or WHITE, **kwargs)
        self.lines = list(lines)
        self.font_size = font_size or Config.DEFAULT_FONT_SIZE
        self.line_spacing = line_spacing
        self.alignment = alignment
        self._text_objects = []
        self._rebuild()

    def _rebuild(self):
        self._text_objects = []
        total_height = 0
        line_h = self.font_size / Config.PIXEL_PER_UNIT * self.line_spacing
        n = len(self.lines)
        start_y = self.position[1] + (n - 1) * line_h / 2
        for i, line in enumerate(self.lines):
            t = Text(line, font_size=self.font_size, color=self.color)
            t.position = np.array([self.position[0], start_y - i * line_h])
            t.opacity = self.opacity
            self._text_objects.append(t)

    def draw(self, surface, camera):
        for t in self._text_objects:
            t.opacity = self.opacity
            t.draw(surface, camera)
        super().draw(surface, camera)
