import numpy as np


class Color:
    def __init__(self, r=255, g=255, b=255, a=255):
        self.r = int(np.clip(r, 0, 255))
        self.g = int(np.clip(g, 0, 255))
        self.b = int(np.clip(b, 0, 255))
        self.a = int(np.clip(a, 0, 255))

    @classmethod
    def from_hex(cls, hex_str):
        hex_str = hex_str.lstrip('#')
        if len(hex_str) == 6:
            r, g, b = int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16)
            return cls(r, g, b, 255)
        elif len(hex_str) == 8:
            r, g, b, a = int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16), int(hex_str[6:8], 16)
            return cls(r, g, b, a)
        raise ValueError(f"Invalid hex color: #{hex_str}")

    @classmethod
    def from_hsv(cls, h, s, v, a=1.0):
        h = h % 360
        c = v * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = v - c
        if h < 60:
            r1, g1, b1 = c, x, 0
        elif h < 120:
            r1, g1, b1 = x, c, 0
        elif h < 180:
            r1, g1, b1 = 0, c, x
        elif h < 240:
            r1, g1, b1 = 0, x, c
        elif h < 300:
            r1, g1, b1 = x, 0, c
        else:
            r1, g1, b1 = c, 0, x
        return cls(int((r1 + m) * 255), int((g1 + m) * 255), int((b1 + m) * 255), int(a * 255))

    @property
    def rgb(self):
        return (self.r, self.g, self.b)

    @property
    def rgba(self):
        return (self.r, self.g, self.b, self.a)

    @property
    def hex(self):
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"

    def with_alpha(self, alpha):
        return Color(self.r, self.g, self.b, int(alpha * 255))

    def copy(self):
        return Color(self.r, self.g, self.b, self.a)

    def __repr__(self):
        return f"Color({self.r}, {self.g}, {self.b}, {self.a})"

    def __eq__(self, other):
        if isinstance(other, Color):
            return self.rgba == other.rgba
        return False


def interpolate_color(c1, c2, t):
    t = np.clip(t, 0.0, 1.0)
    return Color(
        int(c1.r + (c2.r - c1.r) * t),
        int(c1.g + (c2.g - c1.g) * t),
        int(c1.b + (c2.b - c1.b) * t),
        int(c1.a + (c2.a - c1.a) * t),
    )


def color_gradient(colors, n):
    if n <= 1:
        return [colors[0].copy()]
    result = []
    for i in range(n):
        t = i / (n - 1)
        scaled = t * (len(colors) - 1)
        idx = int(scaled)
        frac = scaled - idx
        if idx >= len(colors) - 1:
            result.append(colors[-1].copy())
        else:
            result.append(interpolate_color(colors[idx], colors[idx + 1], frac))
    return result


def hex_to_rgb(hex_str):
    return Color.from_hex(hex_str).rgb


def rgb_to_hex(r, g, b):
    return f"#{r:02x}{g:02x}{b:02x}"


# ── Manim-style color palette ──

WHITE       = Color.from_hex("#FFFFFF")
BLACK       = Color.from_hex("#000000")

GREY_A      = Color.from_hex("#DDDDDD")
GREY_B      = Color.from_hex("#BBBBBB")
GREY_C      = Color.from_hex("#888888")
GREY_D      = Color.from_hex("#555555")
GREY_E      = Color.from_hex("#333333")
GREY        = GREY_C
GRAY        = GREY

RED_A       = Color.from_hex("#FF8080")
RED_B       = Color.from_hex("#FF6666")
RED_C       = Color.from_hex("#FC6255")
RED_D       = Color.from_hex("#E65A4C")
RED_E       = Color.from_hex("#CF5044")
RED         = RED_C

GREEN_A     = Color.from_hex("#C9E2AE")
GREEN_B     = Color.from_hex("#A6CF8C")
GREEN_C     = Color.from_hex("#83C167")
GREEN_D     = Color.from_hex("#77B05D")
GREEN_E     = Color.from_hex("#699C52")
GREEN       = GREEN_C

BLUE_A      = Color.from_hex("#C7E9F1")
BLUE_B      = Color.from_hex("#9CDCEB")
BLUE_C      = Color.from_hex("#58C4DD")
BLUE_D      = Color.from_hex("#29ABCA")
BLUE_E      = Color.from_hex("#236B8E")
BLUE        = BLUE_C

YELLOW_A    = Color.from_hex("#FFF1B6")
YELLOW_B    = Color.from_hex("#FFEA94")
YELLOW_C    = Color.from_hex("#FFFF00")
YELLOW_D    = Color.from_hex("#F4D345")
YELLOW_E    = Color.from_hex("#E8C11C")
YELLOW      = YELLOW_C

TEAL_A      = Color.from_hex("#ACEAD7")
TEAL_B      = Color.from_hex("#76DDC0")
TEAL_C      = Color.from_hex("#5CD0B3")
TEAL_D      = Color.from_hex("#55C1A7")
TEAL_E      = Color.from_hex("#49A88F")
TEAL        = TEAL_C

PURPLE_A    = Color.from_hex("#CAA3E8")
PURPLE_B    = Color.from_hex("#B189C6")
PURPLE_C    = Color.from_hex("#9A72AC")
PURPLE_D    = Color.from_hex("#715582")
PURPLE_E    = Color.from_hex("#644172")
PURPLE      = PURPLE_C

MAROON_A    = Color.from_hex("#ECABC1")
MAROON_B    = Color.from_hex("#EC92AB")
MAROON_C    = Color.from_hex("#C55F73")
MAROON_D    = Color.from_hex("#A24D61")
MAROON_E    = Color.from_hex("#94424F")
MAROON      = MAROON_C

ORANGE      = Color.from_hex("#FF862F")
PINK        = Color.from_hex("#D147BD")
GOLD        = Color.from_hex("#F0AC5F")

BACKGROUND_COLOR = Color.from_hex("#1C1C2E")

UP    = np.array([0.0, 1.0])
DOWN  = np.array([0.0, -1.0])
LEFT  = np.array([-1.0, 0.0])
RIGHT = np.array([1.0, 0.0])
ORIGIN = np.array([0.0, 0.0])

UL = UP + LEFT
UR = UP + RIGHT
DL = DOWN + LEFT
DR = DOWN + RIGHT
