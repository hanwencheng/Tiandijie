from __future__ import annotations
from typing import TYPE_CHECKING

from state.state_calculator import check_if_counterattack_first, check_if_in_battle, check_protector

if TYPE_CHECKING:
    from primitives.Context import Context
    from primitives.Action import Action
    from primitives.hero.Hero import Hero
    from basics import Position

from typing import Callable, List

from calculation.Range import calculate_if_targe_in_diamond_range
from calculation.calculate_damage import apply_damage, \
    apply_counterattack_damage
from calculation.event_calculator import event_listener_calculator
from calculation.modifier_calculator import get_modifier
from primitives.Action import ActionTypes

from primitives.effects.Event import EventTypes
from primitives.skill.SkillTemp import SkillTargetTypes


# move actor to the desired position
def apply_move(action: Action):
    actor = action.actor
    actor.update_position(action.move_point)


action_type_to_event_dict: dict[ActionTypes, tuple[EventTypes, EventTypes]] = {
    ActionTypes.HEAL: (EventTypes.heal_start, EventTypes.heal_end),
    ActionTypes.SKILL_ATTACK: (EventTypes.damage_start, EventTypes.damage_end),
    ActionTypes.NORMAL_ATTACK: (EventTypes.normal_attack_start, EventTypes.normal_attack_end),
    ActionTypes.SUMMON: (EventTypes.summon_start, EventTypes.summon_end),
    ActionTypes.SELF: (EventTypes.self_start, EventTypes.self_end),
    ActionTypes.PASS: (EventTypes.pass_start, EventTypes.pass_end),
    ActionTypes.COUNTERATTACK: (EventTypes.counterattack_start, EventTypes.counterattack_end),
}

skill_type_to_event_dict: dict[SkillTargetTypes, tuple[EventTypes, EventTypes]] = {
    SkillTargetTypes.ENEMY_SINGLE: (EventTypes.skill_single_damage_start, EventTypes.skill_single_damage_end),
    SkillTargetTypes.ENEMY_RANGE: (EventTypes.skill_range_damage_start, EventTypes.skill_range_damage_end),
    SkillTargetTypes.PARTNER_SINGLE: (EventTypes.skill_for_partner_start, EventTypes.skill_for_partner_end),
    SkillTargetTypes.PARTNER_RANGE: (EventTypes.skill_for_partner_start, EventTypes.skill_for_partner_end),
    SkillTargetTypes.SELF: (EventTypes.skill_for_self_start, EventTypes.skill_for_self_end),
    SkillTargetTypes.TERRAIN: (EventTypes.skill_for_terrain_start, EventTypes.skill_for_terrain_end),
}


def counterattack_actions(context: Context):
    action = context.get_last_action()
    counter_attacker = action.get_defender_hero_in_battle()
    actor = action.actor
    event_listener_calculator(counter_attacker, actor, EventTypes.counterattack_start, context)
    event_listener_calculator(actor, counter_attacker, EventTypes.counterattack_start, context)
    apply_counterattack_damage(counter_attacker, action.actor, action, context)
    event_listener_calculator(counter_attacker, actor, EventTypes.counterattack_end, context)
    event_listener_calculator(actor, counter_attacker, EventTypes.counterattack_end, context)


def skill_attack_actions(actor: Hero, target: Hero, action: Action, context: Context):
    actions_start_event_type = action_type_to_event_dict[action.type][0]
    actions_end_event_type = action_type_to_event_dict[action.type][1]
    event_listener_calculator(actor, None, actions_start_event_type, context)
    event_listener_calculator(actor, target, EventTypes.skill_single_damage_start, context)
    event_listener_calculator(target, actor, EventTypes.skill_single_damage_start, context)
    attack_actions(actor, target, action, context)
    event_listener_calculator(actor, target, EventTypes.skill_single_damage_end, context)
    event_listener_calculator(target, actor, EventTypes.skill_single_damage_end, context)
    event_listener_calculator(actor, None, actions_end_event_type, context)


