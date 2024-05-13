from __future__ import annotations
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from primitives.Context import Context
    from primitives.hero.Hero import Hero
    from primitives.Action import Action, ActionTypes
from primitives.Action import ActionTypes

from calculation.modifier_calculator import (
    get_modifier,
    get_skill_modifier,
    calculate_if_targe_in_diamond_range,
)
from calculation.ModifierAttributes import ModifierAttributes as ma
from primitives.skill.SkillTemp import SkillTargetTypes


def check_if_counterattack(actor: Hero, target: Hero, context: Context):
    is_counterattack_disabled = get_modifier(
        ma.is_counterattack_disabled, target, actor, context
    )
    return not is_counterattack_disabled


def check_if_counterattack_first(action: Action, context: Context):
    target = action.get_defender_hero_in_battle()
    actor = action.actor
    is_counterattack_first = get_modifier(
        ma.is_counterattack_first, target, actor, context
    )
    counterattack_first_limit = get_modifier(
        ma.counterattack_first_limit, target, actor, context
    )
    return (
        is_counterattack_first
        and counterattack_first_limit > target.counterattack_count
    )


def check_if_in_battle(action: Action, context: Context):
    if action.type == ActionTypes.NORMAL_ATTACK or (
        action.type == ActionTypes.SKILL_ATTACK
        and action.skill.type == SkillTargetTypes.ENEMY_SINGLE
    ):
        defender = action.get_defender_hero_in_battle()
        if check_if_counterattack(action.actor, defender, context):
            if (
                action.type == ActionTypes.NORMAL_ATTACK
                and calculate_if_targe_in_diamond_range(
                    action.action_point, defender.position, action.actor.temp.hide_professions.value[1]
                )
                or (action.skill and action.skill.range.check_if_target_in_skill_attack_range(
                    defender, action.actor, action.skill
                ))
            ):
                action.update_is_in_battle(True)
                return True
    else:
        return False


def check_protector(context: Context):
    action = context.get_last_action()
    if action.type == ActionTypes.NORMAL_ATTACK or (
        action.type == ActionTypes.SKILL_ATTACK
        and action.skill.type == SkillTargetTypes.ENEMY_SINGLE
    ):
        is_magic = action.is_magic
        target = action.targets[0]
        attr_name = ma.is_ignore_protector

        is_ignore_protector = get_modifier(attr_name, action.actor, target, context)
        if action.skill is not None:
            is_ignore_protector += get_skill_modifier(
                attr_name, action.actor, target, action.skill, context
            )
        if is_ignore_protector:
            return

        target_player_id = target.player_id
        possible_defenders = context.get_heroes_by_player_id(target_player_id)
        possible_protectors: List[tuple[Hero, int]] = []
        for defender in possible_defenders:
            attr_name = (
                ma.magic_protect_range if is_magic else ma.physical_protect_range
            )
            protect_range = get_modifier(attr_name, defender, action.actor, context)
            if protect_range >= 2:
                distance = abs(defender.position[0] - target.position[0]) + abs(
                    defender.position[1] - target.position[1]
                )
                if distance <= protect_range:
                    possible_protectors.append((defender, distance))

        # if there are multiple protectors, choose the one with the smallest distance
        if len(possible_protectors) > 0:
            possible_protectors.sort(key=lambda x: x[1])
            protector = possible_protectors[0][0]
            action.is_with_protector = True
            action.protector = protector


def check_if_double_attack(action: Action, context: Context):
    target = action.get_defender_hero_in_battle()
    actor = action.actor
    if_double_attack = get_modifier(ma.is_double_attack, actor, target, context)
    return if_double_attack
