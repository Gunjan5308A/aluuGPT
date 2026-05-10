import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from speadyanimation import *


class TransformDemo(Scene):
    def construct(self):
        circle = Circle(radius=1.5, color=BLUE, fill_color=BLUE, fill_opacity=0.4)
        self.play(Create(circle), run_time=1.0)
        self.wait(0.5)

        square = Square(side_length=3, color=RED, fill_color=RED, fill_opacity=0.4)
        self.play(Transform(circle, square), run_time=1.5)
        self.wait(0.5)

        hexagon = RegularPolygon(n=6, radius=1.8, color=GREEN, fill_color=GREEN, fill_opacity=0.4)
        self.play(Transform(circle, hexagon), run_time=1.5)
        self.wait(0.5)

        triangle = RegularPolygon(n=3, radius=2.0, color=PURPLE, fill_color=PURPLE, fill_opacity=0.4)
        self.play(Transform(circle, triangle), run_time=1.5)
        self.wait(0.5)

        self.play(FadeOut(circle), run_time=1.0)
        self.wait(0.5)


if __name__ == "__main__":
    TransformDemo().render(preview=True, export=True, filename="transform_demo.mp4" )
