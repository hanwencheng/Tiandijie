from __future__ import annotations
from typing import TYPE_CHECKING

import enum
from typing import List
from basics import Position
from calculation.PathFinding import a_star_search

if TYPE_CHECKING:
    from primitives.hero.Hero import Hero
    from primitives.skill.Skill import Skill
from calculation.modifier_calculator import get_buff_modifier


class ActionTypes(enum.Enum):
    HEAL = 0
    SKILL_ATTACK = 1
    SUMMON = 2
    SELF = 3
    PASS = 4
    NORMAL_ATTACK = 5
    TELEPORT = 6


class AdditionalSkill:
    def __init__(self, skill: Skill, targets: List[Hero], additional_move: int = 0):
        self.skill: Skill = skill
        self.targets: List[Hero] = targets


class Action:
    def __init__(
        self, cast_hero: Hero, affected_heroes, skill: Skill or None, action_point
    ):
        self.actor = cast_hero
        self.targets: List[Hero] = affected_heroes
        self.total_damage: float = 0
        self.is_magic: bool = skill.temp.is_magic() if skill is not None else False
        self.is_in_battle: bool = False
        self.is_with_protector: bool = False
        self.protector: Hero or None = None
        self.skill: Skill or None = skill
        self.type: ActionTypes = ActionTypes.PASS
        self.move_range: int = 0
        self.move_point: Position = cast_hero.position
        self.action_point: Position = action_point
        self.movable: bool = True
        self.actionable: bool = True
        self.player_id = cast_hero.player_id
        self.has_additional_action: bool = False
        self.additional_move: int = 0
        self.additional_skill_list: [AdditionalSkill] or None = None
        self.additional_action: [Action] or None = None

    def update_affected_heroes(self, affected_heroes: List[Hero]):
        self.targets = affected_heroes

    def update_total_damage(self, total_damage: float):
        self.total_damage = total_damage

    def update_is_in_battle(self, is_in_battle: bool):
        self.is_in_battle = is_in_battle

    def update_action_type(self, action_type: ActionTypes):
        self.type: ActionTypes = action_type

    def is_attacker(self, hero_id: str) -> bool:
        return self.actor.id == hero_id

    def get_counter_hero_in_battle(self, hero_id: str) -> Hero:
        if self.is_attacker(hero_id):
            return self.protector if self.is_with_protector else self.targets[0]
        else:
            return self.actor

    def get_defender_hero_in_battle(self) -> Hero:
        if self.is_with_protector:
            return self.protector
        else:
            return self.targets[0]

    def update_additional_move(self, actor, additional_move: int, context):
        move_disabled = get_buff_modifier("is_extra_move_range_disable", actor, None, context)
        if not move_disabled:
            self.has_additional_action = True
            self.additional_move = additional_move

    def update_additional_skill(self, additional_skill_list: [AdditionalSkill]):
        self.has_additional_action = True
        self.additional_skill_list = additional_skill_list

    def update_additional_action(self, actor, additional_action_list: [Action], context):
        action_disabled = get_buff_modifier("is_extra_action_disabled", actor, None, context)
        if not action_disabled:
            self.has_additional_action = True
            self.additional_skill_list = additional_action_list

    def update_moves(self, battle_map, enemies_list) -> List[Position]:
        return a_star_search(self.move_point, self.action_point, battle_map, self.actor.temp.flyable, enemies_list)

    def refresh_move_point(self, battle_map):
        battle_map.hero_move(self.move_point, self.action_point)