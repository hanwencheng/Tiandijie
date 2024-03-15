from __future__ import annotations
from typing import TYPE_CHECKING

from calculation.damage_calculator import (
    calculate_fix_damage,
    calculate_magic_damage,
    calculate_physical_damage,
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
            if new_buff.temp.level > existing_buff.temp.level:
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
    def add_additional_move_and_consume_xiayi(
        actor_instance: Hero, target_instance: Hero, context: Context
    ):
        context.get_last_action().update_additional_move(4)
        _reduce_actor_certain_buff_stack("xiayi", actor_instance, 2)

    @staticmethod
    def heal_self(
        multiplier: float, actor_instance: Hero, target_instance: Hero, context: Context
    ):
        actor_max_life = get_max_life(actor_instance, target_instance, context)
        actor_instance.life += actor_max_life * multiplier
        if actor_instance.life > actor_max_life:
            actor_instance.life = actor_max_life

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
                + get_defense(target_instance, actor_instance, context, is_magic)
            ) * multiplier
            calculate_fix_damage(damage, actor_instance, target_instance, context)

    @staticmethod
    def add_fixed_damage_with_attack(
        multiplier: float,
        is_magic: bool,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
    ):
        if check_is_attacker(actor_instance, context):
            damage = (
                get_attack(actor_instance, target_instance, context, is_magic)
                * multiplier
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
    def receive_fixed_damage_with_life_by_self(
        multiplier: float,
        is_magic: bool,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
    ):
        damage = actor_instance.current_life * multiplier
        calculate_fix_damage(damage, actor_instance, actor_instance, context)

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
                _add_buffs(actor, target, [add_buff], duration)

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
            _add_buffs(actor, partner, selected_harm_buff_temps, duration)

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
            _add_buffs(actor, partner, selected_benefit_buff_temps, duration)

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
    def take_magic_damage_of_buff_caster(
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
        percentage: float, is_attacker: bool, context: Context
    ):
        action = context.get_action_by_side(is_attacker)
        actor = context.get_actor_by_side_in_battle(is_attacker)
        move_count = len(action.moves)
        actor_max_life = get_max_life(actor, is_attacker, context)
        calculate_fix_damage(
            actor_max_life * percentage * move_count, is_attacker, actor, context
        )

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
    def remove_target_harm_buffs(
        count: int, actor: Hero, target: Hero, context: Context
    ):
        harm_buffs = [buff for buff in target.buffs if buff.temp.type == BuffTypes.Harm]
        for harm_buff in harm_buffs[:count]:
            _remove_actor_certain_buff(harm_buff.temp.id, target)

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
        # collect all benefit buffs in target.buffs and remove count number of them
        harm_buffs = [buff for buff in target.buffs if buff.temp.type == BuffTypes.Harm]
        for i in range(buff_level):
            _add_buffs(actor, target, harm_buffs, harm_buffs[i].duration, context)

    @staticmethod
    def take_effect_of_tianjiyin(
        actor: Hero, target: Hero, is_attacker: bool, context: Context
    ):
        damage = get_current_action(context).total_damage
        if damage > 0:  # 为3格范围内其他友方恢复气血（恢复量为施术者法攻的0.5倍）
            Effects.heal_self(
                multiplier=0.5,
                actor_instance=actor,
                target_instance=target,
                context=context,
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
    def reverse_actor_harm_buffs(
        buff_count: int, actor: Hero, target: Hero, context: Context
    ):
        harm_buffs = [buff for buff in target.buffs if buff.temp.type == BuffTypes.Harm]
        if not harm_buffs:
            return
        selected_buffs = random_select(harm_buffs, buff_count)
        new_benefit_buffs = random_select(context.benefit_buffs, buff_count)

        for i in range(buff_count):
            _remove_actor_certain_buff(selected_buffs[i].temp.id, target)
            _add_buffs(
                actor,
                target,
                [new_benefit_buffs[i].temp],
                selected_buffs[i].duration,
                context,
            )

    @staticmethod
    def add_self_random_harm_buff(
        buff_count: int, actor: Hero, target: Hero, context: Context
    ):
        harm_buffs = random_select(context.harm_buffs, buff_count)
        _add_buffs(actor, actor, harm_buffs, 2, context)

    @staticmethod
    def add_caster_random_benefit_buff(
        buff_count: int,
        actor: Hero,
        target: Hero,
        context: Context,
        buff: Buff,
    ):
        benefit_buffs = random_select(context.benefit_buffs, buff_count)
        caster_hero = context.get_hero_by_id(buff.caster_id)
        _add_buffs(actor, caster_hero, benefit_buffs, 2, context)

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
        actor.current_life = 0
        actor.is_alive = False
        actor.buffs = []

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
                partner.current_life += caster_hero.magic_attack * multiplier
                if partner.current_life > partner.max_life:
                    partner.current_life = partner.max_life
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
    def take_effect_of_suhun(
        multiplier: int, actor: Hero, target: Hero, context: Context
    ):
        if not actor.is_taken_suhun:
            Effects.heal_self(multiplier, actor, target, context)
            actor.is_taken_suhun = True

    @staticmethod
    def heal_self_by_magic_attack(
        multiplier: float, actor: Hero, target: Hero, context: Context
    ):
        actor.current_life += actor.magic_attack * multiplier
        if actor.current_life > actor.max_life:
            actor.current_life = actor.max_life

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
    def transfer_self_harm_buff_to_caster(
        buff_count: int, actor: Hero, target: Hero, context: Context
    ):
        harm_buffs = [buff for buff in actor.buffs if buff.temp.type == BuffTypes.Harm]
        selected_buffs = random_select(harm_buffs, buff_count)
        caster = context.get_hero_by_id(target.caster_id)
        for selected_buff in selected_buffs:
            _remove_actor_certain_buff(selected_buff.temp.id, actor)
            _add_buffs(caster, caster, selected_buff.temp.id, selected_buff.duration, context)

    @staticmethod
    def heal_least_partner_health_by_physical_attack_in_range(
        multiplier: float, range_value: int, actor: Hero, target: Hero, context: Context
    ):
        partners = context.get_partners_in_diamond_range(actor, range_value)
        if not partners:
            return
        min_heal_actor = partners[0]
        for partner in partners:
            if partner.life < min_heal_actor.life:
                min_heal_actor = partner
        min_heal_actor.life += actor.attack * multiplier
        actor_max_life = get_max_life(actor, target, context)
        if min_heal_actor.life > actor_max_life:
            min_heal_actor.life = actor_max_life

    @staticmethod
    def heal_self_and_caster_damage(
        multiplier: float, actor: Hero, target: Hero, context: Context, buff: Buff
    ):
        caster = context.get_hero_by_id(buff.caster_id)
        if caster.alive and actor.alive:
            caster_damage = get_current_action(context).total_damage
            if caster_damage > 0:
                caster_damage = caster_damage * multiplier

                actor_max_life = get_max_life(actor, target, context)
                actor.life += caster_damage * multiplier
                if actor.life > actor_max_life:
                    actor.life = actor_max_life
                actor_max_life = get_max_life(actor, target, context)
                actor.life += caster_damage * multiplier
                if actor.life > actor_max_life:
                    actor.life = actor_max_life
