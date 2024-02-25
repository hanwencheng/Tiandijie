from functools import partial

from primitives import Context
from primitives.effects.Event import EventTypes
from primitives.hero.Hero import Hero

class EventListener:
    def __init__(self, event_type: EventTypes, priority: int, requirement: partial[[Hero, Hero, Context], int] or None,
                 listener_effects: partial[[Hero, Hero, Context], None]):
        if requirement is None:
            self.requirement = lambda x, y, z: 1
        self.event_type = event_type
        self.priority = priority
        self.listener_effects = listener_effects
        self.requirement = requirement
