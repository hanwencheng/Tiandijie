from __future__ import annotations

from random import random
from typing import TYPE_CHECKING

from calculation.damage_calculator import (
    calculate_fix_damage,
    calculate_magic_damage,
    calculate_physical_damage,
)
from calculation.healCalculation import (
    calculate_fix_heal,
)
from helpers import random_select

if TYPE_CHECKING:
    from primitives.hero import Hero
    from calculation.Range import Range
    from primitives import Context, Action
    from primitives.buff.Buff import Buff
    from primitives.buff import BuffTemp

from typing import List
from calculation.attribute_calculator import get_defense, get_attack, get_max_life
from primitives.buff.BuffTemp import BuffTypes
from calculation.BuffStack import get_buff_max_stack
from calculation.BuffTriggerLimit import get_buff_max_trigger_limit


def get_current_action(context: Context) -> Action:
    return context.actions[-1]


def check_is_attacker(actor: Hero, context: Context) -> bool:
    return actor.id == get_current_action(context).actor.id


def _add_buffs(
    caster: Hero,
    target: Hero,
    buff_temp: List[BuffTemp],
    duration: int,
    context: Context,
):
    new_buffs = [Buff(b, duration, caster.id) for b in buff_temp]
    for new_buff in new_buffs:
        existing_buff = next(
            (buff for buff in target.buffs if buff.temp.id == new_buff.temp.id), None
        )
        if existing_buff is not None:
            # Replace the existing buff if the new buff has a higher level
            if new_buff.level > existing_buff.level:
                target.buffs.remove(existing_buff)
                target.buffs.append(new_buff)
            else:
                existing_buff.duration = duration
        else:
            target.buffs.append(new_buff)


def _remove_actor_certain_buff(buff_temp_id: str, actor: Hero):
    actor.buffs = [buff for buff in actor.buffs if buff.temp.id != buff_temp_id]


def _reduce_actor_certain_buff_stack(
    buff_temp_id: str, actor: Hero, reduced_stack: int
):
    for buff in actor.buffs:
        if buff.temp.id == buff_temp_id:
            buff.stack -= reduced_stack
            if buff.temp.level <= 0:
                actor.buffs.remove(buff)
            break


def _increase_actor_certain_buff_stack(
    buff_temp_id: str, actor: Hero, increase_stack: int
):
    for buff in actor.buffs:
        if buff.temp.id == buff_temp_id:
            if buff.stack >= get_buff_max_stack(buff.temp):
                return
            buff.stack += increase_stack
            break


def _increase_actor_energy(actor: Hero, increase_stack: int):
    pass


def _reduce_actor_energy(actor: Hero, increase_stack: int):
    pass


def _increase_actor_certain_buff_max_stack(buff_temp_id: str, actor: Hero):
    for buff in actor.buffs:
        if buff.temp.id == buff_temp_id:
            buff.stack = get_buff_max_stack(buff.temp)
            break


def _reserve_buffs(
    actor: Hero, target: Hero, is_benfit: bool, buff_count: int, context: Context
):
    if is_benfit:
        target_buffs = [
            buff for buff in target.buffs if buff.temp.type == BuffTypes.Benefit
        ]
    else:
        target_buffs = [
            buff for buff in target.buffs if buff.temp.type == BuffTypes.Harm
        ]
    if not target_buffs:
        return
    selected_buffs = random_select(target_buffs, buff_count)
    new_opposite_buffs = random_select(context.harm_buffs, buff_count)

    for i in range(buff_count):
        _remove_actor_certain_buff(selected_buffs[i].temp.id, target)
        _add_buffs(
            actor,
            target,
            [new_opposite_buffs[i].temp],
            selected_buffs[i].duration,
            context,
        )


