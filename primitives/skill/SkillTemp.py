from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from calculation.Range import Range
    from primitives.Context import Context
from primitives.hero.HeroBasics import Professions
import enum
from typing import Callable, Any
from typing import List

from calculation.Range import skill_range_profession_dict

class SkillTargetTypes(enum.Enum):
    ENEMY_SINGLE = 0
    ENEMY_RANGE = 1
    PARTNER_SINGLE = 2
    PARTNER_RANGE = 3
    SELF = 4
    TERRAIN = 5

class SkillTemp:
    def __init__(self, damage_multiplier: float, skill_range: Range,
                 before_buff_modifiers: List[Callable[[List[Context]], Any]],
                 after_buff_modifiers: List[Callable[[List[Context]], Any]],
                 before_fixed_damage_modifier: List[Callable[..., Any]],
                 after_fixed_damage_modifier: List[Callable[..., Any]],
                 profession: Professions = None,
                 is_magic: bool = False
                 ):
        self.damage_multiplier = damage_multiplier
        self.before_action_buff_modifier = before_buff_modifiers
        self.after_action_buff_modifier = after_buff_modifiers
        self.before_action_fixed_damage_modifier = before_fixed_damage_modifier
        self.after_action_fixed_damage_modifier = after_fixed_damage_modifier
        self.range = skill_range
        self.target_type = SkillTargetTypes.SELF
        self.is_magic = is_magic


is_magic_profession_dict = {
    Professions.WARRIOR: True,
    Professions.SWORDSMAN: False,
    Professions.ARCHER: False,
    Professions.SORCERER: True,
    Professions.PRIEST: True,
    Professions.GUARD: False,
}


class NormalAttackTemp(SkillTemp):
    def __init__(self, damage_multiplier: float, skill_range: Range,
                 before_buff_modifiers: List[Callable[[List[Context]], Any]],
                 after_buff_modifiers: List[Callable[[List[Context]], Any]],
                 before_fixed_damage_modifier: List[Callable[..., Any]],
                 after_fixed_damage_modifier: List[Callable[..., Any]],
                 profession: Professions,
                 is_magic: bool
                 ):
        super().__init__(1.0, skill_range, [], [],
                         [], [], profession, is_magic)
        self.target_type = SkillTargetTypes.ENEMY_SINGLE
        self.damage_multiplier = 1.0
        self.skill_range = skill_range_profession_dict[profession]


def is_normal_attack(skill: SkillTemp) -> bool:
    return isinstance(skill, NormalAttackTemp)


def create_normal_attack_skill(profession: Professions, is_magic) -> NormalAttackTemp:
    if is_magic is None:
        is_magic = is_magic_profession_dict[profession]
    return NormalAttackTemp(1.0, skill_range_profession_dict[profession], [], [], [], [], profession, is_magic)
