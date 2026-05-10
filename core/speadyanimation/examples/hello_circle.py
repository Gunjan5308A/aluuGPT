import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from speadyanimation import *


class HelloCircle(Scene):
    def construct(self):
        circle = Circle(radius=2, color=BLUE, fill_color=BLUE, fill_opacity=0.3)

        self.play(Create(circle), run_time=1.5)
        self.wait(0.5)

        self.play(Shift(circle, [3, 0]), run_time=1.0)
        self.wait(0.3)

        square = Square(side_length=2.5, color=RED, fill_color=RED, fill_opacity=0.3)
        square.move_to([-3, 0])

        self.play(Create(square), run_time=1.0)
        self.wait(0.5)

        self.play(FadeOut(circle), FadeOut(square), run_time=1.0)
        self.wait(0.5)


if __name__ == "__main__":
    HelloCircle().render(preview=True)