def attack_actions(actor: Hero, target: Hero, action: Action, context: Context):
    event_listener_calculator(actor, target, EventTypes.damage_start, context)
    event_listener_calculator(target, actor, EventTypes.damage_start, context)
    apply_damage(action, context)
    event_listener_calculator(actor, target, EventTypes.damage_end, context)
    event_listener_calculator(target, actor, EventTypes.damage_end, context)


def battle_attack_actions(actor: Hero, target: Hero, action: Action, context: Context):
    event_listener_calculator(actor, target, EventTypes.battle_start, context)
    event_listener_calculator(target, actor, EventTypes.battle_start, context)
    if check_if_counterattack_first(action, context):
        counterattack_actions(context)  # take damage
        if is_hero_live(actor, target, context):
            attack_actions(actor, target, action, context)
        event_listener_calculator(actor, target, EventTypes.battle_end, context)
        event_listener_calculator(target, actor, EventTypes.battle_end, context)
        is_hero_live(target, actor, context)
    else:
        attack_actions(actor, target, action, context)
        if is_hero_live(target, actor, context):
            counterattack_actions(context)
        event_listener_calculator(actor, target, EventTypes.battle_end, context)
        event_listener_calculator(target, actor, EventTypes.battle_end, context)
        is_hero_live(actor, target, context)


def action_wrapper_battle(context: Context, action_func: Callable[[Hero, Hero or None, Context], None]):
    actor = context.get_last_action().actor
    target = context.get_last_action().get_defender_hero_in_battle()
    event_listener_calculator(actor, target, EventTypes.battle_start, context)
    action_func(actor, target, context)
    event_listener_calculator(actor, target, EventTypes.battle_end, context)


def attack_damage_events(actor_instance: Hero, counter_instance: Hero or None, context: Context):
    action = context.get_last_action()
    skill_start_event_type = skill_type_to_event_dict[action.skill.target_type][0]
    skill_end_event_type = skill_type_to_event_dict[action.skill.target_type][1]
    event_listener_calculator(actor_instance, counter_instance, skill_start_event_type, context)
    event_listener_calculator(actor_instance, counter_instance, EventTypes.damage_start, context)
    apply_damage(action, context)
    event_listener_calculator(actor_instance, counter_instance, EventTypes.damage_end, context)
    event_listener_calculator(actor_instance, counter_instance, skill_end_event_type, context)


def is_hero_live(hero_instance: Hero, counter_instance: Hero or None, context: Context):
    if hero_instance.current_life <= 0:
        event_listener_calculator(hero_instance, counter_instance, EventTypes.hero_death, context)
        context.set_hero_died(hero_instance)


def apply_additional_move(position: Position, context: Context):
    actor = context.get_last_action().actor
    actor.update_position(position)


def apply_additional_skill(context: Context):
    actor = context.get_last_action().actor


def apply_action(context: Context, action: Action):
    if not action.actionable:
        return

    actor = context.get_last_action().actor
    context.add_action(action)
    actions_start_event_type = action_type_to_event_dict[action.type][0]
    actions_end_event_type = action_type_to_event_dict[action.type][1]

    event_listener_calculator(actor, None, EventTypes.move_start, context)

    if action.movable:
        apply_move(action)

    event_listener_calculator(actor, None, EventTypes.move_end, context)

    check_protector(context)
    action.update_is_in_battle(check_if_in_battle(action, context))

    if action.is_in_battle:
        target = action.get_defender_hero_in_battle()
        battle_attack_actions(action.actor, target, action, context)

        event_listener_calculator(actor, target, EventTypes.action_end, context)
        is_hero_live(action.actor, True, context)
    else:
        for target in action.targets:
            event_listener_calculator(actor, target, EventTypes.skill_range_damage_start, context)
            attack_actions(actor, target, action, context)
            event_listener_calculator(actor, target, EventTypes.skill_range_damage_end, context)
            event_listener_calculator(actor, target, EventTypes.action_end, context)
            # if action.additional_move > 0:
            # apply_additional_move()
            # event_listener_calculator(actor, None, EventTypes.move_end, context)
            # if action.additional_skill is not None:
            # apply_additional_skill()
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

def generate_legal_actions():
    pass
