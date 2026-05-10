# SpeadyAnimation Documentation

SpeadyAnimation is a Manim-inspired animation library built on Pygame and NumPy.
It is designed around three core ideas:

- `Scene` for the script and timeline
- `Mobject` for anything visible
- `Animation` for time-based changes

The easiest way to use the library is:

```python
from speadyanimation import *
```

That top-level module re-exports the common classes, colors, helpers, and animations so you do not need to import from many submodules.

## Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Core Concepts](#core-concepts)
5. [Public API](#public-api)
6. [Layout and Spacing](#layout-and-spacing)
7. [Animation Patterns](#animation-patterns)
8. [Text and Math](#text-and-math)
9. [Graphing](#graphing)
10. [Exporting Video](#exporting-video)
11. [Examples](#examples)
12. [Notes for LLMs](#notes-for-llms)

## Overview

SpeadyAnimation gives you a small but expressive set of tools for drawing shapes, showing graphs, and animating the transitions between them.

The coordinate system is mathematical:

- origin is at the center of the screen
- positive `x` goes right
- positive `y` goes up

The `Camera` converts between math coordinates and screen pixels.

## Installation

Requirements:

- Python 3.10+
- Pygame 2.x
- NumPy

Optional:

- Matplotlib for `MathTex`
- FFmpeg for MP4 export

Example setup:

```bash
cd speadyanimation
python -m venv venv
source venv/bin/activate
pip install pygame numpy matplotlib
```

## Quick Start

```python
import sys, os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from speadyanimation import *

Config.FPS = 24


class MyScene(Scene):
    def construct(self):
        title = Text("Hello SpeadyAnimation").to_edge(UP)
        circle = Circle(radius=1.5, color=BLUE, fill_color=BLUE, fill_opacity=0.35)
        circle.next_to(title, DOWN, buff=1.0)

        self.play(Write(title))
        self.play(Create(circle))
        self.wait(1.0)
        self.play(FadeOut(title), FadeOut(circle))


if __name__ == "__main__":
    MyScene().render(preview=True, export=True, filename="speadystudioanimation.mp4")
```

## Core Concepts

### Scene

Subclass `Scene` and implement `construct()`. That method defines the animation in order.

Important methods:

- `self.add(*mobjects)` adds objects instantly
- `self.remove(*mobjects)` removes objects instantly
- `self.play(*animations, run_time=None, rate_func=None)` runs animations together
- `self.wait(duration=1.0)` pauses the timeline
- `self.render(preview=True, export=False, filename="output.mp4")` runs the scene

### Mobject

`Mobject` is the base class for visible objects.

Common transformation helpers:

- `move_to(point)`
- `shift(vector)`
- `scale(factor, about_point=None)`
- `rotate(angle, about_point=None)`
- `set_color(color)`
- `set_fill(color=None, opacity=None)`
- `set_stroke(color=None, width=None, opacity=None)`
- `set_opacity(opacity)`
- `next_to(other, direction, buff=0.25)`
- `to_edge(direction, buff=0.25)`
- `align_to(other, direction)`

### Animation

Animations modify one or more mobjects over time.

Common classes:

- Creation: `Create`, `Uncreate`, `DrawBorderThenFill`, `Write`, `ShowPassingFlash`
- Movement: `Shift`, `MoveTo`, `Rotate`, `ScaleInPlace`, `MoveAlongPath`
- Fading: `FadeIn`, `FadeOut`, `FadeTransform`, `GrowFromCenter`
- Transform: `Transform`, `ReplacementTransform`, `CounterclockwiseTransform`, `TransformFromCopy`
- Indication: `Indicate`, `Flash`, `Circumscribe`, `Wiggle`
- Composition: `AnimationGroup`, `Succession`, `LaggedStart`, `Wait`

## Public API

### Core

Import from `speadyanimation`:

- `Config`
- `config`
- `Camera`
- `Renderer`
- `Scene`
- `Timeline`
- `Exporter`

### Geometry and Shapes

- `Mobject`
- `Dot`
- `Circle`
- `Arc`
- `Line`
- `Arrow`
- `DashedLine`
- `Rectangle`
- `Square`
- `Polygon`
- `RegularPolygon`
- `Triangle`
- `Annulus`
- `PointCloud`

### Graphing

- `NumberLine`
- `Axes`
- `NumberPlane`
- `FunctionGraph`
- `ParametricGraph`
- `BarChart`

### Text

- `Text`
- `MathTex`
- `Paragraph`

### Grouping and Media

- `Group`
- `VGroup`
- `ImageMobject`

### Animations

- `Animation`
- `Shift`
- `MoveTo`
- `Rotate`
- `ScaleInPlace`
- `MoveAlongPath`
- `FadeIn`
- `FadeOut`
- `FadeTransform`
- `GrowFromCenter`
- `Create`
- `Uncreate`
- `DrawBorderThenFill`
- `Write`
- `ShowPassingFlash`
- `Transform`
- `ReplacementTransform`
- `CounterclockwiseTransform`
- `TransformFromCopy`
- `Indicate`
- `Flash`
- `Circumscribe`
- `Wiggle`
- `AnimationGroup`
- `Succession`
- `LaggedStart`
- `Wait`

### Colors and Helpers

The top-level import also exposes:

- color objects like `WHITE`, `BLACK`, `RED`, `GREEN`, `BLUE`, `YELLOW`, `TEAL`, `PURPLE`, `ORANGE`, `PINK`, `GOLD`
- direction vectors like `UP`, `DOWN`, `LEFT`, `RIGHT`, `ORIGIN`, `UL`, `UR`, `DL`, `DR`
- easing functions like `smooth`, `linear`, `ease_out_bounce`, `there_and_back`
- math helpers like `normalize`, `lerp`, `distance`, `midpoint`, `points_on_circle`
- bezier helpers like `bezier`, `quadratic_bezier`, `cubic_bezier`, `bezier_path`

## Layout and Spacing

The library provides positioning helpers so text and visuals do not collide.

Recommended rules:

- Use `title.to_edge(UP)` for headings
- Use `next_to(..., buff=0.6 to 1.0)` for subtitles and equations
- Keep a clear gap between major scene elements
- Use `FadeOut` to clear old content before adding new content in the same area
- Avoid placing labels directly on top of graphs unless that is intentional
- Prefer one graph and one or two text objects per scene stage

Useful patterns:

```python
title = Text("Derivative of sin^2(x)").to_edge(UP)
equation = MathTex(r"f(x)=\sin^2(x)").next_to(title, DOWN, buff=0.8)
axes = Axes(x_range=[-4, 4, 1], y_range=[-2, 2, 1])
axes.move_to([0, -0.5])
```

If objects start to compete for space, reorganize the scene instead of shrinking everything too much.

### Positioning Methods

- `to_edge(direction, buff=0.25)` moves an object to the frame edge
- `next_to(other, direction, buff=0.25)` places one object beside another
- `align_to(other, direction)` aligns one edge or side with another object
- `arrange()` and `arrange_in_grid()` are available on `Group` and `VGroup`

## Animation Patterns

### Building a scene

```python
self.play(Write(title))
self.play(Create(axes))
self.play(Create(graph))
self.play(FadeIn(label))
self.play(FadeOut(old_label), FadeOut(old_graph))
```

### Simultaneous animations

`Scene.play` accepts multiple animations and runs them together:

```python
self.play(Create(circle), FadeIn(label))
```

### Standard flow

1. Introduce the topic
2. Show the main equation or object
3. Add the graph or supporting visual
4. Highlight the important part
5. Clean up the screen
6. Finish with a conclusion

## Text and Math

Use the right class for the right job:

- `Text` for plain English or labels
- `MathTex` for formulas, symbols, and equations
- `Paragraph` for multiline text blocks

Examples:

```python
title = Text("Slope of the tangent")
eq = MathTex(r"f'(x)=2x")
note = Paragraph("Derivative", "is the slope", "of the curve")
```

Important notes:

- Use raw strings for `MathTex`, for example `r"\sin(2x)"`
- Do not use `Text` for math
- If a label is symbolic or formula-like, prefer `MathTex`

## Graphing

`Axes` and `NumberLine` are the main graphing helpers.

Examples:

```python
axes = Axes(
    x_range=[-4, 4, 1],
    y_range=[-3, 3, 1],
    x_length=9,
    y_length=5,
)

graph = axes.get_graph(lambda x: math.sin(x), color=BLUE)
point = axes.c2p(1, 2)
```

Useful graph classes:

- `Axes` for 2D plots
- `NumberPlane` for a grid background
- `FunctionGraph` for function curves
- `ParametricGraph` for parametric curves
- `BarChart` for bar visualizations

## Exporting Video

Render a scene with:

```python
MyScene().render(preview=True)
MyScene().render(export=True, filename="my_video.mp4")
MyScene().render(preview=True, export=True, filename="my_video.mp4")
```

The project uses FFmpeg for MP4 export when available.

## Examples

The repository includes example scenes in:

- `examples/hello_circle.py`
- `examples/function_plot.py`
- `examples/bar_chart.py`
- `examples/transform_demo.py`

They are useful references for:

- basic shapes
- graphing
- transforms
- fading and creation effects

## Notes for LLMs

When generating code for this library:

- use `from speadyanimation import *`
- keep spacing generous
- avoid overlapping text and visuals
- prefer `MathTex` for equations
- use the classes and methods that actually exist in this repository
- keep the scene clean by removing old content before introducing new content in the same region

If you are unsure about layout, prioritize readability over density.
