import pygame
import numpy as np
import math
from mobjects.mobject import Mobject
from mobjects.geometry import Line, Arrow, Dot, DashedLine
from utils.color import Color, WHITE, GREY, GREY_D, BLUE, YELLOW, RED, GREEN, ORIGIN
from core.config import Config


class NumberLine(Mobject):
    def __init__(self, x_range=None, length=10, color=None,
                 include_ticks=True, tick_size=0.15,
                 include_numbers=True, font_size=20,
                 include_tip=True, **kwargs):
        super().__init__(color=color or WHITE, **kwargs)
        if x_range is None:
            x_range = [-5, 5, 1]
        self.x_min = x_range[0]
        self.x_max = x_range[1]
        self.x_step = x_range[2] if len(x_range) > 2 else 1
        self.length = length
        self.include_ticks = include_ticks
        self.tick_size = tick_size
        self.include_numbers = include_numbers
        self.font_size = font_size
        self.include_tip = include_tip

    def _val_to_pos(self, val):
        t = (val - self.x_min) / (self.x_max - self.x_min)
        x = self.position[0] - self.length / 2 + t * self.length
        return np.array([x, self.position[1]])

    def draw(self, surface, camera):
        left = self._val_to_pos(self.x_min)
        right = self._val_to_pos(self.x_min + (self.x_max - self.x_min) * self.stroke_proportion)
        px_left = camera.to_pixels(left)
        px_right = camera.to_pixels(right)
        stroke_c = self._get_effective_color()
        sw = max(1, int(self.stroke_width))
        s = self._make_alpha_surface(camera.width, camera.height)
        
        if self.stroke_proportion > 0:
            pygame.draw.line(s, stroke_c, px_left, px_right, sw)
            if self.include_tip and self.stroke_proportion >= 1.0:
                tip_size = int(0.15 * camera.px_per_unit)
                tip_end = camera.to_pixels(self._val_to_pos(self.x_max))
                pygame.draw.polygon(s, stroke_c, [
                    tip_end,
                    (tip_end[0] - tip_size, tip_end[1] - tip_size // 2),
                    (tip_end[0] - tip_size, tip_end[1] + tip_size // 2),
                ])
            if self.include_ticks:
                val = self.x_min
                while val <= self.x_min + (self.x_max - self.x_min) * self.stroke_proportion + 1e-9:
                    pos = self._val_to_pos(val)
                    px = camera.to_pixels(pos)
                    tick_px = int(self.tick_size * camera.px_per_unit)
                    pygame.draw.line(s, stroke_c, (px[0], px[1] - tick_px), (px[0], px[1] + tick_px), sw)
                    val += self.x_step
        surface.blit(s, (0, 0))
        
        if self.include_numbers and self.stroke_proportion >= 1.0:
            try:
                font = pygame.font.SysFont("monospace", self.font_size)
            except Exception:
                font = pygame.font.Font(None, self.font_size)
            if self.opacity > 0:
                val = self.x_min
                while val <= self.x_max + 1e-9:
                    pos = self._val_to_pos(val)
                    px = camera.to_pixels(pos)
                    label = f"{val:g}"
                    text_surf = font.render(label, True, stroke_c[:3])
                    text_surf.set_alpha(int(255 * self.opacity))
                    text_rect = text_surf.get_rect(midtop=(px[0], px[1] + int(self.tick_size * camera.px_per_unit) + 4))
                    surface.blit(text_surf, text_rect)
                    val += self.x_step
        super().draw(surface, camera)


class Axes(Mobject):
    def __init__(self, x_range=None, y_range=None,
                 x_length=10, y_length=6,
                 color=None, include_ticks=True, tick_size=0.1,
                 include_numbers=True, font_size=18,
                 include_tip=True, axis_config=None, **kwargs):
        super().__init__(color=color or WHITE, **kwargs)
        if x_range is None:
            x_range = [-5, 5, 1]
        if y_range is None:
            y_range = [-3, 3, 1]
        self.x_min = x_range[0]
        self.x_max = x_range[1]
        self.x_step = x_range[2] if len(x_range) > 2 else 1
        self.y_min = y_range[0]
        self.y_max = y_range[1]
        self.y_step = y_range[2] if len(y_range) > 2 else 1
        self.x_length = x_length
        self.y_length = y_length
        self.include_ticks = include_ticks
        self.tick_size = tick_size
        self.include_numbers = include_numbers
        self.font_size = font_size
        self.include_tip = include_tip

    def c2p(self, x, y):
        tx = (x - self.x_min) / (self.x_max - self.x_min) if self.x_max != self.x_min else 0.5
        ty = (y - self.y_min) / (self.y_max - self.y_min) if self.y_max != self.y_min else 0.5
        px = self.position[0] - self.x_length / 2 + tx * self.x_length
        py = self.position[1] - self.y_length / 2 + ty * self.y_length
        return np.array([px, py])

    def p2c(self, point):
        point = np.array(point, dtype=float)
        tx = (point[0] - (self.position[0] - self.x_length / 2)) / self.x_length
        ty = (point[1] - (self.position[1] - self.y_length / 2)) / self.y_length
        x = self.x_min + tx * (self.x_max - self.x_min)
        y = self.y_min + ty * (self.y_max - self.y_min)
        return (x, y)

    def coords_to_point(self, x, y):
        return self.c2p(x, y)

    def point_to_coords(self, point):
        return self.p2c(point)

    def draw(self, surface, camera):
        stroke_c = self._get_effective_color()
        sw = max(1, int(self.stroke_width))
        s = self._make_alpha_surface(camera.width, camera.height)
        
        # Draw x-axis
        x_left = self.c2p(self.x_min, 0)
        x_right_val = self.x_min + (self.x_max - self.x_min) * self.stroke_proportion
        x_right = self.c2p(x_right_val, 0)
        px_xl = camera.to_pixels(x_left)
        px_xr = camera.to_pixels(x_right)
        pygame.draw.line(s, stroke_c, px_xl, px_xr, sw)
        
        # Draw y-axis
        y_bottom = self.c2p(0, self.y_min)
        y_top_val = self.y_min + (self.y_max - self.y_min) * self.stroke_proportion
        y_top = self.c2p(0, y_top_val)
        px_yb = camera.to_pixels(y_bottom)
        px_yt = camera.to_pixels(y_top)
        pygame.draw.line(s, stroke_c, px_yb, px_yt, sw)
        
        if self.include_tip and self.stroke_proportion >= 1.0:
            tip_sz = int(0.12 * camera.px_per_unit)
            px_xr_final = camera.to_pixels(self.c2p(self.x_max, 0))
            px_yt_final = camera.to_pixels(self.c2p(0, self.y_max))
            pygame.draw.polygon(s, stroke_c, [
                px_xr_final, (px_xr_final[0] - tip_sz, px_xr_final[1] - tip_sz // 2),
                (px_xr_final[0] - tip_sz, px_xr_final[1] + tip_sz // 2),
            ])
            pygame.draw.polygon(s, stroke_c, [
                px_yt_final, (px_yt_final[0] - tip_sz // 2, px_yt_final[1] + tip_sz),
                (px_yt_final[0] + tip_sz // 2, px_yt_final[1] + tip_sz),
            ])
            
        if self.include_ticks:
            tick_px = int(self.tick_size * camera.px_per_unit)
            val = self.x_min
            while val <= self.x_min + (self.x_max - self.x_min) * self.stroke_proportion + 1e-9:
                if abs(val) > 1e-9:
                    pos = self.c2p(val, 0)
                    px = camera.to_pixels(pos)
                    pygame.draw.line(s, stroke_c, (px[0], px[1] - tick_px), (px[0], px[1] + tick_px), sw)
                val += self.x_step
            val = self.y_min
            while val <= self.y_min + (self.y_max - self.y_min) * self.stroke_proportion + 1e-9:
                if abs(val) > 1e-9:
                    pos = self.c2p(0, val)
                    px = camera.to_pixels(pos)
                    pygame.draw.line(s, stroke_c, (px[0] - tick_px, px[1]), (px[0] + tick_px, px[1]), sw)
                val += self.y_step
        surface.blit(s, (0, 0))
        
        if self.include_numbers and self.stroke_proportion >= 1.0:
            try:
                font = pygame.font.SysFont("monospace", self.font_size)
            except Exception:
                font = pygame.font.Font(None, self.font_size)
            if self.opacity > 0:
                val = self.x_min
                while val <= self.x_max + 1e-9:
                    if abs(val) > 1e-9:
                        pos = self.c2p(val, 0)
                        px = camera.to_pixels(pos)
                        label = f"{val:g}"
                        ts = font.render(label, True, stroke_c[:3])
                        ts.set_alpha(int(255 * self.opacity))
                        tr = ts.get_rect(midtop=(px[0], px[1] + int(self.tick_size * camera.px_per_unit) + 3))
                        surface.blit(ts, tr)
                    val += self.x_step
                val = self.y_min
                while val <= self.y_max + 1e-9:
                    if abs(val) > 1e-9:
                        pos = self.c2p(0, val)
                        px = camera.to_pixels(pos)
                        label = f"{val:g}"
                        ts = font.render(label, True, stroke_c[:3])
                        ts.set_alpha(int(255 * self.opacity))
                        tr = ts.get_rect(midright=(px[0] - int(self.tick_size * camera.px_per_unit) - 5, px[1]))
                        surface.blit(ts, tr)
                    val += self.y_step
        super().draw(surface, camera)

    def get_bounding_box(self):
        bl = self.c2p(self.x_min, self.y_min)
        tr = self.c2p(self.x_max, self.y_max)
        return (bl, tr)

    def get_graph(self, func, x_range=None, color=None, num_points=200, **kwargs):
        return FunctionGraph(func, axes=self, x_range=x_range,
                             color=color, num_points=num_points, **kwargs)


class NumberPlane(Axes):
    def __init__(self, x_range=None, y_range=None,
                 x_length=10, y_length=6,
                 background_line_style=None, **kwargs):
        super().__init__(x_range=x_range, y_range=y_range,
                         x_length=x_length, y_length=y_length, **kwargs)
        self.grid_color = GREY_D
        self.grid_stroke_width = 1
        if background_line_style:
            if 'color' in background_line_style:
                self.grid_color = background_line_style['color']
            if 'stroke_width' in background_line_style:
                self.grid_stroke_width = background_line_style['stroke_width']

    def draw(self, surface, camera):
        grid_c = (self.grid_color.r, self.grid_color.g, self.grid_color.b,
                  int(self.grid_color.a * self.opacity * 0.4))
        gsw = max(1, self.grid_stroke_width)
        s = self._make_alpha_surface(camera.width, camera.height)
        val = self.x_min
        while val <= self.x_max + 1e-9:
            top = self.c2p(val, self.y_max)
            bot = self.c2p(val, self.y_min)
            px_t = camera.to_pixels(top)
            px_b = camera.to_pixels(bot)
            pygame.draw.line(s, grid_c, px_t, px_b, gsw)
            val += self.x_step
        val = self.y_min
        while val <= self.y_max + 1e-9:
            left = self.c2p(self.x_min, val)
            right = self.c2p(self.x_max, val)
            px_l = camera.to_pixels(left)
            px_r = camera.to_pixels(right)
            pygame.draw.line(s, grid_c, px_l, px_r, gsw)
            val += self.y_step
        surface.blit(s, (0, 0))
        super().draw(surface, camera)


class FunctionGraph(Mobject):
    def __init__(self, func, axes=None, x_range=None, color=None,
                 num_points=200, stroke_width=3, **kwargs):
        super().__init__(color=color or YELLOW, stroke_width=stroke_width, **kwargs)
        self.func = func
        self.axes = axes
        self.num_points = num_points
        if x_range is not None:
            self.x_min = x_range[0]
            self.x_max = x_range[1]
        elif axes is not None:
            self.x_min = axes.x_min
            self.x_max = axes.x_max
        else:
            self.x_min = -5
            self.x_max = 5

    def _get_points(self):
        xs = np.linspace(self.x_min, self.x_max, self.num_points)
        points = []
        for x in xs:
            try:
                y = self.func(x)
                if np.isfinite(y):
                    if self.axes:
                        points.append(self.axes.c2p(x, y))
                    else:
                        points.append(np.array([x, y]) + self.position)
            except (ValueError, ZeroDivisionError, OverflowError):
                continue
        return points

    def draw(self, surface, camera):
        points = self._get_points()
        if len(points) < 2:
            return
            
        if self.stroke_proportion < 1.0:
            num_pts = max(2, int(len(points) * self.stroke_proportion))
            points = points[:num_pts]
            
        px_points = [camera.to_pixels(p) for p in points]
        stroke_c = self._get_effective_color()
        sw = max(1, int(self.stroke_width))
        s = self._make_alpha_surface(camera.width, camera.height)
        if self.stroke_proportion > 0:
            pygame.draw.lines(s, stroke_c, False, px_points, sw)
        surface.blit(s, (0, 0))
        super().draw(surface, camera)

    def get_bounding_box(self):
        pts = self._get_points()
        if not pts:
            return (self.position - 1, self.position + 1)
        pts = np.array(pts)
        return (pts.min(axis=0), pts.max(axis=0))


class ParametricGraph(Mobject):
    def __init__(self, func_x, func_y, t_range=None, color=None,
                 num_points=200, stroke_width=3, axes=None, **kwargs):
        super().__init__(color=color or BLUE, stroke_width=stroke_width, **kwargs)
        self.func_x = func_x
        self.func_y = func_y
        self.axes = axes
        if t_range is None:
            t_range = [0, 2 * math.pi]
        self.t_min = t_range[0]
        self.t_max = t_range[1]
        self.num_points = num_points

    def _get_points(self):
        ts = np.linspace(self.t_min, self.t_max, self.num_points)
        points = []
        for t in ts:
            try:
                x = self.func_x(t)
                y = self.func_y(t)
                if np.isfinite(x) and np.isfinite(y):
                    if self.axes:
                        points.append(self.axes.c2p(x, y))
                    else:
                        points.append(np.array([x, y]) + self.position)
            except (ValueError, ZeroDivisionError, OverflowError):
                continue
        return points

    def draw(self, surface, camera):
        points = self._get_points()
        if len(points) < 2:
            return
            
        if self.stroke_proportion < 1.0:
            num_pts = max(2, int(len(points) * self.stroke_proportion))
            points = points[:num_pts]
            
        px_points = [camera.to_pixels(p) for p in points]
        stroke_c = self._get_effective_color()
        sw = max(1, int(self.stroke_width))
        s = self._make_alpha_surface(camera.width, camera.height)
        if self.stroke_proportion > 0:
            pygame.draw.lines(s, stroke_c, False, px_points, sw)
        surface.blit(s, (0, 0))
        super().draw(surface, camera)


class BarChart(Mobject):
    def __init__(self, values, bar_names=None, bar_colors=None,
                 bar_width=0.6, y_range=None, x_length=8, y_length=5,
                 color=None, font_size=18, **kwargs):
        super().__init__(color=color or WHITE, **kwargs)
        self.values = list(values)
        self.bar_names = bar_names or [str(i) for i in range(len(values))]
        self.bar_width = bar_width
        self.x_length = x_length
        self.y_length = y_length
        self.font_size = font_size
        if y_range is None:
            max_val = max(abs(v) for v in values) if values else 1
            self.y_max = max_val * 1.2
            self.y_min = 0
        else:
            self.y_min = y_range[0]
            self.y_max = y_range[1]
        if bar_colors is None:
            default_colors = [BLUE, RED, GREEN, YELLOW, Color.from_hex("#FF862F"),
                              Color.from_hex("#D147BD"), Color.from_hex("#5CD0B3")]
            self.bar_colors = [default_colors[i % len(default_colors)] for i in range(len(values))]
        else:
            self.bar_colors = bar_colors
        self._bar_progress = 1.0

    def set_bar_progress(self, progress):
        self._bar_progress = max(0.0, min(1.0, progress))

    def draw(self, surface, camera):
        if not self.values:
            return
        n = len(self.values)
        total_width = self.x_length
        bar_slot = total_width / n
        stroke_c = self._get_effective_color()
        sw = max(1, int(self.stroke_width))
        s = self._make_alpha_surface(camera.width, camera.height)
        try:
            font = pygame.font.SysFont("monospace", self.font_size)
        except Exception:
            font = pygame.font.Font(None, self.font_size)
        base_y = self.position[1] - self.y_length / 2
        top_y = self.position[1] + self.y_length / 2
        base_left = self.position[0] - self.x_length / 2
        px_base_left = camera.to_pixels(np.array([base_left, base_y]))
        px_base_right = camera.to_pixels(np.array([base_left + self.x_length, base_y]))
        pygame.draw.line(s, stroke_c, px_base_left, px_base_right, sw)
        for i, val in enumerate(self.values):
            bar_center_x = base_left + (i + 0.5) * bar_slot
            bar_h = (val * self._bar_progress / (self.y_max - self.y_min)) * self.y_length if (self.y_max - self.y_min) != 0 else 0
            bar_bottom = np.array([bar_center_x - self.bar_width / 2, base_y])
            bar_top = np.array([bar_center_x + self.bar_width / 2, base_y + bar_h])
            px_bl = camera.to_pixels(bar_bottom)
            px_tr = camera.to_pixels(bar_top)
            rect = pygame.Rect(
                min(px_bl[0], px_tr[0]),
                min(px_bl[1], px_tr[1]),
                abs(px_tr[0] - px_bl[0]),
                abs(px_tr[1] - px_bl[1])
            )
            if rect.width > 0 and rect.height > 0:
                bc = self.bar_colors[i]
                bar_color = (bc.r, bc.g, bc.b, int(bc.a * self.opacity * self.fill_opacity if self.fill_opacity > 0 else bc.a * self.opacity))
                pygame.draw.rect(s, bar_color, rect)
                pygame.draw.rect(s, stroke_c, rect, max(1, sw // 2))
            name_pos = np.array([bar_center_x, base_y])
            px_name = camera.to_pixels(name_pos)
            if i < len(self.bar_names):
                ts = font.render(str(self.bar_names[i]), True, stroke_c[:3])
                ts.set_alpha(int(255 * self.opacity))
                tr = ts.get_rect(midtop=(px_name[0], px_name[1] + 5))
                s.blit(ts, tr)
            if bar_h != 0:
                val_pos = np.array([bar_center_x, base_y + bar_h])
                px_val = camera.to_pixels(val_pos)
                val_text = f"{val * self._bar_progress:.1f}"
                vs = font.render(val_text, True, stroke_c[:3])
                vs.set_alpha(int(255 * self.opacity))
                vr = vs.get_rect(midbottom=(px_val[0], px_val[1] - 3))
                s.blit(vs, vr)
        surface.blit(s, (0, 0))
        super().draw(surface, camera)
