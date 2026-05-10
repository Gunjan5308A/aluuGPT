import sys, os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from speadyanimation import *

Config.FPS = 24


class DerivativeOfXSquared(Scene):
    def construct(self):
        
        # --- Title ---
        title = Group(
            Text("Derivative of"),
            MathTex(r"x^2"),
        ).arrange(RIGHT, buff=0.2).to_edge(UP)
        self.play(Write(title), run_time=1.2)
        self.wait(0.5)

        # --- Equation ---
        equation = MathTex(r"f(x) = x^2").next_to(title, DOWN, buff=0.8)
        self.play(Write(equation), run_time=1.2)
        self.wait(0.5)

        # --- Axes ---
        axes = Axes(
            x_range=[-3, 3, 1],
            y_range=[-1, 9, 2],
        ).move_to([0, -0.5])

        self.play(Create(axes), run_time=1.5)
        self.wait(0.5)

        # --- Graph of x^2 ---
        graph = axes.get_graph(lambda x: x**2)
        self.play(Create(graph), run_time=1.5)
        self.wait(0.5)

        # --- Point on curve ---
        x_val = 1
        y_val = x_val**2
        point = Dot(axes.c2p(x_val, y_val))
        self.play(FadeIn(point), run_time=0.8)

        # --- Tangent line approximation ---
        slope = 2 * x_val  # derivative of x^2
        tangent_line = Line(
            axes.c2p(x_val - 1, y_val - slope),
            axes.c2p(x_val + 1, y_val + slope),
        )

        self.play(Create(tangent_line), run_time=1.2)
        self.wait(0.5)

        # --- Derivative expression ---
        derivative_eq = MathTex(r"\frac{d}{dx}x^2 = 2x").next_to(equation, DOWN, buff=0.8)
        self.play(Write(derivative_eq), run_time=1.2)
        self.wait(1.0)

        # --- Highlight slope ---
        self.play(Indicate(derivative_eq), run_time=0.6)
        self.wait(0.5)

        # --- Clean up ---
        self.play(
            FadeOut(title),
            FadeOut(equation),
            FadeOut(derivative_eq),
            FadeOut(graph),
            FadeOut(tangent_line),
            FadeOut(point),
            FadeOut(axes),
            run_time=1.2
        )


        # --- Final statement ---
        conclusion = MathTex(r"f'(x) = 2x").move_to([0, 0.8])
        subtitle = Group(
            Text("The slope of y ="),
            MathTex(r"x^2"),
            Text("is twice the x-value"),
        ).arrange(RIGHT, buff=0.2).next_to(conclusion, DOWN, buff=0.8)
        self.play(Write(conclusion), run_time=1.0)
        self.play(Write(subtitle), run_time=1.0)
        self.wait(1.5)


if __name__ == "__main__":
    DerivativeOfXSquared().render(
        preview=True,
        export=True,
        filename="speadystudioanimation.mp4",
    )
