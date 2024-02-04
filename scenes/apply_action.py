from typing import Callable, List

from calculation.Range import calculate_if_targe_in_diamond_range
from calculation.calculate_damage import apply_damage, \
    apply_counterattack_damage
from calculation.event_calculator import event_listener_calculator
from calculation.modifier_calculator import get_modifier
from primitives.Action import Action, ActionTypes
from primitives.Context import Context
from primitives.effects.Event import EventTypes
from primitives.hero.Hero import Hero
from calculation.ModifierAttributes import ModifierAttributes as ma
from primitives.skill.SkillTemp import SkillTargetTypes


# move actor to the desired position
def apply_move(action: Action):
    actor = action.actor
    actor.update_position(action)


action_event: dict[ActionTypes, tuple[EventTypes, EventTypes]] = {
    ActionTypes.HEAL: (EventTypes.heal_start, EventTypes.heal_end),
    ActionTypes.SKILL_ATTACK: (EventTypes.damage_start, EventTypes.damage_end),
    ActionTypes.NORMAL_ATTACK: (EventTypes.normal_attack_start, EventTypes.normal_attack_end),
    ActionTypes.SUMMON: (EventTypes.summon_start, EventTypes.summon_end),
    ActionTypes.SELF: (EventTypes.self_start, EventTypes.self_end),
    ActionTypes.PASS: (EventTypes.pass_start, EventTypes.pass_end),
    ActionTypes.COUNTERATTACK: (EventTypes.counterattack_start, EventTypes.counterattack_end),
}

skill_event: dict[SkillTargetTypes, tuple[EventTypes, EventTypes]] = {
    SkillTargetTypes.ENEMY_SINGLE: (EventTypes.skill_single_damage_start, EventTypes.skill_single_damage_end),
    SkillTargetTypes.ENEMY_RANGE: (EventTypes.skill_range_damage_start, EventTypes.skill_range_damage_end),
    SkillTargetTypes.PARTNER_SINGLE: (EventTypes.skill_for_partner_start, EventTypes.skill_for_partner_end),
    SkillTargetTypes.PARTNER_RANGE: (EventTypes.skill_for_partner_start, EventTypes.skill_for_partner_end),
    SkillTargetTypes.SELF: (EventTypes.skill_for_self_start, EventTypes.skill_for_self_end),
    SkillTargetTypes.TERRAIN: (EventTypes.skill_for_terrain_start, EventTypes.skill_for_terrain_end),
}


def check_if_counterattack(actor: Hero, target: Hero, context: Context):
    is_counterattack_disabled = get_modifier(ma.is_counterattack_disabled, target, actor, context)
    return not is_counterattack_disabled


def check_if_counterattack_first(action: Action, context: Context):
    target = action.get_defender_hero_in_battle()
    actor = action.actor
    is_counterattack_first = get_modifier(ma.is_counterattack_first, target, actor, context)
    counterattack_first_limit = get_modifier(ma.counterattack_first_limit, target, actor, context)
    return is_counterattack_first and counterattack_first_limit > target.counterattack_count


def check_if_in_battle(action: Action, context: Context):
    if action.skill.type == SkillTargetTypes.ENEMY_SINGLE:
        defender = action.get_defender_hero_in_battle()
        if check_if_counterattack(action.actor, defender, context):
            if action.skill.range.check_if_target_in_normal_attack_range(defender, action.actor, context):
                action.update_is_in_battle(True)
                return True
    else:
        return False


def check_protector(context: Context):
    action = context.get_last_action()
    if action.skill.type == SkillTargetTypes.ENEMY_SINGLE:
        is_magic = action.skill.is_magic
        target = action.targets[0]
        target_player_id = target.player_id
        possible_defenders = context.get_heroes_by_player_id(target_player_id)
        possible_protectors: List[tuple[Hero, int]] = []
        for defender in possible_defenders:
            attr_name = ma.magic_protect_range if is_magic else ma.physical_protect_range
            protect_range = get_modifier(attr_name, defender, action.actor, context)
            if protect_range >= 2:
                distance = abs(defender.position[0] - target.position[0]) + abs(defender.position[1] - target.position[1])
                if distance <= protect_range:
                    possible_protectors.append((defender, distance))

        # if there are multiple protectors, choose the one with the smallest distance
        if len(possible_protectors) > 0:
            possible_protectors.sort(key=lambda x: x[1])
            protector = possible_protectors[0][0]
            action.is_with_protector = True
            action.protector = protector


def action_wrapper_counterattack(context: Context):
    action = context.get_last_action()
    counter_attacker = action.get_defender_hero_in_battle()
    actor = action.actor
    event_listener_calculator(counter_attacker, actor, EventTypes.counterattack_start, context)
    apply_counterattack_damage(counter_attacker, action.actor, action, context)
    event_listener_calculator(counter_attacker, actor, EventTypes.counterattack_end, context)


