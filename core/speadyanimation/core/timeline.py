from core.config import Config


class TimelineBlock:
    def __init__(self, animations, run_time=None):
        self.animations = animations if isinstance(animations, list) else [animations]
        if run_time is not None:
            self.run_time = run_time
        elif self.animations:
            self.run_time = max(a.run_time for a in self.animations)
        else:
            self.run_time = 0
        self.elapsed = 0.0
        self.started = False
        self.finished = False

    def start(self):
        if not self.started:
            for anim in self.animations:
                anim.begin()
            self.started = True

    def update(self, dt):
        if not self.started:
            self.start()
        self.elapsed += dt
        alpha = min(self.elapsed / self.run_time, 1.0) if self.run_time > 0 else 1.0
        for anim in self.animations:
            anim.update(alpha)
        if alpha >= 1.0:
            self.finished = True

    def get_all_mobjects(self):
        mobjects = []
        for anim in self.animations:
            mobjects.extend(anim.get_all_mobjects())
        return mobjects


class WaitBlock:
    def __init__(self, duration=1.0):
        self.run_time = duration
        self.elapsed = 0.0
        self.started = True
        self.finished = False
        self.animations = []

    def start(self):
        pass

    def update(self, dt):
        self.elapsed += dt
        if self.elapsed >= self.run_time:
            self.finished = True

    def get_all_mobjects(self):
        return []


class Timeline:
    def __init__(self):
        self.blocks = []
        self.current_block_idx = 0

    def add_animation_block(self, animations, run_time=None):
        block = TimelineBlock(animations, run_time)
        self.blocks.append(block)
        return block

    def add_wait_block(self, duration=1.0):
        block = WaitBlock(duration)
        self.blocks.append(block)
        return block

    def get_current_block(self):
        if self.current_block_idx < len(self.blocks):
            return self.blocks[self.current_block_idx]
        return None

    def update(self, dt):
        block = self.get_current_block()
        if block is None:
            return False
        block.update(dt)
        if block.finished:
            self.current_block_idx += 1
        return True

    def is_finished(self):
        return self.current_block_idx >= len(self.blocks)

    def get_total_duration(self):
        return sum(b.run_time for b in self.blocks)

    def reset(self):
        self.current_block_idx = 0
        for block in self.blocks:
            block.elapsed = 0.0
            block.finished = False
            block.started = False
