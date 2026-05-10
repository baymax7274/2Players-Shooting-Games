import sys
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, COLOR_BG


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("双人枪战 — Two-Player Shooter")
        self.clock = pygame.time.Clock()
        self.running = True
        self.scene = None
        self.dt = 0.0

    def change_scene(self, scene):
        self.scene = scene

    def run(self, start_scene):
        self.scene = start_scene
        while self.running:
            dt_ms = self.clock.tick(FPS)
            self.dt = min(dt_ms / 1000.0, 0.1)

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                if self.scene:
                    self.scene.handle_event(event)

            if self.scene:
                self.scene.update(self.dt)
                self.scene.render(self.screen)
                if self.scene.next_scene is not None:
                    self.scene = self.scene.next_scene

            pygame.display.flip()

        pygame.quit()
        sys.exit()
