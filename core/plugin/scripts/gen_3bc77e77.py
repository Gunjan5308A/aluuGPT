import os
import sys, os
sys.path.insert(0, r'/home/goodname/code/AluuGPT/core/speadyanimation')
sys.path.insert(0, r'/home/goodname/code/AluuGPT')
Derivatives are a fundamental concept in calculus, which is a branch of mathematics that deals with the study of continuous change. In essence, derivatives measure the rate at which a function changes as its input changes.
from speadyanimation import *

class Introduction(Scene):
    def construct(self):
        title = Text("Derivatives").to_edge(UP)
        self.add(title)
        self.wait(1)

        equation = MathTex(r"f(x) = x^2").next_to(title, DOWN, buff=0.8)
        self.play(Create(equation))
        self.wait(2)
The derivative of a function `f(x)` is denoted as `f'(x)` and represents the rate of change of the function with respect to `x`. It is defined as the limit of the difference quotient as the change in `x` approaches zero.
class Definition(Scene):
    def construct(self):
        title = Text("Definition of a Derivative").to_edge(UP)
        self.add(title)
        self.wait(1)

        equation = MathTex(r"f'(x) = \lim_{h \to 0} \frac{f(x + h) - f(x)}{h}").next_to(title, DOWN, buff=0.8)
        self.play(Create(equation))
        self.wait(2)
The derivative of a function can be interpreted geometrically as the slope of the tangent line to the graph of the function at a given point.
class GeometricInterpretation(Scene):
    def construct(self):
        title = Text("Geometric Interpretation").to_edge(UP)
        self.add(title)
        self.wait(1)

        axes = Axes(
            x_range=[-10, 10, 2],
            y_range=[-10, 10, 2],
            x_length=8,
            y_length=6,
            axis_config={"include_tip": False},
        ).next_to(title, DOWN, buff=0.8)
        self.play(Create(axes))

        graph = FunctionGraph(lambda x: x**2, x_range=[-10, 10], color=BLUE).next_to(axes, DOWN, buff=0)
        self.play(Create(graph))

        tangent_line = Line(start=axes.coords_to_point(-2, 4), end=axes.coords_to_point(