class Effects:

    @staticmethod
    def remove_caster_harm_buff(
        buff_count: 1,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        buff: Buff,
    ):
        caster = context.get_hero_by_id(buff.caster_id)
        selected_buffs = random_select(caster.buffs, buff_count)
        for selected_buff in selected_buffs:
            _remove_actor_certain_buff(selected_buff.temp.id, caster)

    @staticmethod
    def add_enemies_harm_buff_and(
        additional_buff_name: str,
        enemy_number: int,
        buff_number: int,
        square_range: int,
        duration: int,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
    ):
        targets = context.get_enemies_in_square_range(actor_instance, square_range)
        selected_harm_buff_temps = random_select(context.harm_buffs, buff_number)
        additional_buff_temp = context.get_buff_by_id(additional_buff_name)
        if additional_buff_temp is not None:
            selected_harm_buff_temps.append(
                context.get_buff_by_id(additional_buff_name)
            )
        selected_heroes = random_select(targets, enemy_number)
        for enemy_hero in selected_heroes:
            _add_buffs(
                actor_instance, enemy_hero, selected_harm_buff_temps, duration, context
            )

    @staticmethod
    def add_enemies_harm_buff(
        enemy_number: int,
        buff_number: int,
        square_range: int,
        duration: int,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
    ):
        targets = context.get_enemies_in_square_range(actor_instance, square_range)
        selected_harm_buff_temps = random_select(context.harm_buffs, buff_number)
        selected_heroes = random_select(targets, enemy_number)
        for enemy_hero in selected_heroes:
            _add_buffs(
                actor_instance, enemy_hero, selected_harm_buff_temps, duration, context
            )

    @staticmethod
    def add_all_harm_buff_in_range(
        buff_number: int,
        square_range: int,
        duration: int,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
    ):
        targets = context.get_enemies_in_square_range(actor_instance, square_range)
        selected_harm_buff_temps = random_select(context.harm_buffs, buff_number)
        for enemy_hero in targets:
            _add_buffs(
                actor_instance, enemy_hero, selected_harm_buff_temps, duration, context
            )

    @staticmethod
    def reduce_skill_cooldown(
        cooldown_reduction: int,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
    ):
        skill_id = context.get_last_action().skill.id
        for skills in actor_instance.enabled_skills:
            if skills.id == skill_id:
                skills.cooldown -= cooldown_reduction
                if skills.cooldown < 0:
                    skills.cooldown = 0

    @staticmethod
    def replace_buff(
        existed_buff_id: str,
        new_buff_id: str,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
    ):
        _remove_actor_certain_buff(existed_buff_id, target_instance)
        _add_buffs(
            actor_instance,
            target_instance,
            [context.get_buff_temp_by_id(new_buff_id)],
            2,
            context,
        )

    @staticmethod
    def replace_self_buff(
        existed_buff_id: str,
        new_buff_id: str,
        duration: int,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        buff: Buff,
    ):
        caster = context.get_hero_by_id(buff.caster_id)
        _remove_actor_certain_buff(existed_buff_id, actor_instance)
        _add_buffs(
            caster,
            actor_instance,
            [context.get_buff_temp_by_id(new_buff_id)],
            duration,
            context,
        )

    @staticmethod
    def take_effect_of_xiayi(
        actor_instance: Hero, target_instance: Hero, context: Context
    ):
        context.get_last_action().update_additional_move(4)
        _reduce_actor_certain_buff_stack("xiayi", actor_instance, 2)

    @staticmethod
    def increase_actor_certain_buff_stack(
        buff_id: str, actor_instance: Hero, target_instance: Hero, context: Context
    ):
        _increase_actor_certain_buff_stack(buff_id, actor_instance, 1)

    @staticmethod
    def increase_actor_certain_buff_max_stack(
        buff_id: str, actor_instance: Hero, target_instance: Hero, context: Context
    ):
        _increase_actor_certain_buff_max_stack(buff_id, actor_instance)

    @staticmethod
    def reduce_actor_certain_buff_stack(
        buff_id: str,
        stack_value: int,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
    ):
        _reduce_actor_certain_buff_stack(buff_id, actor_instance, stack_value)

    @staticmethod
    def heal_self(
        multiplier: float, actor_instance: Hero, target_instance: Hero, context: Context
    ):
        actor_max_life = get_max_life(actor_instance, target_instance, context)
        calculate_fix_heal(
            actor_max_life * multiplier, actor_instance, actor_instance, context
        )

    @staticmethod
    def heal_caster(
        multiplier: float,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        buff: Buff,
    ):
        caster_hero = context.get_hero_by_id(buff.caster_id)
        caster_max_life = get_max_life(caster_hero, actor_instance, context)
        calculate_fix_heal(
            caster_max_life * multiplier, actor_instance, caster_max_life, context
        )

    @staticmethod
    def heal_self_by_caster_physical_attack(
        multiplier: float,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        buff: Buff,
    ):
        caster_hero = context.get_hero_by_id(buff.caster_id)
        caster_magic_attack = get_attack(
            caster_hero, target_instance, context, False, True
        )
        calculate_fix_heal(
            caster_magic_attack * multiplier, actor_instance, target_instance, context
        )

    @staticmethod
    def heal_self_by_caster_magic_attack(
        multiplier: float,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        buff: Buff,
    ):
        caster_hero = context.get_hero_by_id(buff.caster_id)
        caster_magic_attack = get_attack(
            caster_hero, target_instance, context, True, True
        )
        calculate_fix_heal(
            caster_magic_attack * multiplier, actor_instance, target_instance, context
        )

    @staticmethod
    def remove_partner_harm_buffs(
        buff_count: int,
        range_value: int,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
    ):
        partners = context.get_partners_in_diamond_range(actor_instance, range_value)
        for partner in partners:
            selected_harm_buffs = random_select(context.harm_buffs, buff_count)
            for selected_harm_buff in selected_harm_buffs:
                partner.buffs = [
                    buff
                    for buff in partner.buffs
                    if buff.temp.id != selected_harm_buff.id
                ]

    @staticmethod
    def add_buffs(
        target: Hero,
        buff_temp: List[BuffTemp],
        duration: int,
        is_attacker: bool,
        context: Context,
    ):
        actor = context.actor
        _add_buffs(actor, target, buff_temp, duration, context)

    @staticmethod
    def add_self_buffs(
        buff_temp: List[BuffTemp],
        duration: int,
        is_attacker: bool,
        context: Context,
    ):
        actor = context.actor
        _add_buffs(actor, actor, buff_temp, duration, context)

    @staticmethod
    def add_caster_buffs(
        buff_temp: List[BuffTemp],
        duration: int,
        is_attacker: bool,
        context: Context,
        buff: Buff,
    ):
        caster = context.get_hero_by_id(buff.caster_id)
        actor = context.actor
        _add_buffs(actor, caster, buff_temp, duration, context)

    @staticmethod
    def add_fixed_damage_with_attack_and_defense(
        multiplier: float,
        is_magic: bool,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
    ):
        if check_is_attacker(actor_instance, context):
            damage = (
                get_attack(actor_instance, target_instance, context, is_magic)
                + get_defense(actor_instance, target_instance, context, is_magic)
            ) * multiplier
            calculate_fix_damage(damage, actor_instance, target_instance, context)

    @staticmethod
    def add_fixed_damage_with_physical_attack(
        multiplier: float,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
    ):
        if check_is_attacker(actor_instance, context):
            damage = (
                get_attack(actor_instance, target_instance, context, False) * multiplier
            )
            calculate_fix_damage(damage, actor_instance, target_instance, context)

    @staticmethod
    def add_fixed_damage_with_physical_and_magic_attack(
        multiplier: float,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
    ):
        if check_is_attacker(actor_instance, context):
            damage = (
                get_attack(actor_instance, target_instance, context, False)
                + get_attack(actor_instance, target_instance, context, True)
            ) * multiplier
            calculate_fix_damage(damage, actor_instance, target_instance, context)

    @staticmethod
    def add_fixed_damage_in_range_by_physical_defense(
        multiplier: float,
        range_value: int,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
    ):
        enemies = context.get_enemies_in_square_range(actor_instance, range_value)
        for enemy in enemies:
            damage = get_defense(enemy, actor_instance, context, False) * multiplier
            calculate_fix_damage(damage, actor_instance, enemy, context)

    @staticmethod
    def add_fixed_damage_in_range_by_max_life(
        multiplier: float,
        range_value: int,
        actor: Hero,
        target: Hero,
        context: Context,
        buff: Buff,
    ):
        caster = context.get_hero_by_id(buff.caster_id)
        targets = context.get_partners_in_diamond_range(actor, range_value)
        for target in targets:
            damage = get_max_life(target, actor, context) * multiplier
            calculate_fix_damage(damage, caster, target, context)
        damage = get_max_life(actor, target, context) * multiplier
        calculate_fix_damage(damage, caster, actor, context)

    @staticmethod
    def add_fixed_damage_in_diamond_range_by_caster_magic_attack(
        multiplier: float,
        range_value: int,
        actor: Hero,
        target: Hero,
        context: Context,
        buff: Buff,
    ):
        caster = context.get_hero_by_id(buff.caster_id)
        targets = context.get_enemies_in_diamond_range(caster, range_value)
        for target in targets:
            damage = get_attack(caster, target, context, True, True) * multiplier
            calculate_fix_damage(damage, caster, target, context)

    @staticmethod
    def add_fixed_damage_in_range_by_caster_magic_attack(
        multiplier: float,
        range_value: int,
        actor: Hero,
        target: Hero,
        context: Context,
        buff: Buff,
    ):
        caster = context.get_hero_by_id(buff.caster_id)
        targets = context.get_enemies_in_square_range(caster, range_value)
        for target in targets:
            damage = get_attack(caster, target, context, True, True) * multiplier
            calculate_fix_damage(damage, caster, target, context)

    @staticmethod
    def add_fixed_damage_in_range_by_caster_physical_attack(
        multiplier: float,
        range_value: int,
        actor: Hero,
        target: Hero,
        context: Context,
        buff: Buff,
    ):
        caster = context.get_hero_by_id(buff.caster_id)
        targets = context.get_enemies_in_square_range(caster, range_value)
        for target in targets:
            damage = get_attack(caster, target, context, False, True) * multiplier
            calculate_fix_damage(damage, caster, target, context)

    @staticmethod
    def add_fixed_damage_by_caster_physical_attack(
        multiplier: float,
        actor: Hero,
        target: Hero,
        context: Context,
        buff: Buff,
    ):
        caster = context.get_hero_by_id(buff.caster_id)
        damage = get_attack(caster, actor, context, False) * multiplier
        calculate_fix_damage(damage, caster, actor, context)

    @staticmethod
    def add_fixed_damage_by_target_max_life(
        multiplier: float,
        actor: Hero,
        target: Hero,
        context: Context,
        buff: Buff,
    ):
        caster = context.get_hero_by_id(buff.caster_id)
        damage = get_max_life(target, actor, context) * multiplier
        calculate_fix_damage(damage, caster, actor, context)

    @staticmethod
    def receive_fixed_damage_by_current_life_percentage(
        multiplier: float,
        is_magic: bool,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        buff: Buff,
    ):
        caster_hero = context.get_hero_by_id(buff.caster_id)
        damage = actor_instance.current_life * multiplier
        calculate_fix_damage(damage, caster_hero, actor_instance, context)

    @staticmethod
    def receive_fixed_damage_by_max_life_percentage(
        multiplier: float,
        is_magic: bool,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        buff: Buff,
    ):
        caster_hero = context.get_hero_by_id(buff.caster_id)
        actor_max_life = get_max_life(actor_instance, target_instance, context)
        damage = actor_max_life * multiplier
        calculate_fix_damage(damage, caster_hero, actor_instance, context)

    @staticmethod
    def receive_fixed_damage_by_caster_physical_attack(
        multiplier: float,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        buff: Buff,
    ):
        caster_hero = context.get_hero_by_id(buff.caster_id)
        damage = get_attack(caster_hero, actor_instance, context, False) * multiplier
        calculate_fix_damage(damage, caster_hero, actor_instance, context)

    @staticmethod
    def receive_fixed_damage_by_caster_magic_attack(
        multiplier: float,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        buff: Buff,
    ):
        caster_hero = context.get_hero_by_id(buff.caster_id)
        damage = get_attack(caster_hero, actor_instance, context, True) * multiplier
        calculate_fix_damage(damage, caster_hero, actor_instance, context)

    @staticmethod
    def receive_fixed_damage_by_physical_defense_and_magic_defense(
        multiplier: float,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        buff: Buff,
    ):
        caster_hero = context.get_hero_by_id(buff.caster_id)
        damage = (
            get_defense(actor_instance, target_instance, context, False)
            + get_defense(actor_instance, target_instance, context, True)
        ) * multiplier
        calculate_fix_damage(damage, caster_hero, actor_instance, context)

    @staticmethod
    def add_target_harm_buffs(
        buff_temp_ids: List[str],
        duration: int,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
    ):
        buff_temps = [
            context.get_harm_buff_temp_by_id(buff_temp_id)
            for buff_temp_id in buff_temp_ids
        ]
        add_buffs = map(lambda b: Buff(b, duration, actor_instance.id), buff_temps)
        target_instance.buffs.extend(add_buffs)

    @staticmethod
    def reduce_target_benefit_buff_duration(
        duration_reduction: int, is_attacker: bool, context: Context
    ):
        action = context.get_action_by_side(is_attacker)
        for target in action.targets:
            for buff in target.buffs:
                if (
                    buff.type == BuffTypes.Benefit
                ):  # Assuming each buff has an 'is_advantage' attribute
                    buff.duration -= duration_reduction
                    if buff.duration < 0:
                        buff.duration = 0  # Prevent negative duration

    @staticmethod
    def check_buff_conditional_add_target_buff(
        check_buff: BuffTemp,
        add_buff: BuffTemp,
        duration: int,
        is_attacker: bool,
        context: Context,
    ):
        actor = context.get_actor_by_side_in_battle(is_attacker)
        action = context.get_action_by_side(is_attacker)
        if any(buff.temp == check_buff for buff in actor.buffs):
            for target in action.targets:
                _add_buffs(actor, target, [add_buff], duration, context)

    @staticmethod
    def add_partner_harm_buffs(
        buff_number: int,
        range_value: int,
        duration: int,
        is_attacker: bool,
        context: Context,
    ):
        actor = context.get_actor_by_side_in_battle(is_attacker)
        partners = context.get_partners_in_diamond_range(actor, range_value)
        selected_harm_buff_temps = random_select(context.harm_buffs, buff_number)
        for partner in partners:
            _add_buffs(actor, partner, selected_harm_buff_temps, duration, context)

    @staticmethod
    def add_partner_benefit_buffs(
        buff_number: int,
        range_value: int,
        duration: int,
        is_attacker: bool,
        context: Context,
    ):
        actor = context.get_actor_by_side_in_battle(is_attacker)
        partners = context.get_partners_in_diamond_range(actor, range_value)
        selected_benefit_buff_temps = random_select(context.benefit_buffs, buff_number)
        for partner in partners:
            _add_buffs(actor, partner, selected_benefit_buff_temps, duration, context)

    @staticmethod
    def remove_partner_selected_buffs(
        buff_temp: BuffTemp, range_value: int, is_attacker: bool, context: Context
    ):
        actor = context.get_actor_by_side_in_battle(is_attacker)
        partners = context.get_partners_in_diamond_range(actor, range_value)
        for partner in partners:
            partner.buffs = [
                buff for buff in partner.buffs if buff.temp.id != buff_temp.id
            ]

    @staticmethod
    def clear_terrain_in_range(range_class: Range, is_attacker: bool, context: Context):
        terrain = context.terrain
        for i in range_class.get_area(context):
            terrain[i] = None

    @staticmethod
    def receive_fixed_magic_damage_by_caster_magic_attack(
        multiplier: float,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        buff: Buff,
    ):
        caster_hero = context.get_hero_by_id(buff.caster_id)
        if caster_hero.alive:
            caster_magic_attack = get_attack(
                actor_instance, target_instance, context, True, True
            )
            calculate_magic_damage(
                caster_magic_attack * multiplier, caster_hero, actor_instance, context
            )

    @staticmethod
    def take_physical_damage(
        multiplier: float, is_attacker: bool, context: Context, caster_id: str
    ):
        actor = context.getlast_action().actor
        caster_hero = context.get_hero_by_id(caster_id)
        if caster_hero.alive:
            caster_attack = get_attack(caster_hero, actor, context, False, True)
            calculate_physical_damage(
                caster_attack * multiplier, is_attacker, actor, context
            )

    @staticmethod
    def take_fixed_damage_by_percentage(
        percentage: float,
        actor_instance: Hero,
        target_instance: Hero or None,
        context: Context,
    ):
        actor_max_life = get_max_life(actor_instance, target_instance, context)
        calculate_fix_damage(
            actor_max_life * percentage, actor_instance, target_instance, context
        )

    @staticmethod
    def take_fixed_damage_by_percentage_per_each_move(
        percentage: float, max_percentage: int, is_attacker: bool, context: Context
    ):
        action = context.get_action_by_side(is_attacker)
        actor = context.get_actor_by_side_in_battle(is_attacker)
        move_count = len(action.moves)
        actor_max_life = get_max_life(actor, is_attacker, context)
        multiplier = min(percentage * move_count, max_percentage)
        calculate_fix_damage(actor_max_life * multiplier, is_attacker, actor, context)

    @staticmethod
    def remove_actor_certain_buff(
        buff_temp_id: str, actor: Hero, target: Hero, context: Context
    ):
        _remove_actor_certain_buff(buff_temp_id, actor)

    @staticmethod
    def remove_target_certain_buff(
        buff_temp_id: str, actor: Hero, target: Hero, context: Context
    ):
        _remove_actor_certain_buff(buff_temp_id, target)

    @staticmethod
    def remove_actor_harm_buffs(
        count: int, actor: Hero, target: Hero, context: Context
    ):
        # collect all harm buffs in target.buffs and remove count number of them
        harm_buffs = [buff for buff in actor.buffs if buff.temp.type == BuffTypes.Harm]
        for harm_buff in harm_buffs[:count]:
            _remove_actor_certain_buff(harm_buff.temp.id, actor)

    @staticmethod
    def remove_self_harm_buffs(count: int, actor: Hero, target: Hero, context: Context):
        harm_buffs = [buff for buff in actor.buffs if buff.temp.type == BuffTypes.Harm]
        for harm_buff in harm_buffs[:count]:
            _remove_actor_certain_buff(harm_buff.temp.id, actor)

    @staticmethod
    def remove_target_harm_buffs_in_range(
        count: int, range_value: int, actor: Hero, target: Hero, context: Context
    ):

        enemies = context.get_enemies_in_square_range(actor, range_value)
        for enemy in enemies:
            harm_buffs = [
                buff for buff in enemy.buffs if buff.temp.type == BuffTypes.Harm
            ]
            for harm_buff in harm_buffs[:count]:
                _remove_actor_certain_buff(harm_buff.temp.id, enemy)

    @staticmethod
    def remove_partner_harm_buffs_in_range(
        count: int, range_value: int, actor: Hero, target: Hero, context: Context
    ):

        partners = context.get_enemies_in_square_range(actor, range_value)
        for partner in partners:
            harm_buffs = [
                buff for buff in partner.buffs if buff.temp.type == BuffTypes.Harm
            ]
            for harm_buff in harm_buffs[:count]:
                _remove_actor_certain_buff(harm_buff.temp.id, partner)

    @staticmethod
    def remove_actor_benefit_buffs(
        count: int, actor: Hero, target: Hero, context: Context
    ):
        harm_buffs = [
            buff for buff in actor.buffs if buff.temp.type == BuffTypes.Benefit
        ]
        for harm_buff in harm_buffs[:count]:
            _remove_actor_certain_buff(harm_buff.temp.id, actor)

    @staticmethod
    def remove_target_benefit_buffs(
        count: int, actor: Hero, target: Hero, context: Context
    ):
        # collect all benefit buffs in target.buffs and remove count number of them
        benefit_buffs = [
            buff for buff in target.buffs if buff.temp.type == BuffTypes.Benefit
        ]
        for benefit_buff in benefit_buffs[:count]:
            _remove_actor_certain_buff(benefit_buff.temp.id, target)

    @staticmethod
    def increase_target_harm_buff_level(
        buff_level: int, actor: Hero, target: Hero, context: Context
    ):
        harm_buffs = [buff for buff in target.buffs if buff.temp.type == BuffTypes.Harm]
        for buff in harm_buffs:
            if buff.temp.upgradable:
                buff.level += buff_level
                _add_buffs(actor, target, buff, buff.duration, context)

    @staticmethod
    def take_effect_of_tianjiyin(
        actor: Hero, target: Hero, is_attacker: bool, context: Context, buff: Buff
    ):
        partners = context.get_partners_in_diamond_range(actor, 3)
        if not partners:
            return
        damage = get_current_action(context).total_damage
        if damage > 0:  # 为3格范围内其他友方恢复气血（恢复量为施术者法攻的0.5倍）
            for partner in partners:
                Effects.heal_self_by_caster_magic_attack(
                    multiplier=0.5,
                    actor_instance=actor,
                    target_instance=partner,
                    context=context,
                    buff=buff,
                )
        else:  # 反之为自身3格范围内4个其他友方施加1个随机「有益状态」
            Effects.add_partner_benefit_buffs(
                buff_number=1,
                range_value=3,
                duration=2,
                is_attacker=is_attacker,
                context=Context,
            )

    @staticmethod
    def reverse_target_harm_buffs(
        buff_count: int, actor: Hero, target: Hero, context: Context
    ):
        _reserve_buffs(actor, target, False, buff_count, context)

    @staticmethod
    def reverse_target_benfit_buffs(
        buff_count: int, actor: Hero, target: Hero, context: Context
    ):
        _reserve_buffs(actor, target, True, buff_count, context)

    @staticmethod
    def reverse_target_benefit_buffs_in_range(
        buff_count: int, range_value: int, actor: Hero, target: Hero, context: Context
    ):
        enemies = context.get_enemies_in_square_range(actor, range_value)
        for enemy in enemies:
            _reserve_buffs(actor, enemy, True, buff_count, context)

    @staticmethod
    def reverse_self_harm_buffs(
        buff_count: int, actor: Hero, target: Hero, context: Context
    ):
        _reserve_buffs(actor, target, False, buff_count, context)

    @staticmethod
    def add_self_random_harm_buff(
        buff_count: int, actor: Hero, target: Hero, context: Context
    ):
        harm_buffs = random_select(context.harm_buffs, buff_count)
        _add_buffs(actor, actor, harm_buffs, 2, context)

    @staticmethod
    def add_self_random_benefit_buff(
        buff_count: int, actor: Hero, target: Hero, context: Context
    ):
        benefit_buffs = random_select(context.benefit_buffs, buff_count)
        _add_buffs(actor, actor, benefit_buffs, 2, context)

    @staticmethod
    def add_target_random_harm_buff(
        buff_count: int,
        actor: Hero,
        target: Hero,
        context: Context,
        buff: Buff,
    ):
        harm_buffs = random_select(context.harm_buffs, buff_count)
        _add_buffs(actor, target, harm_buffs, 2, context)

    @staticmethod
    def add_attacker_random_harm_buff_with_probability(
        buff_count: int,
        probability: float,
        actor: Hero,
        target: Hero,
        context: Context,
        buff: Buff,
    ):
        if random() < probability:
            harm_buffs = random_select(context.harm_buffs, buff_count)
            _add_buffs(actor, target, harm_buffs, 2, context)

    @staticmethod
    def add_partner_random_benefit_buff(
        buff_count: int, range_value: int, actor: Hero, target: Hero, context: Context
    ):
        benefit_buffs = random_select(context.benefit_buffs, buff_count)
        partners = context.get_partners_in_diamond_range(actor, range_value)
        for partner in partners:
            _add_buffs(actor, partner, benefit_buffs, 2, context)

    @staticmethod
    def kill_self(actor: Hero, target: Hero, context: Context):
        context.set_hero_died(actor)

    @staticmethod
    def heal_partner_and_add_benefit_buff_by_caster(
        multiplier: float,
        range_value: int,
        actor: Hero,
        target: Hero,
        context: Context,
        buff: Buff,
    ):
        caster_hero = context.get_hero_by_id(buff.caster_id)
        if caster_hero.alive:
            partners = context.get_partners_in_diamond_range(caster_hero, range_value)
            for partner in partners:
                Effects.heal_self_by_caster_magic_attack(
                    multiplier, actor, partner, context, buff
                )
                benefit_buffs = random_select(context.benefit_buffs, 1)
                _add_buffs(actor, partner, benefit_buffs, 2, context)

    @staticmethod
    def increase_self_loongest_skill_cooldown(
        cooldown_reduction: int, actor: Hero, target: Hero, context: Context
    ):
        longest_skill = max(actor.enabled_skills, key=lambda x: x.cool_down)
        longest_skill.cool_down += cooldown_reduction

    @staticmethod
    def reduce_self_all_skill_cooldown(
        cooldown_reduction: int, actor: Hero, target: Hero, context: Context
    ):
        for skill in actor.enabled_skills:
            skill.cool_down -= cooldown_reduction
            if skill.cool_down < 0:
                skill.cool_down = 0

    @staticmethod
    def reduce_self_ramdon_damage_skill_cooldown(
        cooldown_reduction: int, actor: Hero, target: Hero, context: Context
    ):
        pass
        # for skill in actor.enabled_skills:
        #     skill.cool_down -= cooldown_reduction
        #     if skill.cool_down < 0:
        #         skill.cool_down = 0

    @staticmethod
    def steal_target_benefit_buff(
        buff_count: int, actor: Hero, target: Hero, context: Context
    ):
        benefit_buffs = [
            buff for buff in target.buffs if buff.temp.type == BuffTypes.Benefit
        ]
        selected_buffs = random_select(benefit_buffs, buff_count)
        for selected_buff in selected_buffs:
            _remove_actor_certain_buff(selected_buffs.temp.id, target)
            _add_buffs(
                actor, actor, selected_buff.temp.id, selected_buff.duration, context
            )

    @staticmethod
    def stolen_self_benefit_buff_by_caster(
        buff_count: int, actor: Hero, target: Hero, context: Context, buff: Buff
    ):
        caster = context.get_hero_by_id(buff.caster_id)
        benefit_buffs = [
            buff for buff in actor.buffs if buff.temp.type == BuffTypes.Benefit
        ]
        selected_buffs = random_select(benefit_buffs, buff_count)
        for selected_buff in selected_buffs:
            _remove_actor_certain_buff(selected_buff.temp.id, actor)
            selected_buff_caster = context.get_hero_by_id(selected_buff.caster_id)
            _add_buffs(
                selected_buff_caster,
                caster,
                selected_buff.temp.id,
                selected_buff.duration,
                context,
            )

    @staticmethod
    def extend_enemy_harm_buffs(
        buff_number: int,
        range_value: int,
        duration: int,
        actor: Hero,
        target: Hero,
        context: Context,
    ):
        targets = context.get_enemies_in_diamond_range(actor, range_value)
        for enemy in targets:
            for buff in enemy.buffs:
                if buff.temp.type == BuffTypes.Harm:
                    buff.duration += duration

    @staticmethod
    def extend_partner_benefit_buffs(
        buff_number: int,
        range_value: int,
        duration: int,
        actor: Hero,
        target: Hero,
        context: Context,
    ):
        partners = context.get_partners_in_diamond_range(actor, range_value)
        for partner in partners:
            for buff in partner.buffs:
                if buff.temp.type == BuffTypes.Benefit:
                    buff.duration += duration

    @staticmethod
    def transfer_self_harm_buff_to_attacker(
        buff_count: int, actor: Hero, target: Hero, context: Context
    ):
        harm_buffs = [buff for buff in actor.buffs if buff.temp.type == BuffTypes.Harm]
        selected_buffs = random_select(harm_buffs, buff_count)
        caster = context.get_hero_by_id(target.caster_id)
        for selected_buff in selected_buffs:
            _remove_actor_certain_buff(selected_buff.temp.id, actor)
            _add_buffs(
                caster, target, selected_buff.temp.id, selected_buff.duration, context
            )

    @staticmethod
    def heal_least_partner_health_by_physical_attack_in_range(
        multiplier: float,
        range_value: int,
        actor: Hero,
        target: Hero,
        context: Context,
        buff: Buff,
    ):
        partners = context.get_partners_in_diamond_range(actor, range_value)
        if not partners:
            return
        min_heal_actor = partners[0]
        for partner in partners:
            if partner.current_life < min_heal_actor.current_life:
                min_heal_actor = partner
        Effects.heal_self_by_caster_physical_attack(
            multiplier, actor, min_heal_actor, context, buff
        )

    @staticmethod
    def heal_self_and_caster_damage(
        multiplier: float, actor: Hero, target: Hero, context: Context, buff: Buff
    ):
        caster = context.get_hero_by_id(buff.caster_id)
        damage = get_current_action(context).total_damage
        calculate_fix_heal(damage * multiplier, actor, caster, context)
        calculate_fix_heal(damage * multiplier, actor, actor, context)

    @staticmethod
    def heal_self_and_transfer_self_harm_buff(
        multiplier: float, actor: Hero, target: Hero, context: Context, buff: Buff
    ):
        caster = context.get_hero_by_id(buff.caster_id)
        harm_buffs = [buff for buff in actor.buffs if buff.temp.type == BuffTypes.Harm]
        for harm_buff in harm_buffs:
            harm_buff_caster = context.get_hero_by_id(harm_buff.caster_id)
            _remove_actor_certain_buff(harm_buff.temp.id, actor)
            _add_buffs(
                caster, harm_buff_caster, harm_buff.temp.id, harm_buff.duration, context
            )
        Effects.heal_self_by_caster_magic_attack(
            multiplier, caster, actor, context, buff
        )

    @staticmethod
    def heal_self_and_remove_harm_buffs(
        multiplier: float, buff_count: int, actor: Hero, target: Hero, context: Context
    ):
        harm_buffs = [buff for buff in actor.buffs if buff.temp.type == BuffTypes.Harm]
        for i in range(buff_count):
            harm_buff = random_select(harm_buffs, 1)
            _remove_actor_certain_buff(harm_buff.temp.id, actor)
            harm_buffs.remove(harm_buff)
        Effects.heal_self(multiplier, actor, actor, context)

    @staticmethod
    def receive_fixed_damage_with_maxlife_and_losslife(
        multiplier: float,
        multiplier2: float,
        actor: Hero,
        target: Hero,
        context: Context,
        buff: Buff,
    ):
        actor_max_life = get_max_life(actor, target, context)
        damage = (
            actor_max_life * multiplier
            + (actor_max_life - actor.current_life) * multiplier2
        )
        caster = context.get_hero_by_id(buff.caster_id)
        calculate_fix_damage(damage, caster, actor, context)

    @staticmethod
    def take_effect_of_qingliu(actor: Hero, target: Hero, context: Context, buff: Buff):
        Effects.heal_self_by_caster_magic_attack(0.4, actor, target, context, buff)
        partners = context.get_partners_in_diamond_range(actor, 2)
        if not partners:
            return
        min_life_percentage = 1
        min_life_percentage_partner = partners[0]
        for partner in partners:
            if partner.current_life / partner.max_life < min_life_percentage:
                min_life_percentage = partner.current_life / partner.max_life
                min_life_percentage_partner = partner
        harm_buffs = [
            buff
            for buff in min_life_percentage_partner.buffs
            if buff.temp.type == BuffTypes.Harm
        ]
        selected_harm_buffs = random_select(harm_buffs, 1)
        _remove_actor_certain_buff(
            selected_harm_buffs[0].temp.id, min_life_percentage_partner
        )

    @staticmethod
    def heal_self_by_damage(
        multiplier: float, actor: Hero, target: Hero, context: Context
    ):
        damage = get_current_action(context).total_damage
        calculate_fix_heal(damage * multiplier, actor, actor, context)

    @staticmethod
    def refresh_buff_trigger(actor: Hero, target: Hero, context: Context, buff: Buff):
        Buff.trigger = 0

    # energy
    @staticmethod
    def increase_self_energy(
        energy_value: int, actor: Hero, target: Hero, context: Context
    ):
        _increase_actor_energy(actor, energy_value)

    @staticmethod
    def increase_target_energy(
        energy_value: int, actor: Hero, target: Hero, context: Context
    ):
        _increase_actor_energy(target, energy_value)

    @staticmethod
    def reduce_target_energy(
        energy_value: int, actor: Hero, target: Hero, context: Context
    ):
        _reduce_actor_energy(target, energy_value)

    @staticmethod
    def reduce_target_energy_in_range(
        range_value: int, energy_value: int, actor: Hero, target: Hero, context: Context
    ):
        enemies = context.get_enemies_in_diamond_range(actor, range_value)
        for enemy in enemies:
            _reduce_actor_energy(enemy, energy_value)

    # shield
    @staticmethod
    def add_shield():
        pass

    @staticmethod
    def take_effect_of_quxing(
        actor: Hero,
        target: Hero,
        context: Context,
        buff: Buff,
    ):
        if not target.is_alive:
            return
        caster = context.get_hero_by_id(buff.caster_id)
        Effects.add_fixed_damage_in_diamond_range_by_caster_magic_attack(
            0.5, 2, actor, target, context, buff
        )
        _remove_actor_certain_buff("quxing", actor)

    @staticmethod
    def take_effect_of_zhuijia(
        actor: Hero,
        target: Hero,
        context: Context,
        buff: Buff,
    ):
        max_trigger = get_buff_max_trigger_limit("zhuijia")
        if buff.trigger >= max_trigger:
            return
        buff.trigger += 1
        Effects.heal_self(0.25, actor, actor, context)
        Effects.remove_actor_harm_buffs(1, actor, actor, context)

    # 以3格范围内物攻/法攻最高的敌人为中心，对其2格范围内所有敌方造成1次「固定伤害」伤害（最大气血的12%），并施加1层「燃烧」状态，持续2回合。
    @staticmethod
    def take_effect_of_tandi(
        actor: Hero,
        target: Hero,
        context: Context,
        buff: Buff,
    ):
        max_trigger_limit = get_buff_max_trigger_limit("tandi")
        if buff.trigger >= max_trigger_limit:
            return
        buff.trigger += 1
        caster = context.get_hero_by_id(buff.caster_id)
        _add_buffs(actor, caster, ["yudi"], 1, context)

    @staticmethod
    def take_effect_of_xueqi(
        actor: Hero,
        target: Hero,
        context: Context,
        buff: Buff,
    ):
        if not target.is_alive:
            return
        damage = get_current_action(context).total_damage
        calculate_fix_damage(damage, target, actor, context)

    @staticmethod
    def take_effect_of_exin(
        actor: Hero,
        target: Hero,
        context: Context,
        buff: Buff,
    ):
        caster = context.get_hero_by_id(buff.caster_id)
        benfit_buffs = [
            buff for buff in actor.buffs if buff.temp.type == BuffTypes.Benefit
        ]
        if len(benfit_buffs) <= 2:
            return
        transfer_buffs_count = min(6, len(benfit_buffs) - 2)
        transfer_buffs = random_select(benfit_buffs, transfer_buffs_count)
        for transfer_buff in transfer_buffs:
            _remove_actor_certain_buff(transfer_buff.temp.id, actor)
            _add_buffs(
                caster, actor, transfer_buff.temp.id, transfer_buff.duration, context
            )
        _add_buffs(actor, caster, ["xinnian"], 2, context)

    @staticmethod
    def take_effect_of_chaozai(
        actor: Hero,
        target: Hero,
        context: Context,
        buff: Buff,
    ):
        damage = get_current_action(context).total_damage
        if damage <= 0:
            return
        if random() < 0.5:
            _add_buffs(actor, actor, ["jinbi"], 1, context)

    @staticmethod
    def take_effect_of_jianyi_jidang(
        actor: Hero,
        target: Hero,
        context: Context,
        buff: Buff,
    ):
        actor_luck = actor.initial_attribute.luck
        target_luck = target.initial_attribute.luck
        damage = get_attack(actor, target, context, False) + get_attack(
            actor, target, context, True
        )
        if actor_luck > target_luck:
            calculate_fix_damage(damage, actor, target, context)
        else:
            calculate_fix_damage(damage * 0.75, actor, target, context)

    @staticmethod
    def take_effect_of_longyan(actor: Hero, target: Hero, context: Context, buff: Buff):
        action = context.get_last_action()
        caster = context.get_hero_by_id(buff.caster_id)
        Effects.increase_target_energy(action.targets, actor, caster, context)

    @staticmethod
    def take_effect_of_ruizou(actor: Hero, target: Hero, context: Context, buff: Buff):
        action = context.get_last_action()
        caster = context.get_hero_by_id(buff.caster_id)
        Effects.increase_self_energy(1, actor, actor, context)
        Effects.increase_target_energy(1, actor, caster, context)

    @staticmethod
    def take_effect_of_feiyu(
        actor_instance: Hero, target_instance: Hero, context: Context
    ):
        context.get_last_action().update_additional_move(2)

    @staticmethod
    def take_effect_of_youkai(
        actor_instance: Hero, target_instance: Hero, context: Context
    ):
        pass

    @staticmethod
    def take_effect_of_chuliang(
        actor_instance: Hero, target_instance: Hero, context: Context, buff: Buff
    ):
        calculate_fix_damage(
            buff.content * 0.5, actor_instance, actor_instance, context
        )

    @staticmethod
    def take_effect_of_xunlie(
        actor_instance: Hero, target_instance: Hero, context: Context, buff: Buff
    ):
        max_trigger_limit = get_buff_max_trigger_limit("xunlie")
        if buff.trigger >= max_trigger_limit:
            return
        caster = context.get_hero_by_id(buff.caster_id)
        if caster.alive and target_instance.alive:
            damage = get_attack(caster, target_instance, context, False, True)
            calculate_fix_damage(damage * 0.5, caster, target_instance, context)

    @staticmethod
    def take_effect_of_songqingming(
        actor_instance: Hero, target_instance: Hero, context: Context, buff: Buff
    ):
        if actor_instance.id == "niexiaoqian":
            _add_buffs(actor_instance, actor_instance, ["jiyi", "shenhu"], 1, context)
            Effects.reduce_self_all_skill_cooldown(
                1, actor_instance, actor_instance, context
            )
        max_trigger_limit = get_buff_max_trigger_limit("songqingming")
        if buff.trigger >= max_trigger_limit:
            return
        caster = context.get_hero_by_id(buff.caster_id)
        _add_buffs(actor_instance, caster, ["mingyun"], 1, context)

    @staticmethod
    def transfer_certain_buff_to_random_partner(
        buff_id: str,
        range_value: int,
        actor: Hero,
        target: Hero,
        context: Context,
        buff: Buff,
    ):
        max_trigger_limit = get_buff_max_trigger_limit(buff_id)
        if buff.trigger >= max_trigger_limit:
            return
        partners = context.get_partners_in_diamond_range(actor, range_value)
        partner = random_select(partners, 1)
        _remove_actor_certain_buff(buff_id, actor)
        _add_buffs(actor, partner, [context.get_buff_temp_by_id(buff_id)], 2, context)

    @staticmethod
    def transfer_buff_to_other_buff(
        buff_id: str, target_buff_id: str, actor: Hero, target: Hero, context: Context
    ):
        _remove_actor_certain_buff(buff_id, actor)
        _add_buffs(
            actor, target, [context.get_buff_temp_by_id(target_buff_id)], 2, context
        )

    @staticmethod
    def take_effect_of_kongxing(
        actor_instance: Hero, target_instance: Hero, context: Context, buff: Buff
    ):
        caster = context.get_hero_by_id(buff.caster_id)
        action = context.get_last_action()
        hero_count = len(action.targets)
        caster_physical_attack = get_attack(caster, actor_instance, context, True, True)
        calculate_fix_damage(
            min(hero_count, 5) * 0.1 * caster_physical_attack,
            caster,
            actor_instance,
            context,
        )
        _add_buffs(caster, caster, ["baonu"], 1, context)
