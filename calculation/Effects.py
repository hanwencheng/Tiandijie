from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from primitives.hero import Hero
    from calculation.Range import Range
    from primitives import Context, Action
    from primitives.buff.Buff import Buff
    from primitives.buff import BuffTemp

import random
from typing import List
from calculation.attribute_calculator import get_defense, get_attack, get_max_life
from calculation.calculate_damage import calculate_fix_damage, calculate_magic_damage, \
    calculate_physical_damage
from primitives.buff.BuffTemp import BuffTypes




def get_current_action(context: Context) -> Action:
    return context.actions[-1]


def check_is_attacker(actor: Hero, context: Context) -> bool:
    return actor.id == get_current_action(context).actor.id


def _add_buffs(caster: Hero, target: Hero, buff_temp: List[BuffTemp], duration: int, context: Context):
    new_buffs = [Buff(b, duration, caster.id) for b in buff_temp]
    for new_buff in new_buffs:
        existing_buff = next((buff for buff in target.buffs if buff.temp.id == new_buff.temp.id), None)
        if existing_buff is not None:
            # Replace the existing buff if the new buff has a higher level
            if new_buff.temp.level > existing_buff.temp.level:
                target.buffs.remove(existing_buff)
                target.buffs.append(new_buff)
            else:
                existing_buff.duration = duration
        else:
            target.buffs.append(new_buff)


class Effects:
    @staticmethod
    def heal_self(multiplier: float, actor_instance: Hero, target_instance: Hero, context: Context):
        actor_max_life = get_max_life(actor_instance, target_instance, context)
        actor_instance.life += actor_max_life * multiplier
        if actor_instance.life > actor_max_life:
            actor_instance.life = actor_max_life

    @staticmethod
    def remove_partner_harm_buffs(buff_count: int, range_value: int, actor_instance: Hero, target_instance: Hero, context: Context):
        partners = context.get_partners_in_range(actor_instance, range_value)
        for partner in partners:
            selected_harm_buffs = random.sample(context.harm_buffs, buff_count)
            for selected_harm_buff in selected_harm_buffs:
                partner.buffs = [buff for buff in partner.buffs if buff.temp.id != selected_harm_buff.id]

    @staticmethod
    def add_buffs(target: Hero, buff_temp: List[BuffTemp], duration: int, is_attacker: bool, context: Context):
        actor = context.actor
        _add_buffs(actor, target, buff_temp, duration)

    @staticmethod
    def add_fixed_damage_with_attack_and_defense(multiplier: float, is_magic: bool, actor_instance: Hero,
                                                 target_instance: Hero, context: Context):
        if check_is_attacker(actor_instance, context):
            damage = (get_attack(actor_instance, target_instance, is_magic, context) + get_defense(
                target_instance, actor_instance, is_magic, context)) * multiplier
            calculate_fix_damage(damage, actor_instance, target_instance, context)

    @staticmethod
    def add_target_harm_buffs(buff_temp_ids: List[str], duration: int, actor_instance: Hero,
                              target_instance: Hero, context: Context):
        buff_temps = [context.get_harm_buff_temp_by_id(buff_temp_id) for buff_temp_id in buff_temp_ids]
        add_buffs = map(lambda b: Buff(b, duration, actor_instance.id), buff_temps)
        target_instance.buffs.extend(add_buffs)

    @staticmethod
    def reduce_target_benefit_buff_duration(duration_reduction: int, is_attacker: bool, context: Context):
        action = context.get_action_by_side(is_attacker)
        for target in action.targets:
            for buff in target.buffs:
                if buff.type == BuffTypes.Benefit:  # Assuming each buff has an 'is_advantage' attribute
                    buff.duration -= duration_reduction
                    if buff.duration < 0:
                        buff.duration = 0  # Prevent negative duration

    @staticmethod
    def check_buff_conditional_add_target_buff(check_buff: BuffTemp, add_buff: BuffTemp, duration: int,
                                               is_attacker: bool, context: Context):
        actor = context.get_actor_by_side_in_battle(is_attacker)
        action = context.get_action_by_side(is_attacker)
        if any(buff.temp == check_buff for buff in actor.buffs):
            for target in action.targets:
                _add_buffs(actor, target, [add_buff], duration)

    @staticmethod
    def add_partner_harm_buffs(buff_number: int, range_value: int, duration: int, is_attacker: bool, context: Context):
        actor = context.get_actor_by_side_in_battle(is_attacker)
        partners = context.get_partners_in_range(actor, range_value)
        selected_harm_buff_temps = random.sample(context.harm_buffs, buff_number)
        for partner in partners:
            _add_buffs(actor, partner, selected_harm_buff_temps, duration)

    @staticmethod
    def remove_partner_selected_buffs(buff_temp: BuffTemp, range_value: int, is_attacker: bool, context: Context):
        actor = context.get_actor_by_side_in_battle(is_attacker)
        partners = context.get_partners_in_range(actor, range_value)
        for partner in partners:
            partner.buffs = [buff for buff in partner.buffs if buff.temp.id != buff_temp.id]

    @staticmethod
    def clear_terrain_in_range(range_class: Range, is_attacker: bool, context: Context):
        terrain = context.terrain
        for i in range_class.get_area(context):
            terrain[i] = None

    @staticmethod
    def take_magic_damage_of_buff_caster(multiplier: float, actor_instance: Hero, target_instance: Hero, context: Context, buff: Buff):
        caster_hero = context.get_hero_by_id(buff.caster_id)
        if caster_hero.alive:
            caster_magic_attack = get_attack(actor_instance, target_instance, context, True, True)
            calculate_magic_damage(caster_magic_attack * multiplier, caster_hero, actor_instance, context)

    @staticmethod
    def take_physical_damage(multiplier: float, is_attacker: bool, context: Context, caster_id: str):
        actor = context.getlast_action().actor
        caster_hero = context.get_hero_by_id(caster_id)
        if caster_hero.alive:
            caster_attack = get_attack(caster_hero, actor, context, False, True)
            calculate_physical_damage(caster_attack * multiplier, is_attacker, actor, context)

    @staticmethod
    def take_fixed_damage_by_percentage(percentage: float, actor_instance: Hero, target_instance: Hero or None,
                                        context: Context):
        actor_max_life = get_max_life(actor_instance, target_instance, context)
        calculate_fix_damage(actor_max_life * percentage, actor_instance, target_instance, context)

    @staticmethod
    def take_fixed_damage_by_percentage_per_each_move(percentage: float, is_attacker: bool, context: Context):
        action = context.get_action_by_side(is_attacker)
        actor = context.get_actor_by_side_in_battle(is_attacker)
        move_count = len(action.moves)
        actor_max_life = get_max_life(actor, is_attacker, context)
        calculate_fix_damage(actor_max_life * percentage * move_count, is_attacker, actor, context)

    @staticmethod
    def remove_actor_certain_buff(buff_temp_id: str, actor: Hero, target: Hero, context: Context):
        actor.buffs = [buff for buff in actor.buffs if buff.temp.id != buff_temp_id]

    @staticmethod
    def remove_target_certain_buff(buff_temp_id: str, actor: Hero, target: Hero, context: Context):
        target.buffs = [buff for buff in target.buffs if buff.temp.id != buff_temp_id]
