from __future__ import annotations

from enum import Enum
from functools import partial
from typing import List

from calculation.Effects import Effects
from primitives.effects.Event import EventTypes
from primitives.effects.EventListener import EventListener
from calculation.Modifier import Modifier
from primitives.RequirementCheck.RequirementsCheck import RequirementCheck as RS


class TerrainBuffTemp:
    def __init__(self, buff_id: str, dispellable: bool, modifier_dict, on_event=None):
        if on_event is None:
            on_event = []
        self.modifier = Modifier(modifier_dict)
        self.id = buff_id
        self.dispellable = dispellable
        self.on_event: List[EventListener] = on_event


class TerrainBuff:
    def __init__(self, temp: TerrainBuffTemp, duration: int, side: int):
        self.temp = temp
        self.duration = duration
        self.side = side


class TerrainBuffTemps(Enum):
    fire = TerrainBuffTemp(
        "fire",
        True,
        {},
        [
            EventListener(
                EventTypes.action_end,
                1,
                RS.always_true,
                partial(Effects.take_fixed_damage_by_percentage, percentange=0.1),
            )
        ],
    )
    ice = TerrainBuffTemp("ice", True, {"move_range": -1})
