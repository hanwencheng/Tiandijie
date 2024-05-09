from __future__ import annotations

from typing import List
from primitives.hero.Attributes import generate_max_level_attributes
from typing import TYPE_CHECKING
from calculation.PathFinding import bfs_move_range
from calculation.Range import calculate_if_targe_in_diamond_range

if TYPE_CHECKING:
    from primitives.hero.HeroTemp import HeroTemp
    from primitives.skill.Skill import Skill
    from primitives.buff import Buff
    from primitives.fieldbuff.FieldBuff import FieldBuff
    from basics import Position


class Hero:
    def __init__(self, player_id: int, hero_temp: HeroTemp, init_position):
        self.id = hero_temp.temp_id + str(player_id)
        self.player_id = player_id
        self.temp: HeroTemp = hero_temp
        self.equipments = []
        self.enabled_passives: List[Skill] = []
        self.enabled_skills: List[Skill] = []
        self.position = init_position
        self.stones = []
        self.buffs: List[Buff] = []
        self.field_buffs: List[FieldBuff] = []
        self.talents_field_buffs: List[FieldBuff] = []
        self.initial_attributes = None
        self.current_life: float = 1.0
        self.is_alive: bool = True
        self.max_life: float = 1.0
        self.died_once: bool = False
        self.counterattack_count = 0
        self.initialize_attributes()
        self.actionable = True
        self.movable_range: [Position] = []
        self.attackable_hero: [Hero] = []

    def initialize_attributes(self):
        initial_attributes = generate_max_level_attributes(
            self.temp.level0_attributes,
            self.temp.growth_coefficients,
            self.temp.hide_professions,
            self.temp.temp_id,
        )
        self.initial_attributes = initial_attributes
        self.current_life = self.initial_attributes.life

    def take_harm(self, harm_value: float):
        if harm_value > 0:
            self.current_life = max(self.current_life - harm_value, 0)

    def take_healing(self, healing_value: float):
        if healing_value > 0:
            self.current_life = min(self.current_life + healing_value, self.max_life)

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

    def initialize_movable_range(self, battlemap, hero_list):
        other_hero_list = [hero for hero in hero_list if hero.id != self.id]
        enemies_list = [hero.position for hero in hero_list if hero.player_id != self.player_id]
        partner_list = [hero.position for hero in other_hero_list if hero.player_id == self.player_id]
        self.movable_range = bfs_move_range(self.position, self.temp.hide_professions.value[2], battlemap, self.temp.flyable, enemies_list, partner_list)

    def initialize_attackable_hero(self, hero_list):
        for hero in hero_list:
            if hero.player_id != self.player_id:
                for position in self.movable_range:
                    if calculate_if_targe_in_diamond_range(position, hero.position, self.temp.hide_professions.value[1]) and hero not in self.attackable_hero:
                        self.attackable_hero.append(hero)

