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
    from primitives.Action import Action

from calculation.modifier_calculator import get_modifier, get_skill_modifier
from calculation.ModifierAttributes import ModifierAttributes as Ma

from typing import List
from primitives.hero.Element import get_elemental_relationship, ElementRelationships
from primitives.Action import ActionTypes

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
    def attack_certain_hero(
        hero_temp_id: str, actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        if _is_attacker(actor_hero, context):
            if target_hero.temp.id == hero_temp_id:
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
        if _is_attacker(target_hero, context):
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
    def move_more_than(
        max_move: int, actor_hero: Hero, target_hero: Hero, context: Context
    ):
        action = context.get_last_action()
        if actor_hero == action.actor:
            if action.moves > max_move:
                return True
        return False

    @staticmethod
    def self_all_active_skills_in_cooldown(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        for skill in actor_hero.enabled_skills:
            if skill not in actor_hero.temp.passives and skill.cool_down <= 0:
                return 0
        return 1

    @staticmethod
    def self_has_active_skills_in_cooldown(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        for skill in actor_hero.enabled_skills:
            if skill not in actor_hero.temp.passives and skill.cool_down > 0:
                return 1
        return 0

    @staticmethod
    def target_has_active_skills_in_cooldown(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        for skill in target_hero.enabled_skills:
            if skill not in target_hero.temp.passives and skill.cool_down > 0:
                return 1
        return 0

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
    def is_in_battle(actor_hero: Hero, target_hero: Hero, context: Context) -> int:
        action = context.get_last_action()
        return action.is_in_battle

    @staticmethod
    def is_attack_target(actor_hero: Hero, target_hero: Hero, context: Context) -> int:
        return _is_attacker(target_hero, context)

    @staticmethod
    def is_battle_attack_target(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        action = context.get_last_action()
        return _is_attacker(target_hero, context) and action.is_in_battle

    @staticmethod
    def is_battle_with_remote(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        action = context.get_last_action()
        if (
            target_hero.temp.profession
            in [
                Professions.SORCERER,
                Professions.PRIEST,
                Professions.ARCHER,
            ]
            and action.is_in_battle
        ):
            return 1
        return 0

    @staticmethod
    def attacked_by_melee_attack(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        action = context.get_last_action()
        if (
            target_hero.temp.profession
            in [
                Professions.GUARD,
                Professions.SWORDSMAN,
                Professions.RIDER,
                Professions.WARRIOR,
            ]
            and action.is_in_battle
            and _is_attacker(target_hero, context)
        ):
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
    def skill_is_certain_element(
        element_value: Elements, actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        action = context.get_last_action()
        if _is_attacker(actor_hero, context):
            if action.skill.temp.skill_element == element_value:
                return 1
        return 0

    @staticmethod
    def self_use_certain_skill(
        skill_id: str, actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        action = context.get_last_action()
        if _is_attacker(actor_hero, context):
            if action.skill.temp.id == skill_id:
                return 1
        return 0

    @staticmethod
    def skill_is_in_element_list(
        element_list: List[Elements],
        actor_hero: Hero,
        target_hero: Hero,
        context: Context,
    ) -> int:
        action = context.get_last_action()
        if _is_attacker(actor_hero, context):
            if action.skill.temp.skill_element in element_list:
                return 1
        return 0

    @staticmethod
    def action_is_active_skill(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        if context.get_last_action().type == ActionTypes.SKILL_ATTACK:
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
    def self_is_used_active_skill(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        action = context.get_last_action()
        if _is_attacker(actor_hero, context):
            if action.skill.temp in actor_hero.enabled_skills:
                return 1
        return 0

    @staticmethod
    def is_target_by_fire_element(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        action = context.get_last_action()
        if _is_attacker(target_hero, context):
            if action.skill.temp.skill_element == Elements.FIRE:
                return 1
        return 0

    @staticmethod
    def target_is_certain_element(
        element_value: Elements, actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        if _is_attacker(actor_hero, context):
            if actor_hero.temp.element == element_value:
                return 1
        return 0

    @staticmethod
    def is_magic_attack(actor_hero: Hero, target_hero: Hero, context: Context) -> int:
        action = context.get_last_action()
        if action.skill.temp.is_magic():
            return 1
        return 0

    @staticmethod
    def is_in_terrain(
        terrain_value: str, actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        return 1

    @staticmethod
    def xingyun_requires_check(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        if not RequirementCheck.is_battle_attack_target(
            actor_hero, target_hero, context
        ):
            return 0

        action = context.get_last_action()
        if actor_hero == action.actor:
            return min(action.moves, 3)
        return False

    @staticmethod
    def miepokongjian_requires_check(
        actor_hero: Hero, target_hero: Hero, context: Context, buff: Buff
    ) -> int:
        caster = context.get_hero_by_id(buff.caster_id)
        if caster.player_id != actor_hero.player_id:
            return 0
        return LifeRequirementChecks.life_not_full(
            actor_hero, target_hero, context
        ) and RequirementCheck.self_is_first_attack(actor_hero, target_hero, context)

    @staticmethod
    def huanyanliezhen_requires_check(
        actor_hero: Hero, target_hero: Hero, context: Context, buff: Buff
    ) -> int:
        caster = context.get_hero_by_id(buff.caster_id)
        if caster.player_id != actor_hero.player_id:
            return 0
        return BuffRequirementChecks.target_has_certain_buff(
            "ranshao", actor_hero, target_hero, context
        ) and RequirementCheck.self_is_first_attack(actor_hero, target_hero, context)

    @staticmethod
    def yanyukongjian_requires_check(
        level_value: int, actor_hero: Hero, target_hero: Hero, context: Context, buff: Buff
    ) -> int:
        caster = context.get_hero_by_id(buff.caster_id)
        if caster.player_id != actor_hero.player_id:
            return 0
        if RequirementCheck.target_is_certain_element(
                Elements.THUNDER, actor_hero, target_hero, context
        ) and RequirementCheck.self_is_first_attack(actor_hero, target_hero, context):
            if (level_value == 1 or level_value == 2) and buff.trigger <= 2:
                buff.trigger += 1
                return 1
            elif level_value == 3 and buff.trigger <= 3:
                buff.trigger += 1
                return 1
        return 0

    @staticmethod
    def self_is_first_attack(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        action = context.get_last_action()
        if _is_attacker(actor_hero, context) and action.is_in_battle():
            if RequirementCheck.target_has_counterattack_first(action, context):
                return 1
        return 0

    @staticmethod
    def self_and_caster_is_partner_and_first_attack(
        actor_hero: Hero, target_hero: Hero, context: Context, buff: Buff
    ) -> int:
        action = context.get_last_action()
        caster = context.get_hero_by_id(buff.caster_id)
        if _is_attacker(actor_hero, context) and action.is_in_battle() and actor_hero.player_id == caster.player_id:
            if RequirementCheck.target_has_counterattack_first(action, context):
                return 1
        return 0

    @staticmethod
    def target_has_counterattack_first(action: Action, context: Context):
        target = action.get_defender_hero_in_battle()
        actor = action.actor
        is_counterattack_first = get_modifier(
            Ma.is_counterattack_first, target, actor, context
        )
        counterattack_first_limit = get_modifier(
            Ma.counterattack_first_limit, target, actor, context
        )
        return (
            is_counterattack_first
            and counterattack_first_limit > target.counterattack_count
        )

    @staticmethod
    def self_and_caster_is_enemy(
        actor_hero: Hero, target_hero: Hero, context: Context, buff: Buff
    ) -> int:
        action = context.get_last_action()
        caster = context.get_hero_by_id(buff.caster_id)
        return caster.player_id != actor_hero.player_id

    @staticmethod
    def self_and_caster_is_partner(
        actor_hero: Hero, target_hero: Hero, context: Context, buff: Buff
    ) -> int:
        action = context.get_last_action()
        caster = context.get_hero_by_id(buff.caster_id)
        return caster.player_id == actor_hero.player_id

    @staticmethod
    def self_and_caster_is_partner_and_is_attacked_target(
        actor_hero: Hero, target_hero: Hero, context: Context, buff: Buff
    ) -> int:
        caster = context.get_hero_by_id(buff.caster_id)
        if _is_attacker(target_hero, context) and caster.player_id == actor_hero.player_id:
            return 1
        return 0


    LifeChecks: LifeRequirementChecks
    PositionChecks: PositionRequirementChecks
    BuffChecks: BuffRequirementChecks
