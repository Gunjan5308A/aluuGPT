from utils.color import Color, BACKGROUND_COLOR


class Config:
    WIDTH = 1280
    HEIGHT = 720
    FPS = 60
    BACKGROUND_COLOR = BACKGROUND_COLOR
    PIXEL_PER_UNIT = 64
    DEFAULT_STROKE_WIDTH = 4
    DEFAULT_FONT_SIZE = 36
    DEFAULT_MOBJECT_COLOR = Color.from_hex("#FFFFFF")
    FRAME_X_RADIUS = 1280 / (2 * 64)
    FRAME_Y_RADIUS = 720 / (2 * 64)

    @classmethod
    def set_quality(cls, quality):
        presets = {
            "low":    (854, 480, 30),
            "medium": (1280, 720, 30),
            "high":   (1920, 1080, 60),
            "4k":     (3840, 2160, 60),
        }
        if quality not in presets:
            raise ValueError(f"Unknown quality: {quality}. Choose from {list(presets.keys())}")
        cls.WIDTH, cls.HEIGHT, cls.FPS = presets[quality]
        cls.FRAME_X_RADIUS = cls.WIDTH / (2 * cls.PIXEL_PER_UNIT)
        cls.FRAME_Y_RADIUS = cls.HEIGHT / (2 * cls.PIXEL_PER_UNIT)

    @classmethod
    def set_resolution(cls, width, height):
        cls.WIDTH = width
        cls.HEIGHT = height
        cls.FRAME_X_RADIUS = width / (2 * cls.PIXEL_PER_UNIT)
        cls.FRAME_Y_RADIUS = height / (2 * cls.PIXEL_PER_UNIT)


config = Config()
