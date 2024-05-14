from __future__ import annotations

from typing import List
from primitives.hero.Attributes import generate_max_level_attributes
from typing import TYPE_CHECKING
from calculation.PathFinding import bfs_move_range
from calculation.Range import calculate_if_targe_in_diamond_range
from primitives.skill.SkillTypes import SkillTargetTypes
from primitives.Action import Action, ActionTypes
from calculation.modifier_calculator import get_level2_modifier

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
        self.actionable_list: [Hero] = []

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

    def reset_actionable(self, move_range=None, context=None):
        self.actionable = True
        if move_range is None:
            move_range = self.temp.hide_professions.value[2] + get_level2_modifier(
                self, None, "move_range", context
            )
        self.initialize_actionable_hero(context.heroes, move_range, context)

    def initialize_movable_range(self, battlemap, hero_list, move_range):
        other_hero_list = [hero for hero in hero_list if hero.id != self.id]
        enemies_list = [
            hero.position for hero in hero_list if hero.player_id != self.player_id
        ]
        partner_list = [
            hero.position
            for hero in other_hero_list
            if hero.player_id == self.player_id
        ]
        self.movable_range = bfs_move_range(
            self.position,
            move_range,
            battlemap,
            self.temp.flyable,
            enemies_list,
            partner_list,
        )

    def initialize_actionable_hero(self, hero_list, move_range, context):
        self.initialize_movable_range(context.battlemap, hero_list, move_range)
        for position in self.movable_range:     # 可移动的Action
            new_action = Action(self, [], None, position)
            new_action.update_action_type(ActionTypes.PASS)
            self.actionable_list.append(new_action)

        for hero in hero_list:
            if hero.player_id != self.player_id:
                for position in self.movable_range:
                    if (
                        calculate_if_targe_in_diamond_range(
                            position, hero.position, self.temp.hide_professions.value[1]
                        )
                    ):
                        new_action = Action(self, [hero], None, position)
                        new_action.update_action_type(ActionTypes.NORMAL_ATTACK)

                        self.actionable_list.append(new_action)

        for skill in self.enabled_skills:
            if skill.cool_down == 0:
                target_hero_list = []
                if (
                        skill.temp.target_type == SkillTargetTypes.ENEMY_SINGLE
                        or skill.temp.target_type == SkillTargetTypes.ENEMY_RANGE
                ):
                    target_hero_list = [hero for hero in hero_list if hero.player_id != self.player_id]
                elif (
                        skill.temp.target_type == SkillTargetTypes.PARTNER_SINGLE
                        or skill.temp.target_type == SkillTargetTypes.PARTNER_RANGE
                ):
                    target_hero_list = [hero for hero in hero_list if hero.player_id == self.player_id]

                if target_hero_list is not None:
                    for hero in target_hero_list:
                        for moveable_position in self.movable_range:
                            if skill.temp.range_value.check_if_target_in_range(
                                moveable_position, hero.position, hero.position
                            ):
                                if skill.temp.target_type == SkillTargetTypes.ENEMY_RANGE or skill.temp.target_type == SkillTargetTypes.PARTNER_RANGE:
                                    hero_in_skill = []
                                    for effect_hero in target_hero_list:
                                        if skill.temp.range_value.check_if_target_in_range(moveable_position, hero.position, effect_hero.position):
                                            hero_in_skill.append(effect_hero)

                                    new_action = Action(self, hero_in_skill, skill, moveable_position)      # 有目标有伤害技能
                                    new_action.update_action_type(ActionTypes.SKILL_ATTACK)
                                    self.actionable_list.append(new_action)
                                else:
                                    new_action = Action(self, [hero], skill, moveable_position)     # 有目标无伤害技能
                                    self.actionable_list.append(new_action)
                else:
                    for moveable_position in self.movable_range:    # 无目标技能：律的传送等
                        new_action = Action(self, [], skill, moveable_position)
                        new_action.update_action_type(ActionTypes.SELF)
                        self.actionable_list.append(new_action)

