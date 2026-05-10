import copy
from utils.rate_functions import smooth


class Animation:
    def __init__(self, mobject, run_time=1.0, rate_func=smooth):
        self.mobject = mobject
        self.run_time = run_time
        self.rate_func = rate_func
        self.starting_mobject = None
        self._is_started = False
        self._is_finished = False

    def begin(self):
        self.starting_mobject = self.mobject.copy()
        self._is_started = True

    def interpolate(self, alpha):
        alpha = max(0.0, min(1.0, alpha))
        t = self.rate_func(alpha)
        self.interpolate_mobject(t)

    def interpolate_mobject(self, t):
        pass

    def finish(self):
        self.interpolate(1.0)
        self._is_finished = True

    def clean_up(self):
        pass

    def is_done(self):
        return self._is_finished

    def get_all_mobjects(self):
        return [self.mobject]

    def get_run_time(self):
        return self.run_time

    def update(self, alpha):
        if not self._is_started:
            self.begin()
        if alpha >= 1.0:
            self.finish()
        else:
            self.interpolate(alpha)
