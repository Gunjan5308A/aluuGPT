import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from speadyanimation import *


class BarChartDemo(Scene):
    def construct(self):
        chart = BarChart(
            values=[3, 7, 2, 5, 8, 4],
            bar_names=["A", "B", "C", "D", "E", "F"],
            bar_width=0.5,
            x_length=9,
            y_length=5,
            fill_opacity=0.8,
        )
        chart.set_bar_progress(0.0)

        self.add(chart)
        self.wait(0.3)

        frames_to_grow = 90
        for i in range(frames_to_grow + 1):
            chart.set_bar_progress(i / frames_to_grow)
            self.wait(1.0 / 60)

        self.wait(1.5)


if __name__ == "__main__":
    BarChartDemo().render(preview=True)
