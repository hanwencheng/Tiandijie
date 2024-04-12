from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from primitives.effects import EventListener
    from calculation.Modifier import Modifier
    from primitives.effects.ModifierEffect import ModifierEffect
import enum
import string
from typing import List


class FieldBuffTemp:
    def __init__(
        self,
        buff_id: str,
        buff_hero: str,
        buff_range: int,
        modifier_effects: List[List[ModifierEffect]] or List[ModifierEffect] = None,
        on_event: List[EventListener] = None,
    ):
        if modifier_effects is None:
            modifier_effects = [[]]
            self.upgradable = False
        elif all(isinstance(item, list) for item in modifier_effects):
            self.upgradable = True
        else:
            modifier_effects = [modifier_effects]
            self.upgradable = False
        if on_event is None:
            on_event = []
        self.id = buff_id
        self.buff_hero = buff_hero
        self.buff_range = buff_range
        self.modifier_effects: List[ModifierEffect] = modifier_effects
        self.event_listeners: List[EventListener] = on_event

    def __getitem__(self, key):
        return getattr(self, key)
