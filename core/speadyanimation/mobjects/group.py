import numpy as np
from mobjects.mobject import Mobject


class Group(Mobject):
    def __init__(self, *mobjects, **kwargs):
        super().__init__(**kwargs)
        for m in mobjects:
            self.submobjects.append(m)

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

    def get_center(self):
        if not self.submobjects:
            return self.position.copy()
        centers = np.array([m.get_center() for m in self.submobjects])
        return centers.mean(axis=0)

    def get_bounding_box(self):
        if not self.submobjects:
            return (self.position - 0.5, self.position + 0.5)
        bbs = [m.get_bounding_box() for m in self.submobjects]
        mins = np.array([bb[0] for bb in bbs])
        maxs = np.array([bb[1] for bb in bbs])
        return (mins.min(axis=0), maxs.max(axis=0))

    def arrange(self, direction=None, buff=0.25, center=True):
        if direction is None:
            direction = np.array([1.0, 0.0])
        direction = np.array(direction, dtype=float)
        if not self.submobjects:
            return self
        current_pos = self.submobjects[0].get_center().copy()
        for i, m in enumerate(self.submobjects):
            m.move_to(current_pos)
            if i < len(self.submobjects) - 1:
                bb = m.get_bounding_box()
                size = bb[1] - bb[0]
                next_bb = self.submobjects[i + 1].get_bounding_box()
                next_size = next_bb[1] - next_bb[0]
                offset = np.zeros(2)
                for d in range(2):
                    if abs(direction[d]) > 0.01:
                        offset[d] = direction[d] * (size[d] / 2 + next_size[d] / 2 + buff)
                current_pos = current_pos + offset
        if center:
            group_center = self.get_center()
            shift = self.position - group_center
            for m in self.submobjects:
                m.shift(shift)
        return self

    def arrange_in_grid(self, rows=None, cols=None, buff=0.25):
        n = len(self.submobjects)
        if n == 0:
            return self
        if rows is None and cols is None:
            import math
            cols = math.ceil(math.sqrt(n))
            rows = math.ceil(n / cols)
        elif rows is None:
            import math
            rows = math.ceil(n / cols)
        elif cols is None:
            import math
            cols = math.ceil(n / rows)
        max_w = max((m.get_width() for m in self.submobjects), default=1)
        max_h = max((m.get_height() for m in self.submobjects), default=1)
        for idx, m in enumerate(self.submobjects):
            row = idx // cols
            col = idx % cols
            x = self.position[0] + (col - (cols - 1) / 2) * (max_w + buff)
            y = self.position[1] - (row - (rows - 1) / 2) * (max_h + buff)
            m.move_to(np.array([x, y]))
        return self

    def __len__(self):
        return len(self.submobjects)

    def __getitem__(self, idx):
        return self.submobjects[idx]

    def __iter__(self):
        return iter(self.submobjects)


class VGroup(Group):
    pass
