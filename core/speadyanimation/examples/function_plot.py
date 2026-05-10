import sys, os, math
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from speadyanimation import *


class FunctionPlotDemo(Scene):
    def construct(self):
        axes = Axes(
            x_range=[-4, 4, 1],
            y_range=[-4, 4, 1],
            x_length=9,
            y_length=9,
            color=WHITE
        )

        self.play(Create(axes), run_time=1.5)
        self.wait(0.3)

        sin_graph = axes.get_graph(math.sin, color=YELLOW)
        self.play(Create(sin_graph), run_time=1.5)
        self.wait(0.5)

        cos_graph = axes.get_graph(math.cos, color=BLUE)
        self.play(Create(cos_graph), run_time=1.5)
        self.wait(0.5)

        x_squared = axes.get_graph(lambda x: x**2 / 4, color=RED)
        self.play(Create(x_squared), run_time=1.5)
        self.wait(1.0)


if __name__ == "__main__":
    FunctionPlotDemo().render(preview=True)
