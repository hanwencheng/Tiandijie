

class Equipment:
    def __init__(self, equipment_id, modifier_effects, on_event):
        self.equipment_id = equipment_id
        self.modifier_effects = modifier_effects
        self.on_event = on_event
        self.cool_down = 0

