from __future__ import annotations

from typing import List
from primitives import Equipment
from primitives.Stone import Stone
from primitives.hero.Attributes import generate_max_level_attributes
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from primitives.hero.HeroTemp import HeroTemp
    from primitives.skill.Skill import Skill
    from primitives.buff import Buff
    from primitives.fieldbuff.FieldBuff import FieldBuff
    from basics import Position


class Hero:
    def __init__(self, player_id: int, hero_temp: HeroTemp):
        self.id = hero_temp.id + player_id
        self.player_id = player_id
        self.temp: HeroTemp = hero_temp
        self.equipments: List[Equipment] = []
        self.enabled_passives: List[Skill] = []
        self.enabled_skills: List[Skill] = []
        self.position = (0, 0)
        self.stones = Stone()
        self.buffs: List[Buff] = []
        self.field_buffs: List[FieldBuff] = []
        self.initial_attributes = None
        self.current_life: float = 1.0
        self.is_alive: bool = True
        self.max_life: float = 1.0
        self.died_once: bool = False
        self.counterattack_count = 0
        self.initialize_attributes()
        self.actionable = True

    def initialize_attributes(self):
        initial_attributes = generate_max_level_attributes(
            self.temp.level0_attributes,
            self.temp.growth_coefficients,
            self.temp.profession,
        )
        self.initial_attributes = initial_attributes
        self.current_life = self.initial_attributes.life

    def update_position(self, position: Position):
        self.position = position
        # TODO move_path

    def add_counter_attack_count(self):
        self.counterattack_count += 1

    def get_buff_by_id(self, buff_id: str) -> Buff:
        return [buff for buff in self.buffs if buff.id == buff_id][0]

    def get_field_buff_by_id(self, field_name: str) -> FieldBuff:
        return [buff for buff in self.field_buffs if buff.temp.id == field_name][0]

    def reset_actionable(self):
        self.actionable = True
