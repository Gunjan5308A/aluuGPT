import pygame
import pygame.gfxdraw
import numpy as np
import math
from mobjects.mobject import Mobject
from utils.color import Color, WHITE


class Dot(Mobject):
    def __init__(self, point=None, radius=0.08, color=None, **kwargs):
        super().__init__(color=color or WHITE, fill_opacity=1.0, **kwargs)
        if point is not None:
            self.position = np.array(point, dtype=float)
        self.radius = radius

    def draw(self, surface, camera):
        px = camera.to_pixels(self.position)
        pr = max(1, int(self.radius * camera.px_per_unit))
        color = self._get_effective_color()
        if self.opacity < 1.0 or color[3] < 255:
            s = self._make_alpha_surface(pr * 2 + 2, pr * 2 + 2)
            pygame.draw.circle(s, color, (pr + 1, pr + 1), pr)
            surface.blit(s, (px[0] - pr - 1, px[1] - pr - 1))
        else:
            pygame.draw.circle(surface, color[:3], px, pr)
        super().draw(surface, camera)

    def get_bounding_box(self):
        r = self.radius
        return (self.position - r, self.position + r)


class Circle(Mobject):
    def __init__(self, radius=1.0, color=None, fill_color=None,
                 fill_opacity=0.0, **kwargs):
        super().__init__(color=color, fill_color=fill_color,
                         fill_opacity=fill_opacity, **kwargs)
        self.radius = radius

    def _apply_scale(self, factor, about_point):
        self.radius *= abs(factor)

    def draw(self, surface, camera):
        px = camera.to_pixels(self.position)
        pr = max(1, int(self.radius * camera.px_per_unit))
        diameter = pr * 2 + 4
        s = self._make_alpha_surface(diameter, diameter)
        center = (pr + 2, pr + 2)
        
        # If stroke_proportion is less than 1, we draw an arc instead of a circle
        if self.fill_opacity > 0 and self.stroke_proportion >= 1.0:
            fill_c = self._get_effective_fill_color()
            pygame.draw.circle(s, fill_c, center, pr)
            
        if self.stroke_width > 0 and self.opacity > 0 and self.stroke_proportion > 0:
            stroke_c = self._get_effective_color()
            sw = max(1, int(self.stroke_width))
            if self.stroke_proportion >= 1.0:
                pygame.draw.circle(s, stroke_c, center, pr, sw)
            else:
                rect = pygame.Rect(center[0] - pr, center[1] - pr, pr * 2, pr * 2)
                # pygame arc uses radians, start at 0 and go to 2pi * proportion
                pygame.draw.arc(s, stroke_c, rect, 0, 2 * math.pi * self.stroke_proportion, sw)
        surface.blit(s, (px[0] - pr - 2, px[1] - pr - 2))
        super().draw(surface, camera)

    def get_bounding_box(self):
        r = self.radius
        return (self.position - r, self.position + r)

    def point_at_angle(self, angle):
        return self.position + self.radius * np.array([math.cos(angle), math.sin(angle)])


class Arc(Mobject):
    def __init__(self, start_angle=0, angle=math.pi / 2, radius=1.0,
                 color=None, num_segments=64, **kwargs):
        super().__init__(color=color, **kwargs)
        self.start_angle = start_angle
        self.angle = angle
        self.radius = radius
        self.num_segments = num_segments

    def _apply_scale(self, factor, about_point):
        self.radius *= abs(factor)

    def _get_arc_points(self):
        angles = np.linspace(self.start_angle, self.start_angle + self.angle, self.num_segments)
        return [self.position + self.radius * np.array([math.cos(a), math.sin(a)]) for a in angles]

    def draw(self, surface, camera):
        points = self._get_arc_points()
        if len(points) < 2:
            return
        
        # Clip points based on stroke_proportion
        if self.stroke_proportion < 1.0:
            num_pts = max(2, int(len(points) * self.stroke_proportion))
            points = points[:num_pts]
            
        px_points = [camera.to_pixels(p) for p in points]
        if self.opacity > 0 and self.stroke_width > 0 and self.stroke_proportion > 0:
            stroke_c = self._get_effective_color()
            sw = max(1, int(self.stroke_width))
            s = self._make_alpha_surface(camera.width, camera.height)
            pygame.draw.lines(s, stroke_c, False, px_points, sw)
            surface.blit(s, (0, 0))
        super().draw(surface, camera)

    def get_bounding_box(self):
        pts = self._get_arc_points()
        if not pts:
            return (self.position - self.radius, self.position + self.radius)
        pts = np.array(pts)
        return (pts.min(axis=0), pts.max(axis=0))


