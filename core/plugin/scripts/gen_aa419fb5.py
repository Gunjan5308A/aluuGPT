import os
import sys, os
sys.path.insert(0, r'/home/goodname/code/AluuGPT/core/speadyanimation')
sys.path.insert(0, r'/home/goodname/code/AluuGPT')
import sys, os, math
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from speadyanimation import *

Config.FPS = 24


class DerivativeOfX2(Scene):
    def construct(self):
        # Title
        title = Text("Derivative of x^2").to_edge(UP)
        self.play(Write(title), run_time=1.0)
        self.wait(0.5)

        # Equation
        equation = MathTex(r"f(x) = x^2")
        self.play(Write(equation), run_time=1.0)
        self.wait(0.5)

        # Derivative explanation
        derivative_title = Text("Derivative:").next_to(equation, DOWN, buff=0.8)
        derivative_equation = MathTex(r"f'(x) = 2x")
        self.play(Write(derivative_title), Write(derivative_equation), run_time=1.0)
        self.wait(0.5)

        # Graph
        axes = Axes(
            x_range=[-4, 4, 1],
            y_range=[-4, 16, 4],
            x_length=8,
            y_length=6,
            axis_config={"include_tip": False},
        )
        graph = axes.plot(lambda x: x**2, x_range=[-4, 4], color=YELLOW)
        derivative_graph = axes.plot(lambda x: 2*x, x_range=[-4, 4], color=RED)
        self.play(Create(axes), Create(graph), run_time=1.5)
        self.wait(0.5)
        self.play(Create(derivative_graph), run_time=1.5)
        self.wait(0.5)

        # Tangent line
        x_value = 2
        tangent_line = axes.plot(
            lambda x: 2*x_value*(x - x_value) + x_value**2,
            x_range=[-4, 4],
            color=BLUE,
        )
        self.play(Create(tangent_line), run_time=1.5)
        self.wait(0.5)

        # Clean up
        self.play(
            Uncreate(tangent_line),
            Uncreate(derivative_graph),
            Uncreate(graph),
            Uncreate(axes),
            Uncreate(derivative_equation),
            Uncreate(derivative_title),