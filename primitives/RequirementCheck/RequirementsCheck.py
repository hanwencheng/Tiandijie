from __future__ import annotations
from typing import TYPE_CHECKING

from primitives.RequirementCheck.BuffRequirementChecks import BuffRequirementChecks
from primitives.RequirementCheck.CheckHelpers import _is_attacker
from primitives.RequirementCheck.LifeRequirementChecks import LifeRequirementChecks
from primitives.RequirementCheck.PositionRequirementChecks import (
    PositionRequirementChecks,
)

if TYPE_CHECKING:
    from primitives.Context import Context
    from primitives.hero.Hero import Hero
    from primitives.buff.Buff import Buff
    from primitives.skill.SkillTypes import SkillTargetTypes
    from primitives.hero.Element import Elements


from primitives.hero.Element import get_elemental_relationship, ElementRelationships

from primitives.hero.HeroBasics import Professions, Gender


class RequirementCheck:
    # TODO  should not include any function related to level2 modifier

    @staticmethod
    def enemies_in_skill_range(
        maximum_count: int, actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        counted_enemies = 0
        action = context.get_last_action()
        skill = action.skill
        for hero in context.heroes:
            if hero.player_id != actor_hero.player_id:
                if skill.temp.range.check_if_target_in_range(
                    actor_hero.position, skill.target_point, hero.position
                ):
                    counted_enemies += 1
        return min(maximum_count, counted_enemies)

    @staticmethod
    def battle_with_certain_hero(
        hero_temp_id: str, actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        action = context.get_last_action()
        if action.is_in_battle:
            if (
                target_hero.temp.id == hero_temp_id
                or actor_hero.temp.id == hero_temp_id
            ):
                return 1
        return 0

    @staticmethod
    def battle_with_caster(
        actor_hero: Hero, target_hero: Hero, context: Context, buff: Buff
    ) -> int:
        caster_id = buff.caster_id
        action = context.get_last_action()
        if action.is_in_battle:
            if target_hero.id == caster_id:
                return 1
        return 0

    @staticmethod
    def attacked_by_caster(
        actor_hero: Hero, target_hero: Hero, context: Context, buff: Buff
    ) -> int:
        caster_id = buff.caster_id
        action = context.get_last_action()
        if action.is_in_battle and _is_attacker(target_hero, context):
            if target_hero.id == caster_id:
                return 1
        return 0

    @staticmethod
    def move_less_or_equal_than(
        max_move: int, actor_hero: Hero, target_hero: Hero, context: Context
    ):
        action = context.get_last_action()
        if actor_hero == action.actor:
            if action.moves <= max_move:
                return True
        return False

    @staticmethod
    def all_skills_in_cooldown(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        for skill in actor_hero.enabled_skills:
            if skill.cool_down > 0:
                return 0
        return 1

    @staticmethod
    def self_all_active_skills_in_cooldown(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        for skill in actor_hero.enabled_skills:
            if skill not in actor_hero.temp.passives and skill.cool_down > 0:
                return 0
        return 1

    @staticmethod
    def target_all_active_skills_in_cooldown(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        for skill in target_hero.enabled_skills:
            if skill not in target_hero.temp.passives and skill.cool_down > 0:
                return 0
        return 1

    @staticmethod
    def in_battle_with_non_flyable(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        action = context.get_last_action()
        if action.is_in_battle:
            if target_hero.temp.flyable:
                return 0
            else:
                return 1
        return 0

    @staticmethod
    def in_battle_with_non_female(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        action = context.get_last_action()
        if action.is_in_battle:
            if target_hero.temp.gender != Gender.FEMALE:
                return 1
        return 0

    @staticmethod
    def always_true() -> int:
        return 1

    @staticmethod
    def battle_with_no_element_advantage(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        action = context.get_last_action()
        if action.is_in_battle:
            actor_element = actor_hero.temp.element
            target_element = target_hero.temp.element
            if (
                get_elemental_relationship(actor_element, target_element)
                == ElementRelationships.NEUTRAL
            ):
                return 1
            else:
                return 0
        return 0

    @staticmethod
    def is_attacker(actor_hero: Hero, target_hero: Hero, context: Context) -> int:
        return _is_attacker(actor_hero, context)

    @staticmethod
    def target_is_battle_in_remote(actor_hero: Hero, target_hero: Hero, context: Context) -> int:
        action = context.get_last_action()
        if target_hero.temp.profession in [
            Professions.SORCERER,
            Professions.PRIEST,
            Professions.ARCHER,
        ] and action.is_in_battle:
            return 1
        return 0

    @staticmethod
    def skill_is_single_target_damage_and_life_is_higher_percentage(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> float:
        skill_target_type = context.get_last_action().skill.target_type
        if skill_target_type == SkillTargetTypes.ENEMY_SINGLE:
            return actor_hero.current_life / actor_hero.max_life
        return 0

    @staticmethod
    def skill_is_water_element(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        action = context.get_last_action()
        if _is_attacker(actor_hero, context):
            if action.skill.temp.skill_element == Elements.WATER:
                return 1
        return 0

    @staticmethod
    def is_attacked_by_fire_element(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        action = context.get_last_action()
        if _is_attacker(target_hero, context):
            if action.skill.temp.skill_element == Elements.FIRE:
                return 1
        return 0

    @staticmethod
    def is_attacked_by_non_flyer(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        action = context.get_last_action()
        if _is_attacker(target_hero, context):
            if not target_hero.temp.flyable and action.is_in_battle:
                return 1
        return 0

    @staticmethod
    def attack_to_advantage_elements(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        if _is_attacker(actor_hero, context):
            if (
                get_elemental_relationship(
                    actor_hero.temp.element, target_hero.temp.element
                )
                == ElementRelationships.ADVANTAGE
            ):
                return 1
        return 0

    @staticmethod
    def under_attack_by_advantage_elements(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        if _is_attacker(target_hero, context):
            if (
                get_elemental_relationship(
                    actor_hero.temp.element, target_hero.temp.element
                )
                == ElementRelationships.ADVANTAGE
            ):
                return 1
        return 0

    @staticmethod
    def self_is_used_skill(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        action = context.get_last_action()
        if action.actor == actor_hero:
            return 1
        return 0

    LifeChecks: LifeRequirementChecks
    PositionChecks: PositionRequirementChecks
    BuffChecks: BuffRequirementChecks
