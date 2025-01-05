from .gematria_actions import GematriaActions
# Import other tab action classes

class ActionManager:
    def __init__(self, main_window):
        self.gematria_actions = GematriaActions(main_window)
        # Initialize other tab actions

    def connect_all_actions(self):
        self.gematria_actions.connect_actions()
        # Connect other tab actions