class Line(Mobject):
    def __init__(self, start=None, end=None, color=None, **kwargs):
        super().__init__(color=color, **kwargs)
        self.start = np.array(start if start is not None else [-1, 0], dtype=float)
        self.end = np.array(end if end is not None else [1, 0], dtype=float)
        self.position = (self.start + self.end) / 2

    def _apply_scale(self, factor, about_point):
        about_point = np.array(about_point, dtype=float)
        self.start = about_point + factor * (self.start - about_point)
        self.end = about_point + factor * (self.end - about_point)

    def _apply_rotation(self, angle, about_point):
        about_point = np.array(about_point, dtype=float)
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        for attr in ['start', 'end']:
            pt = getattr(self, attr)
            offset = pt - about_point
            rotated = np.array([cos_a * offset[0] - sin_a * offset[1],
                                sin_a * offset[0] + cos_a * offset[1]])
            setattr(self, attr, about_point + rotated)

    def shift(self, vector):
        vector = np.array(vector, dtype=float)
        self.start += vector
        self.end += vector
        self.position = (self.start + self.end) / 2
        for sub in self.submobjects:
            sub.shift(vector)
        return self

    def move_to(self, point):
        point = np.array(point, dtype=float)
        shift_vec = point - self.get_center()
        self.shift(shift_vec)
        return self

    def get_center(self):
        return (self.start + self.end) / 2

    def get_length(self):
        return np.linalg.norm(self.end - self.start)

    def get_angle(self):
        diff = self.end - self.start
        return math.atan2(diff[1], diff[0])

    def get_unit_vector(self):
        diff = self.end - self.start
        norm = np.linalg.norm(diff)
        if norm == 0:
            return np.array([1.0, 0.0])
        return diff / norm

    def draw(self, surface, camera):
        start = self.start
        end = self.start + (self.end - self.start) * self.stroke_proportion
        
        px_start = camera.to_pixels(start)
        px_end = camera.to_pixels(end)
        if self.opacity > 0 and self.stroke_width > 0 and self.stroke_proportion > 0:
            stroke_c = self._get_effective_color()
            sw = max(1, int(self.stroke_width))
            s = self._make_alpha_surface(camera.width, camera.height)
            pygame.draw.line(s, stroke_c, px_start, px_end, sw)
            surface.blit(s, (0, 0))
        super().draw(surface, camera)

    def get_bounding_box(self):
        min_pt = np.minimum(self.start, self.end)
        max_pt = np.maximum(self.start, self.end)
        return (min_pt, max_pt)


class Arrow(Line):
    def __init__(self, start=None, end=None, color=None,
                 tip_length=0.25, tip_width=0.15, **kwargs):
        super().__init__(start=start, end=end, color=color, **kwargs)
        self.tip_length = tip_length
        self.tip_width = tip_width

    def _apply_scale(self, factor, about_point):
        super()._apply_scale(factor, about_point)
        self.tip_length *= abs(factor)
        self.tip_width *= abs(factor)

    def draw(self, surface, camera):
        px_start = camera.to_pixels(self.start)
        px_end = camera.to_pixels(self.end)
        stroke_c = self._get_effective_color()
        sw = max(1, int(self.stroke_width))
        s = self._make_alpha_surface(camera.width, camera.height)
        pygame.draw.line(s, stroke_c, px_start, px_end, sw)
        direction = self.get_unit_vector()
        perp = np.array([-direction[1], direction[0]])
        tip_base = self.end - direction * self.tip_length
        tip_left = tip_base + perp * self.tip_width
        tip_right = tip_base - perp * self.tip_width
        tip_points = [
            camera.to_pixels(self.end),
            camera.to_pixels(tip_left),
            camera.to_pixels(tip_right),
        ]
        pygame.draw.polygon(s, stroke_c, tip_points)
        surface.blit(s, (0, 0))
        for sub in self.submobjects:
            sub.draw(surface, camera)


class DashedLine(Line):
    def __init__(self, start=None, end=None, color=None,
                 dash_length=0.15, gap_length=0.1, **kwargs):
        super().__init__(start=start, end=end, color=color, **kwargs)
        self.dash_length = dash_length
        self.gap_length = gap_length

    def draw(self, surface, camera):
        stroke_c = self._get_effective_color()
        sw = max(1, int(self.stroke_width))
        s = self._make_alpha_surface(camera.width, camera.height)
        total_length = self.get_length()
        direction = self.get_unit_vector()
        segment = self.dash_length + self.gap_length
        dist = 0.0
        while dist < total_length:
            d_start = self.start + direction * dist
            d_end_dist = min(dist + self.dash_length, total_length)
            d_end = self.start + direction * d_end_dist
            px_s = camera.to_pixels(d_start)
            px_e = camera.to_pixels(d_end)
            pygame.draw.line(s, stroke_c, px_s, px_e, sw)
            dist += segment
        surface.blit(s, (0, 0))
        for sub in self.submobjects:
            sub.draw(surface, camera)


