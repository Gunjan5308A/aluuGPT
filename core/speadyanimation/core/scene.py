import pygame
import sys
from core.config import Config
from core.camera import Camera
from core.renderer import Renderer
from core.timeline import Timeline
from animation.fading import FadeOut


class Scene:
    def __init__(self):
        self.mobjects = []
        self.camera = Camera()
        self.renderer = Renderer(self.camera)
        self.timeline = Timeline()
        self._animations_queue = []

    def construct(self):
        pass

    def add(self, *mobjects):
        for m in mobjects:
            if m not in self.mobjects:
                self.mobjects.append(m)
        return self

    def remove(self, *mobjects):
        for m in mobjects:
            if m in self.mobjects:
                self.mobjects.remove(m)
        return self

    def play(self, *animations, run_time=None, rate_func=None):
        anim_list = list(animations)
        if rate_func is not None:
            for anim in anim_list:
                anim.rate_func = rate_func
        block = self.timeline.add_animation_block(anim_list, run_time)
        self._animations_queue.append(('play', block, anim_list))
        return self

    def wait(self, duration=1.0):
        block = self.timeline.add_wait_block(duration)
        self._animations_queue.append(('wait', block, []))
        return self

    def render(self, preview=True, export=False, filename="output.mp4"):
        pygame.init()
        self.construct()

        width = Config.WIDTH
        height = Config.HEIGHT
        fps = Config.FPS

        self.camera.set_resolution(width, height)

        if preview:
            screen = pygame.display.set_mode((width, height))
            pygame.display.set_caption("SpeadyAnimation")
        else:
            screen = pygame.Surface((width, height))

        exporter = None
        if export:
            from core.exporter import Exporter
            exporter = Exporter(width, height, fps, filename)
            exporter.start()

        clock = pygame.time.Clock()
        dt = 1.0 / fps

        running = True
        while running:
            if preview:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False

            still_playing = self.timeline.update(dt)

            current_block = self.timeline.get_current_block()
            if current_block and hasattr(current_block, 'animations'):
                if not getattr(current_block, 'started', False):
                    current_block.start()
                    for anim in current_block.animations:
                        anim.interpolate(0.0)

                for anim in current_block.animations:
                    # Ensure mobjects in active animations are in the scene
                    for m in anim.get_all_mobjects():
                        if m not in self.mobjects:
                            self.mobjects.append(m)
                    
                    if anim.is_done():
                        if hasattr(anim, '_remove_on_finish') and anim._remove_on_finish:
                            for m in anim.get_all_mobjects():
                                if m in self.mobjects:
                                    self.mobjects.remove(m)
                        if hasattr(anim, '_add_target') and anim._add_target:
                            for m in anim.get_all_mobjects():
                                if m not in self.mobjects:
                                    self.mobjects.append(m)
                        if hasattr(anim, '_replace_on_finish') and anim._replace_on_finish:
                            if hasattr(anim, 'source') and anim.source in self.mobjects:
                                self.mobjects.remove(anim.source)
                            if hasattr(anim, 'target') and anim.target not in self.mobjects:
                                self.mobjects.append(anim.target)

            self.renderer.render_frame(screen, self.mobjects)

            if preview:
                pygame.display.flip()

            if exporter:
                frame_data = self.renderer.capture_frame(screen)
                exporter.write_frame(frame_data)

            if not still_playing:
                if export:
                    running = False
                else:
                    if not preview:
                        running = False
                        continue
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                running = False
                    self.renderer.render_frame(screen, self.mobjects)
                    if preview:
                        pygame.display.flip()

            clock.tick(fps)

        if exporter:
            exporter.finish()

        pygame.quit()
