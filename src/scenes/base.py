class Scene:
    def __init__(self, game):
        self.game = game
        self.next_scene = None

    def handle_event(self, event):
        pass

    def update(self, dt):
        pass

    def render(self, screen):
        pass