def action_wrapper_battle(context: Context, action_func: Callable[[Hero, Hero or None, Context], None]):
    actor = context.get_last_action().actor
    target = context.get_last_action().get_defender_hero_in_battle()
    event_listener_calculator(actor, target, EventTypes.battle_start, context)
    action_func(actor, target, context)
    event_listener_calculator(actor, target, EventTypes.battle_end, context)


def attack_damage_events(actor_instance: Hero, counter_instance: Hero or None, context: Context):
    action = context.get_last_action()
    skill_start_event_type = skill_event[action.skill.target_type][0]
    skill_end_event_type = skill_event[action.skill.target_type][1]
    event_listener_calculator(actor_instance, counter_instance, skill_start_event_type, context)
    event_listener_calculator(actor_instance, counter_instance, EventTypes.damage_start, context)
    apply_damage(action, context)
    event_listener_calculator(actor_instance, counter_instance, EventTypes.damage_end, context)
    event_listener_calculator(actor_instance, counter_instance, skill_end_event_type, context)


def is_hero_live(hero_instance: Hero, counter_instance: Hero or None, context: Context):
    if hero_instance.current_life <= 0:
        event_listener_calculator(hero_instance, counter_instance, EventTypes.hero_death, context)
        context.set_hero_died(hero_instance)


def apply_action(context: Context, action: Action):
    if not action.actionable:
        return

    actor = context.get_last_action().actor
    context.add_action(action)
    actions_start_event_type = action_event[action.type][0]
    actions_end_event_type = action_event[action.type][1]

    event_listener_calculator(actor, None, EventTypes.move_start, context)

    if action.movable:
        apply_move(action)

    event_listener_calculator(actor, None, EventTypes.move_end, context)

    check_protector(context)
    action.update_is_in_battle(check_if_in_battle(action, context))

    event_listener_calculator(actor, None, actions_start_event_type, context)

    if action.is_in_battle:
        target = action.get_defender_hero_in_battle()
        if check_if_counterattack_first(action, context):
            action_wrapper_counterattack(context)  # take damage
            if is_hero_live(action.actor, target, context):
                event_listener_calculator(actor, target, EventTypes.battle_start, context)
                event_listener_calculator(actor, target, EventTypes.skill_single_damage_start, context)
                event_listener_calculator(actor, target, EventTypes.damage_start, context)
                apply_damage(action, context)
                event_listener_calculator(actor, target, EventTypes.damage_end, context)
                event_listener_calculator(actor, target, EventTypes.skill_single_damage_end, context)

            event_listener_calculator(actor, target, EventTypes.battle_end, context)
            is_hero_live(target, action.actor, context)
        else:
            event_listener_calculator(actor, target, EventTypes.battle_start, context)
            event_listener_calculator(actor, target, EventTypes.skill_single_damage_start, context)
            event_listener_calculator(actor, target, EventTypes.damage_start, context)
            apply_damage(action, context)
            event_listener_calculator(actor, target, EventTypes.damage_end, context)
            event_listener_calculator(actor, target, EventTypes.skill_single_damage_end, context)
            if is_hero_live(target, actor, context):
                action_wrapper_counterattack(context)
            event_listener_calculator(actor, target, EventTypes.battle_end, context)
            event_listener_calculator(actor, target, actions_end_event_type, context)
            event_listener_calculator(actor, target, EventTypes.action_end, context)
            is_hero_live(action.actor, True, context)
    else:
        for target in action.targets:
            event_listener_calculator(actor, target, EventTypes.skill_range_damage_start, context)
            event_listener_calculator(actor, target, EventTypes.damage_start, context)
            apply_damage(action, context)
            event_listener_calculator(actor, target, EventTypes.damage_end, context)
            event_listener_calculator(actor, target, EventTypes.skill_range_damage_end, context)
            event_listener_calculator(actor, target, actions_end_event_type, context)
            event_listener_calculator(actor, target, EventTypes.action_end, context)
            apply_additional_move()
            apply_additional_skill()
            is_hero_live(target, actor, context)

    # check liveness of all the heroes
    for hero in context.heroes:
        if hero.id != actor.id:
            is_hero_live(hero, None, context)

    # TODO Critical
    event_listener_calculator(actor, None, actions_end_event_type, context)
    event_listener_calculator(actor, None, EventTypes.action_end, context)

    # trigger partners event listener
    for hero in context.heroes:
        if hero.player_id == context.get_heroes_by_player_id(actor.player_id):
            event_listener_calculator(hero, actor, EventTypes.partner_action_end, context)
        else:
            event_listener_calculator(hero, actor, EventTypes.enemy_action_end, context)
