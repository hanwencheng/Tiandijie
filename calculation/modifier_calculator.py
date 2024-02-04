from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from calculation.Modifier import Modifier
    from primitives.Context import Context
    from primitives.effects.ModifierEffect import ModifierEffect
    from primitives.formation.Formation import Formation
    from primitives.hero.Hero import Hero
from functools import reduce
from typing import List
from calculation.BuffStack import calculate_buff_with_max_stack


def accumulate_attribute(modifiers: List[Modifier], attr_name: str) -> float:
    return reduce(lambda total, buff: total + getattr(buff, attr_name, 0), modifiers, 0)


def merge_modifier(total: Modifier, hero: Hero, attr_name: str) -> Modifier:
    setattr(total, attr_name, getattr(total, attr_name, 0) + getattr(hero.temp.talents, attr_name, 0))
    return total


def accumulate_talents_modifier(attr_name: str, actor_instance: Hero, target_instance: Hero, context: Context) -> float:
    player_id = actor_instance.player_id
    partner_heroes = context.get_heroes_by_player_id(player_id)
    counter_heroes = context.get_heroes_by_counter_player_id(player_id)

    partner_talents = reduce(lambda total, hero: total + getattr(hero.talents, attr_name), partner_heroes, float(0))
    counter_talents = reduce(lambda total, hero: total + getattr(total, hero.talents, attr_name), counter_heroes,
                             float(0))
    return partner_talents + counter_talents


def get_formation_modifier(attr_name: str, actor_instance: Hero, target_instance: Hero, context: Context) -> float:
    player_id = actor_instance.player_id
    current_formation: Formation = context.get_formation_by_player_id(player_id)
    basic_modifier_value = 0
    if current_formation.is_active:
        basic_modifier_value = getattr(current_formation.temp.basic_modifier, attr_name)
        formation_modifier_effects: List[ModifierEffect] = current_formation.temp.modifier_effects
        for effect in formation_modifier_effects:
            if hasattr(effect.modifier, attr_name):
                multiplier = effect.requirement(actor_instance, target_instance, context)
                if multiplier > 0:
                    basic_modifier_value += getattr(effect.modifier, attr_name) * multiplier
    return basic_modifier_value


def get_buff_modifier(attr_name: str, actor_instance: Hero, target_instance: Hero, context: Context) ->  float:
    basic_modifier_value = 0
    for buff in actor_instance.buffs:
        buff_modifier_levels_effects = buff.temp.modifier_effects
        buff_modifier_effects: List[ModifierEffect] = buff_modifier_levels_effects[buff.level - 1]
        for modifier_effects in buff_modifier_effects:
            if hasattr(modifier_effects.modifier, attr_name):
                is_requirement_meet = modifier_effects.requirement(actor_instance, target_instance, context, buff)
                if is_requirement_meet > 0:
                    basic_modifier_value += calculate_buff_with_max_stack(buff, modifier_effects.modifier, attr_name)
    return basic_modifier_value


def get_battle_damage_modifier(is_attacker: bool, context: Context) -> float:
    action = context.get_action_by_side(is_attacker)
    is_in_battle = action.is_in_battle
    if is_in_battle:
        return get_formation_modifier(ma.battle_damage_percentage, is_attacker, context)
    else:
        return 0


def get_level1_modified_result(hero_instance: Hero, value_attr_name: str, basic: float) -> float:
    accumulated_stones_value_modifier = accumulate_attribute(hero_instance.stones.value, value_attr_name)
    accumulated_stones_percentage_modifier = accumulate_attribute(hero_instance.stones.percentage,
                                                                  value_attr_name + '_percentage')
    return basic * (1 + accumulated_stones_percentage_modifier) + accumulated_stones_value_modifier


def get_level2_modifier(actor_instance: Hero, counter_instance: Hero, attr_name: str, context: Context, is_basic: bool = False) -> float:
    accumulated_buffs_modifier = accumulate_attribute(actor_instance.buffs, attr_name) if not is_basic else 0
    accumulated_stones_effect_modifier = accumulate_attribute(actor_instance.stones.effect, attr_name)
    accumulated_talents_modifier = accumulate_talents_modifier(attr_name, actor_instance, counter_instance, context)
    accumulated_equipments_modifier = accumulate_attribute(actor_instance.equipments, attr_name)
    formation_modifier = get_formation_modifier(attr_name, actor_instance, counter_instance, context)
    accumulated_passives_modifier = accumulate_attribute(actor_instance.enabled_passives, attr_name)

    return accumulated_talents_modifier + accumulated_buffs_modifier + accumulated_stones_effect_modifier + accumulated_equipments_modifier + formation_modifier + accumulated_passives_modifier


def get_modifier(attr_name: str, actor_instance: Hero, counter_instance: Hero, context: Context) -> float:
    accumulated_buffs_modifier = get_buff_modifier(attr_name, actor_instance, counter_instance, context)
    accumulated_talents_modifier = accumulate_talents_modifier(attr_name, actor_instance, counter_instance, context)
    accumulated_equipments_modifier = accumulate_attribute(actor_instance.equipments, attr_name)
    accumulated_passives_modifier = accumulate_attribute(actor_instance.enabled_passives, attr_name)

    return accumulated_talents_modifier + accumulated_buffs_modifier + accumulated_equipments_modifier + accumulated_passives_modifier