class Rectangle(Mobject):
    def __init__(self, width=2.0, height=1.0, color=None, fill_color=None,
                 fill_opacity=0.0, corner_radius=0, **kwargs):
        super().__init__(color=color, fill_color=fill_color,
                         fill_opacity=fill_opacity, **kwargs)
        self.width = width
        self.height = height
        self.corner_radius = corner_radius

    def _apply_scale(self, factor, about_point):
        self.width *= abs(factor)
        self.height *= abs(factor)
        self.corner_radius *= abs(factor)

    def _get_corners(self):
        hw, hh = self.width / 2, self.height / 2
        corners = np.array([
            [-hw, -hh], [hw, -hh], [hw, hh], [-hw, hh]
        ], dtype=float)
        if self._angle != 0:
            cos_a, sin_a = math.cos(self._angle), math.sin(self._angle)
            rotated = np.zeros_like(corners)
            for i, c in enumerate(corners):
                rotated[i] = [cos_a * c[0] - sin_a * c[1],
                              sin_a * c[0] + cos_a * c[1]]
            corners = rotated
        return corners + self.position

    def draw(self, surface, camera):
        corners = self._get_corners()
        # For Rectangle, drawing proportion is a bit complex, 
        # let's treat it as a path of 4 lines if proportion < 1
        if self.stroke_proportion < 1.0:
            # Create a path of the rectangle boundary
            path = [corners[0], corners[1], corners[2], corners[3], corners[0]]
            num_segments = 4
            target_dist = self.stroke_proportion * num_segments
            idx = int(target_dist)
            remainder = target_dist - idx
            
            if idx >= 4:
                final_pts = path
            else:
                final_pts = path[:idx + 1]
                if remainder > 0:
                    last_seg_start = path[idx]
                    last_seg_end = path[idx+1]
                    interp_pt = last_seg_start + (last_seg_end - last_seg_start) * remainder
                    final_pts.append(interp_pt)
            
            px_points = [camera.to_pixels(p) for p in final_pts]
            s = self._make_alpha_surface(camera.width, camera.height)
            if self.opacity > 0 and self.stroke_width > 0:
                stroke_c = self._get_effective_color()
                sw = max(1, int(self.stroke_width))
                if len(px_points) >= 2:
                    pygame.draw.lines(s, stroke_c, False, px_points, sw)
            surface.blit(s, (0, 0))
        else:
            px_corners = [camera.to_pixels(c) for c in corners]
            s = self._make_alpha_surface(camera.width, camera.height)
            if self.fill_opacity > 0:
                fill_c = self._get_effective_fill_color()
                pygame.draw.polygon(s, fill_c, px_corners)
            if self.stroke_width > 0 and self.opacity > 0:
                stroke_c = self._get_effective_color()
                sw = max(1, int(self.stroke_width))
                pygame.draw.polygon(s, stroke_c, px_corners, sw)
            surface.blit(s, (0, 0))
        super().draw(surface, camera)

    def get_bounding_box(self):
        corners = self._get_corners()
        return (corners.min(axis=0), corners.max(axis=0))


class Square(Rectangle):
    def __init__(self, side_length=2.0, **kwargs):
        super().__init__(width=side_length, height=side_length, **kwargs)
        self.side_length = side_length

    def _apply_scale(self, factor, about_point):
        super()._apply_scale(factor, about_point)
        self.side_length *= abs(factor)


