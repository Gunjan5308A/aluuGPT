import sys
import os
import argparse
import textwrap

# Ensure the speadyanimation library is in path
LIB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "speadyanimation"))
sys.path.insert(0, LIB_DIR)

from speadyanimation import *

# 3B1B Style Constants
BG_COLOR = "#111111"
BLUE_P = Color.from_hex("#58C4DD")
GREEN_P = Color.from_hex("#83C167")
YELLOW_P = Color.from_hex("#FFFF00")
GREY_P = Color.from_hex("#888888")

class FallbackScene(Scene):
    def __init__(self, explanation, equation, graph_type, graph_points, output_path):
        self.explanation_text = explanation
        self.equation_latex = equation
        self.graph_type = graph_type
        self.graph_points = graph_points
        self.output_path = output_path
        super().__init__()

    def construct(self):
        # Set background
        self.camera.background_color = Color.from_hex(BG_COLOR)
        
        # --- 1. Explanation / Title with WRAPPING ---
        # Wrap text to 40 characters to avoid going off-screen
        wrapped_text = "\n".join(textwrap.wrap(self.explanation_text, width=45))
        title = Text(wrapped_text, font_size=32, color=BLUE_P).to_edge(UP, buff=0.5)
        
        # --- 2. Structural Layer (Axes) ---
        axes = None
        if self.graph_type.lower() in ["line", "scatter", "plot"]:
            axes = Axes(x_range=[0, 10], y_range=[0, 10]).scale(0.6).to_edge(DOWN, buff=0.5)
            axes.set_opacity(0.15)
            self.add(axes)
            self.play(Create(axes), run_time=1.0)

        # Reveal Title
        self.play(Write(title), run_time=1.5)
        self.wait(1.0)

        # --- 3. Algebraic Layer (Equation) ---
        if self.equation_latex:
            eq = MathTex(self.equation_latex, color=YELLOW_P).scale(0.8)
            # Position it below title but above axes
            eq.next_to(title, DOWN, buff=0.4)
            self.play(FadeIn(eq), run_time=1.5)
            self.wait(1.5)
        
        # --- 4. Geometric Layer (Visualization) ---
        if self.graph_type.lower() in ["line", "scatter", "plot"] and self.graph_points and axes:
            try:
                coords = []
                for p in self.graph_points.split(","):
                    if ":" in p:
                        x, y = p.split(":")
                        coords.append([float(x), float(y), 0])
                
                if coords:
                    if self.graph_type.lower() == "line":
                        path = VMobject(color=GREEN_P).set_points_as_corners(coords)
                        self.play(Create(path), run_time=2.0)
                    else: # Scatter
                        dots = VGroup(*[Dot(point=axes.c2p(c[0], c[1]), color=GREEN_P) for c in coords])
                        self.play(Create(dots), run_time=2.0)
                    self.wait(2.0)
            except Exception as e:
                print(f"Graph Error: {e}")
        
        elif self.graph_type.lower() == "circle":
            circle = Circle(radius=1.2, color=GREEN_P).to_edge(DOWN, buff=0.8)
            self.play(GrowFromCenter(circle), run_time=1.5)
            self.play(Indicate(circle), run_time=1.0)
            self.wait(2.0)
            
        elif self.graph_type.lower() == "rect":
            rect = Rectangle(width=3, height=2, color=GREEN_P).to_edge(DOWN, buff=0.8)
            self.play(Create(rect), run_time=1.5)
            self.play(Indicate(rect), run_time=1.0)
            self.wait(2.0)

        self.wait(1.0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--explanation", default="Explanation")
    parser.add_argument("--equation", default="")
    parser.add_argument("--graph_type", default="none")
    parser.add_argument("--graph_points", default="")
    parser.add_argument("--output", default="output.mp4")
    args = parser.parse_args()

    os.environ["SDL_VIDEODRIVER"] = "dummy"
    Config.FPS = 30
    Config.WIDTH = 1280
    Config.HEIGHT = 720
    
    scene = FallbackScene(args.explanation, args.equation, args.graph_type, args.graph_points, args.output)
    scene.render(preview=False, export=True, filename=args.output)
