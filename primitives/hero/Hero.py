from __future__ import annotations

from typing import List
from primitives.hero.Attributes import generate_max_level_attributes
from typing import TYPE_CHECKING
from calculation.PathFinding import bfs_move_range
from calculation.Range import calculate_if_targe_in_diamond_range
from primitives.skill.SkillTypes import SkillTargetTypes, SkillType
from primitives.Action import Action, ActionTypes
from calculation.modifier_calculator import get_level2_modifier

if TYPE_CHECKING:
    from primitives.hero.HeroTemp import HeroTemp
    from primitives.buff import Buff
    from primitives.fieldbuff.FieldBuff import FieldBuff
    from basics import Position
    from primitives.Passive import Passive
from primitives.skill.skills import Skills
from primitives.skill.Skill import Skill
from calculation.Range import (
    calculate_diamond_area,
)


class Hero:
    def __init__(self, player_id: int, hero_temp: HeroTemp, init_position):
        self.id = hero_temp.temp_id + str(player_id)
        self.player_id = player_id
        self.temp: HeroTemp = hero_temp
        self.equipments = []
        self.enabled_passives: List[Passive] = []
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
        self.energy: int = 0
        self.shield: int = 0

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
            damage = max(harm_value - self.shield, 0)
            self.shield = max(self.shield - harm_value, 0)
            self.current_life = max(self.current_life - damage, 0)

    def take_healing(self, healing_value: float):
        if healing_value > 0:
            self.current_life = min(self.current_life + healing_value, self.max_life)

    def add_shield(self, shield_value: float):
        if shield_value > 0:
            self.shield = min(self.shield + shield_value, self.max_life)

    def update_position(self, position: Position):
        self.position = position
        # TODO move_path

    def add_counter_attack_count(self):
        self.counterattack_count += 1

    def get_buff_by_id(self, buff_id: str) -> Buff:
        return [buff for buff in self.buffs if buff.id == buff_id][0]

    def get_field_buff_by_id(self, field_name: str) -> FieldBuff:
        return [buff for buff in self.field_buffs if buff.temp.id == field_name][0]

    def reset_actionable(self, context, move_range=None):
        self.actionable = True
        if context.get_last_action().has_additional_action:
            print("再动后的", self.id, move_range)
        self.initialize_actionable_hero(context, move_range)

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

    def initialize_actionable_hero(self, context, move_range=None):
        self.actionable_list = []
        hero_list = context.heroes

        # 默认移动范围
        if move_range is None:
            move_range = self.temp.hide_professions.value[2] + get_level2_modifier(self, None, "move_range", context)

        self.initialize_movable_range(context.battlemap, hero_list, move_range)

        # 处理可移动的Action
        for position in self.movable_range:
            action_type = ActionTypes.PASS if position == self.position else ActionTypes.MOVE
            new_action = Action(self, [], None, position, position)
            new_action.update_action_type(action_type)
            self.actionable_list.append(new_action)

        # 处理普通攻击的Action
        attack_range = self.temp.hide_professions.value[1] + get_level2_modifier(self, None, "attack_range", context)
        for hero in filter(lambda h: h.player_id != self.player_id, hero_list):
            for position in self.movable_range:
                if calculate_if_targe_in_diamond_range(position, hero.position, attack_range):
                    new_action = Action(self, [hero], None, position, hero.position)
                    new_action.update_action_type(ActionTypes.NORMAL_ATTACK)
                    self.actionable_list.append(new_action)

        # 处理技能的Action
        for skill in filter(lambda s: s.cool_down == 0, self.enabled_skills):
            for moveable_position in self.movable_range:
                if skill.temp.target_type == SkillTargetTypes.TERRAIN:
                    target_position_list = calculate_diamond_area(moveable_position, skill.temp.distance.distance_value)
                    target_position_list = [pos for pos in target_position_list if pos not in {hero.position for hero in hero_list}]

                    for target_position in target_position_list:
                        target_hero_list = [hero for hero in hero_list if hero.player_id != self.player_id]
                        hero_in_skill = [enemy for enemy in target_hero_list if skill.temp.range_instance.check_if_target_in_range(moveable_position, enemy.position, target_position)]

                        if hero_in_skill:
                            new_action = Action(self, hero_in_skill, skill, moveable_position, target_position)
                            new_action.update_action_type(ActionTypes.SKILL_ATTACK)
                            self.actionable_list.append(new_action)
                elif skill.temp.target_type == SkillTargetTypes.SELF:
                    hero_in_skill = [self]
                    if skill.temp.skill_type == SkillType.Support:
                        partner_list = [hero for hero in hero_list if hero.player_id == self.player_id and hero.player_id != self.player_id]
                        hero_in_skill.extend(partner for partner in partner_list if skill.temp.range_instance.check_if_target_in_range(moveable_position, moveable_position, partner.position))

                        new_action = Action(self, hero_in_skill, skill, moveable_position, moveable_position)
                        new_action.update_action_type(ActionTypes.SUPPORT)
                        self.actionable_list.append(new_action)
                    elif skill.temp.skill_type in {SkillType.Physical, SkillType.Magical}:
                        enemy_list = [hero for hero in hero_list if hero.player_id != self.player_id]
                        hero_in_skill = [enemy for enemy in enemy_list if skill.temp.range_instance.check_if_target_in_range(moveable_position, moveable_position, enemy.position)]

                        if hero_in_skill:
                            new_action = Action(self, hero_in_skill, skill, moveable_position, moveable_position)
                            new_action.update_action_type(ActionTypes.SKILL_ATTACK)
                            self.actionable_list.append(new_action)
                else:
                    target_hero_list = [hero for hero in hero_list if (skill.temp.target_type == SkillTargetTypes.ENEMY and hero.player_id != self.player_id) or (skill.temp.target_type != SkillTargetTypes.ENEMY and hero.player_id == self.player_id)]

                    for target in target_hero_list:
                        skill_new_distance = skill.temp.distance.distance_value + get_level2_modifier(self, None, "active_skill_range", context)
                        skill_new_distance += get_level2_modifier(self, None, "single_skill_range" if skill.temp.range_instance.range_value == 0 else "range_skill_range", context)

                        if calculate_if_targe_in_diamond_range(moveable_position, target.position, int(skill_new_distance)):
                            hero_in_skill = [target] + [effect_hero for effect_hero in target_hero_list if effect_hero != target and skill.temp.range_instance.check_if_target_in_range(moveable_position, target.position, effect_hero.position)]

                            new_action = Action(self, hero_in_skill, skill, moveable_position, target.position)
                            if skill.temp.skill_type == SkillType.Support:
                                new_action.update_action_type(ActionTypes.SUPPORT)
                            elif skill.temp.skill_type == SkillType.Heal:
                                new_action.update_action_type(ActionTypes.HEAL)
                            elif skill.temp.skill_type in {SkillType.Physical, SkillType.Magical}:
                                new_action.update_action_type(ActionTypes.SKILL_ATTACK)
                            self.actionable_list.append(new_action)


    def transfor_enable_skill(
        self, old_skill_name: str, new_skill_name: str, init_skill_cooldown: int = 0
    ):
        for skill in self.enabled_skills:
            if skill.temp.id == old_skill_name:
                self.enabled_skills.remove(skill)
                break
        self.enabled_skills.append(
            Skill(init_skill_cooldown, Skills.get_skill_by_id(new_skill_name))
        )
        # for skill in self.enabled_skills:
        #     print(22222, skill.temp.id)
        # if skill.temp.id == "leiyinwanyu" and self.player_id == 0:
        #     print(moveable_position, target.position, int(skill_new_distance),  calculate_if_targe_in_diamond_range(
        #         moveable_position,
        #         target.position,
        #         int(skill_new_distance),
        #     ))
