import os
import sys, os
sys.path.insert(0, r'/home/goodname/code/AluuGPT/core/speadyanimation')
sys.path.insert(0, r'/home/goodname/code/AluuGPT')
import sys, os, math
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from speadyanimation import *

Config.FPS = 24


class Derivatives(Scene):
    def construct(self):
        # Title
        title = Text("Derivatives").to_edge(UP)
        self.add(title)

        # Equation
        equation = MathTex(r"f(x) = x^2").next_to(title, DOWN, buff=0.8)
        self.play(Create(equation), run_time=1.5)

        # Graph
        axes = Axes(x_range=[-5, 5, 1], y_range=[-5, 25, 5]).move_to([0, -0.5])
        self.play(Create(axes), run_time=1.5)

        # Function Graph
        function_graph = axes.plot(lambda x: x**2, x_range=[-5, 5], color=BLUE)
        self.play(Create(function_graph), run_time=1.5)

        # Tangent Line
        tangent_line = axes.plot(lambda x: 2*x + 0, x_range=[-5, 5], color=YELLOW)
        self.play(Create(tangent_line), run_time=1.5)

        # Derivative Equation
        derivative_equation = MathTex(r"f'(x) = 2x").next_to(axes, DOWN, buff=0.6)
        self.play(Create(derivative_equation), run_time=1.5)

        # Insight
        insight = Text("The derivative represents the rate of change of the function").next_to(derivative_equation, DOWN, buff=0.6)
        self.play(Create(insight), run_time=1.5)

        self.wait(2.0)

        # Clean up
        self.remove(axes, function_graph, tangent_line, derivative_equation, insight)

        # Conclusion
        conclusion = Text("Derivatives are used to model rates of change in real-world phenomena").to_edge(DOWN)
        self.play(Create(conclusion), run_time=1.5)

        self.wait(2.0)


if __name__ == "__main__":
    Derivatives().render(
        preview=True,
        export=True,
        filename="/home/goodname/code/AluuGPT/static/animations/animation_7b55fe04.mp4",
    )