from animation.animation import Animation
from utils.rate_functions import smooth, linear


class AnimationGroup(Animation):
    def __init__(self, *animations, run_time=None, rate_func=None, lag_ratio=0.0):
        self.animations = list(animations)
        self.lag_ratio = lag_ratio
        if run_time is None:
            if self.animations:
                run_time = max(a.run_time for a in self.animations)
            else:
                run_time = 0
        rf = rate_func or smooth
        super().__init__(None, run_time=run_time, rate_func=rf)

    def begin(self):
        for anim in self.animations:
            anim.begin()
        self._is_started = True

    def interpolate(self, alpha):
        alpha = max(0.0, min(1.0, alpha))
        t = self.rate_func(alpha)
        if self.lag_ratio == 0:
            for anim in self.animations:
                anim.update(t)
        else:
            n = len(self.animations)
            for i, anim in enumerate(self.animations):
                start = i * self.lag_ratio / n
                end = start + (1 - self.lag_ratio * (n - 1) / n)
                if end <= start:
                    end = start + 0.01
                if t <= start:
                    sub_alpha = 0.0
                elif t >= end:
                    sub_alpha = 1.0
                else:
                    sub_alpha = (t - start) / (end - start)
                anim.update(sub_alpha)

    def finish(self):
        for anim in self.animations:
            if not anim.is_done():
                anim.finish()
        self._is_finished = True

    def get_all_mobjects(self):
        result = []
        for anim in self.animations:
            result.extend(anim.get_all_mobjects())
        return result

    def clean_up(self):
        for anim in self.animations:
            anim.clean_up()


class Succession(Animation):
    def __init__(self, *animations, run_time=None, rate_func=linear):
        self.animations = list(animations)
        if run_time is None:
            run_time = sum(a.run_time for a in self.animations)
        super().__init__(None, run_time=run_time, rate_func=rate_func)
        self._current_idx = 0

    def begin(self):
        if self.animations:
            self.animations[0].begin()
        self._is_started = True

    def interpolate(self, alpha):
        alpha = max(0.0, min(1.0, alpha))
        t = self.rate_func(alpha)
        total = sum(a.run_time for a in self.animations)
        elapsed = t * total
        cumulative = 0
        for i, anim in enumerate(self.animations):
            if cumulative + anim.run_time >= elapsed or i == len(self.animations) - 1:
                if not anim._is_started:
                    anim.begin()
                sub_alpha = (elapsed - cumulative) / anim.run_time if anim.run_time > 0 else 1.0
                sub_alpha = max(0.0, min(1.0, sub_alpha))
                anim.update(sub_alpha)
                break
            else:
                if not anim.is_done():
                    if not anim._is_started:
                        anim.begin()
                    anim.finish()
            cumulative += anim.run_time

    def finish(self):
        for anim in self.animations:
            if not anim.is_done():
                if not anim._is_started:
                    anim.begin()
                anim.finish()
        self._is_finished = True

    def get_all_mobjects(self):
        result = []
        for anim in self.animations:
            result.extend(anim.get_all_mobjects())
        return result

    def clean_up(self):
        for anim in self.animations:
            anim.clean_up()


class LaggedStart(AnimationGroup):
    def __init__(self, *animations, lag_ratio=0.5, run_time=None, rate_func=smooth):
        super().__init__(*animations, lag_ratio=lag_ratio, run_time=run_time, rate_func=rate_func)


class Wait(Animation):
    def __init__(self, duration=1.0):
        super().__init__(None, run_time=duration, rate_func=linear)

    def begin(self):
        self._is_started = True

    def interpolate_mobject(self, t):
        pass

    def finish(self):
        self._is_finished = True

    def get_all_mobjects(self):
        return []
