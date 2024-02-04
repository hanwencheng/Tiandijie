from scenes.setup import setup_context


class State:
    def __int__(self):
        self.context = setup_context()

    def _apply_action(self, action):
        apply_action(action)