class Polygon(Mobject):
    def __init__(self, *vertices, color=None, fill_color=None,
                 fill_opacity=0.0, **kwargs):
        super().__init__(color=color, fill_color=fill_color,
                         fill_opacity=fill_opacity, **kwargs)
        self.vertices = np.array(vertices, dtype=float)
        if len(self.vertices) > 0:
            self.position = self.vertices.mean(axis=0)

    def _apply_scale(self, factor, about_point):
        about_point = np.array(about_point, dtype=float)
        self.vertices = about_point + factor * (self.vertices - about_point)

    def _apply_rotation(self, angle, about_point):
        about_point = np.array(about_point, dtype=float)
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        for i, v in enumerate(self.vertices):
            offset = v - about_point
            self.vertices[i] = about_point + np.array([
                cos_a * offset[0] - sin_a * offset[1],
                sin_a * offset[0] + cos_a * offset[1],
            ])

    def shift(self, vector):
        vector = np.array(vector, dtype=float)
        self.vertices += vector
        self.position = self.vertices.mean(axis=0)
        for sub in self.submobjects:
            sub.shift(vector)
        return self

    def move_to(self, point):
        point = np.array(point, dtype=float)
        shift_vec = point - self.get_center()
        self.shift(shift_vec)
        return self

    def get_center(self):
        return self.vertices.mean(axis=0)

    def draw(self, surface, camera):
        if len(self.vertices) < 3:
            return
            
        if self.stroke_proportion < 1.0:
            # Similar to Rectangle, draw boundary path
            path = list(self.vertices) + [self.vertices[0]]
            num_segments = len(self.vertices)
            target_dist = self.stroke_proportion * num_segments
            idx = int(target_dist)
            remainder = target_dist - idx
            
            if idx >= num_segments:
                final_pts = path
            else:
                final_pts = path[:idx + 1]
                if remainder > 0:
                    last_seg_start = path[idx]
                    last_seg_end = path[idx+1]
                    interp_pt = last_seg_start + (last_seg_end - last_seg_start) * remainder
                    final_pts.append(interp_pt)
            
            px_points = [camera.to_pixels(p) for p in final_pts]
            s = self._make_alpha_surface(camera.width, camera.height)
            if self.opacity > 0 and self.stroke_width > 0:
                stroke_c = self._get_effective_color()
                sw = max(1, int(self.stroke_width))
                if len(px_points) >= 2:
                    pygame.draw.lines(s, stroke_c, False, px_points, sw)
            surface.blit(s, (0, 0))
        else:
            px_verts = [camera.to_pixels(v) for v in self.vertices]
            s = self._make_alpha_surface(camera.width, camera.height)
            if self.fill_opacity > 0:
                fill_c = self._get_effective_fill_color()
                pygame.draw.polygon(s, fill_c, px_verts)
            if self.stroke_width > 0 and self.opacity > 0:
                stroke_c = self._get_effective_color()
                sw = max(1, int(self.stroke_width))
                pygame.draw.polygon(s, stroke_c, px_verts, sw)
            surface.blit(s, (0, 0))
        super().draw(surface, camera)

    def get_bounding_box(self):
        return (self.vertices.min(axis=0), self.vertices.max(axis=0))


class RegularPolygon(Polygon):
    def __init__(self, n=6, radius=1.0, start_angle=math.pi / 2, **kwargs):
        self._n = n
        self._poly_radius = radius
        angles = [start_angle + 2 * math.pi * i / n for i in range(n)]
        vertices = [np.array([radius * math.cos(a), radius * math.sin(a)]) for a in angles]
        super().__init__(*vertices, **kwargs)


class Triangle(RegularPolygon):
    def __init__(self, **kwargs):
        super().__init__(n=3, **kwargs)


class Annulus(Mobject):
    def __init__(self, inner_radius=0.5, outer_radius=1.0, color=None,
                 fill_color=None, fill_opacity=1.0, **kwargs):
        super().__init__(color=color, fill_color=fill_color,
                         fill_opacity=fill_opacity, **kwargs)
        self.inner_radius = inner_radius
        self.outer_radius = outer_radius

    def _apply_scale(self, factor, about_point):
        self.inner_radius *= abs(factor)
        self.outer_radius *= abs(factor)

    def draw(self, surface, camera):
        px = camera.to_pixels(self.position)
        pr_outer = max(1, int(self.outer_radius * camera.px_per_unit))
        pr_inner = max(1, int(self.inner_radius * camera.px_per_unit))
        diameter = pr_outer * 2 + 4
        s = self._make_alpha_surface(diameter, diameter)
        center = (pr_outer + 2, pr_outer + 2)
        if self.fill_opacity > 0:
            fill_c = self._get_effective_fill_color()
            pygame.draw.circle(s, fill_c, center, pr_outer)
            pygame.draw.circle(s, (0, 0, 0, 0), center, pr_inner)
        if self.stroke_width > 0 and self.opacity > 0:
            stroke_c = self._get_effective_color()
            sw = max(1, int(self.stroke_width))
            pygame.draw.circle(s, stroke_c, center, pr_outer, sw)
            pygame.draw.circle(s, stroke_c, center, pr_inner, sw)
        surface.blit(s, (px[0] - pr_outer - 2, px[1] - pr_outer - 2))
        super().draw(surface, camera)

    def get_bounding_box(self):
        r = self.outer_radius
        return (self.position - r, self.position + r)


class PointCloud(Mobject):
    def __init__(self, points=None, color=None, dot_radius=0.04, **kwargs):
        super().__init__(color=color, **kwargs)
        self.points = np.array(points if points is not None else [], dtype=float)
        self.dot_radius = dot_radius

    def draw(self, surface, camera):
        pr = max(1, int(self.dot_radius * camera.px_per_unit))
        color = self._get_effective_color()
        for pt in self.points:
            px = camera.to_pixels(pt + self.position)
            pygame.draw.circle(surface, color[:3], px, pr)
        super().draw(surface, camera)

    def shift(self, vector):
        self.position += np.array(vector, dtype=float)
        return self