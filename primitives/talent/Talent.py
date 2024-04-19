from typing import List

from primitives.effects.EventListener import EventListener
from primitives.effects.ModifierEffect import ModifierEffect


class Talent:
    def __init__(
        self,
        talent_id: str,
        hero_id: str,
        effects: List[ModifierEffect] = None,
        event_listeners: List[EventListener] = None,
    ):
        if effects is None:
            effects = []
        if event_listeners is None:
            event_listeners = []
        self.id = talent_id
        self.hero_id = hero_id
        self.modifier_effects = effects
        self.trigger: int = 0
        self.cooldown: int = 0
        self.event_listeners = event_listeners
