from __future__ import annotations
from typing import TYPE_CHECKING

from helpers import is_magic_profession_dict

if TYPE_CHECKING:
    from calculation.Range import Range
    from primitives.effects.ModifierEffect import ModifierEffect
    from primitives.effects.SkillListener import SkillListener
    from primitives.hero.Element import Elements
    from primitives.skill.Distance import Distance
    from typing import List
    from primitives.hero.HeroBasics import Professions

import enum
from calculation.Range import skill_range_profession_dict


class SkillTargetTypes(enum.Enum):
    ENEMY_SINGLE = 0
    ENEMY_RANGE = 1
    PARTNER_SINGLE = 2
    PARTNER_RANGE = 3
    SELF = 4
    TERRAIN = 5


class SkillType(enum.IntEnum):
    Physical = 0
    Magical = 1
    Move = 2


class SkillTemp:
    def __init__(self, skill_temp_id: str, cost: int, skill_element: Elements, skill_type: SkillType,
                 max_cool_down: int, distance: Distance,
                 range_vale: Range, multiplier: float, effects: List[ModifierEffect] = None,
                 event_listeners: List[SkillListener] = None):
        if effects is None:
            effects = []
        if event_listeners is None:
            event_listeners = []
        self.id = skill_temp_id
        self.max_cool_down = max_cool_down
        self.cost = cost
        self.element = skill_element
        self.skill_type = skill_type
        self.distance = distance
        self.range_value = range_vale
        self.multiplier = multiplier
        self.modifier_effects = effects
        self.event_listeners = event_listeners

    def is_magic(self):
        return self.skill_type == SkillType.Magical


class NormalAttackTemp(SkillTemp):
    def __init__(self, skill_temp_id: str, cost: int, skill_element: Elements, skill_type: SkillType,
                 max_cool_down: int, distance: Distance, range_vale: Range, multiplier: float,
                 effects: List[ModifierEffect] = None, event_listeners: List[SkillListener] = None):
        super().__init__(skill_temp_id, cost, skill_element, skill_type, max_cool_down, distance, range_vale,
                         multiplier, effects, event_listeners)
        if effects is None:
            effects = []
        if event_listeners is None:
            event_listeners = []
        self.id = skill_temp_id
        self.cost = cost
        self.element = skill_element
        self.skill_type = skill_type
        self.max_cool_down = 0
        self.distance = distance
        self.range_value = range_vale
        self.multiplier = multiplier
        self.modifier_effects = effects
        self.event_listeners = event_listeners


def is_normal_attack(skill: SkillTemp) -> bool:
    return isinstance(skill, NormalAttackTemp)


def create_normal_attack_skill(profession: Professions, is_magic) -> NormalAttackTemp:
    if is_magic is None:
        is_magic = is_magic_profession_dict[profession]
    return NormalAttackTemp(1.0, skill_range_profession_dict[profession], [], [], [], [], profession, is_magic)
