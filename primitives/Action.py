import enum
from typing import List
from basics import Position

from primitives.hero import Hero
from primitives.skill.Skill import Skill


class ActionTypes(enum.Enum):
    HEAL = 0
    SKILL_ATTACK = 1
    SUMMON = 2
    SELF = 3
    PASS = 4
    NORMAL_ATTACK = 5


class Action:
    def __init__(self, cast_hero: Hero, affected_heroes, skill: Skill, movable, actionable):
        self.targets: List[Hero] = affected_heroes
        self.total_damage: float = 0
        self.is_magic: bool = skill.is_magic()
        self.is_in_battle: bool = False
        self.is_with_protector: bool = False
        self.protector: Hero or None = None
        self.skill: Skill = skill
        self.type: ActionTypes = ActionTypes.PASS
        self.move_range: int = 0
        self.moves: List[Position] = []
        self.move_point: Position = (0, 0)
        self.action_point: Position = (0, 0)
        self.movable: bool = movable
        self.actionable: bool = actionable
        self.actor = cast_hero
        self.player_id = cast_hero.player_id
        self.has_additional_action: bool = False
        self.additional_move: int = 0
        self.additional_skill: Skill = None

    def update_affected_heroes(self, affected_heroes: List[Hero]):
        self.targets = affected_heroes

    def update_total_damage(self, total_damage: float):
        self.total_damage = total_damage

    def update_is_in_battle(self, is_in_battle: bool):
        self.is_in_battle = is_in_battle

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

    def update_additional_move(self, additional_move: int):
        self.additional_move = additional_move
