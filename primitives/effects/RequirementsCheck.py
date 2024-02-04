from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from primitives.Context import Context
    from primitives.hero.Hero import Hero
    from primitives.hero.Element import Elements
from typing import List
from calculation.Range import calculate_if_targe_in_diamond_range
from primitives.buff.BuffTemp import BuffTypes
from primitives.hero.Element import get_elemental_multiplier



def check_buff_on_target(actor_hero: Hero, target_hero: Hero, buff_type: BuffTypes, is_self: bool) -> int:
    check_hero = actor_hero if is_self else target_hero
    for buff in check_hero.buffs:
        if buff.temp.type == buff_type:
            return 1
    return 0


def _is_attacker(actor_hero: Hero, context: Context) -> int:
    if actor_hero.id == context.get_last_action().actor.id:
        return 1
    else:
        return 0


def check_buff_in_range(range_value: int, actor_hero: Hero, context: Context, buff_type: BuffTypes,
                        is_partner: bool) -> int:
    actor_position = actor_hero.position
    for hero in context.heroes:
        if hero.id == actor_hero.id:
            continue
        if hero.player_id == actor_hero.player_id if is_partner else hero.player_id != actor_hero.player_id:
            for buff in hero.buffs:
                if buff.temp.type == buff_type:
                    if calculate_if_targe_in_diamond_range(actor_position, hero.position, range_value):
                        return 1
    return 0


class RequirementCheck:
    # TODO  should not include any function related to level2 modifier
    @staticmethod
    def buff_stack_reach(reach_number: int, buff_id: str, actor_hero: Hero, target_hero: Hero, context: Context) -> int:
        for buff in target_hero.buffs:
            if buff.temp.id == buff_id:
                if buff.stack >= reach_number:
                    return 1
        return 0

    @staticmethod
    def all_skills_in_cooldown(actor_hero: Hero, target_hero: Hero, context: Context) -> int:
        for skill in actor_hero.enabled_skills:
            if skill.current_cooldown > 0:
                return 0
        return 1

    @staticmethod
    def self_life_is_higher_and_no_harm_buff(percentage: float, actor_hero: Hero, target_hero: Hero,
                                             context: Context) -> int:
        if actor_hero.current_life / actor_hero.max_life > percentage / 100:
            for buff in actor_hero.buffs:
                if buff.temp.type == BuffTypes.Harm:
                    return 0
            return 1
        return 0

    @staticmethod
    def in_the_same_line(actor_hero: Hero, target_hero: Hero, context: Context) -> int:
        actor_position = actor_hero.position
        target_position = target_hero.position
        if actor_position[0] == target_position[0] or actor_position[1] == target_position[1]:
            return 1
        else:
            return 0

    @staticmethod
    def in_battle_with_non_flyable(actor_hero: Hero, target_hero: Hero, context: Context) -> int:
        action = context.get_last_action()
        if action.is_in_battle:
            if target_hero.temp.flyable:
                return 0
            else:
                return 1
        return 0

    @staticmethod
    def target_life_is_below(percentage: float, actor_hero: Hero, target_hero: Hero, context: Context) -> int:
        return 1 if target_hero.current_life / target_hero.max_life < percentage / 100 else 0

    @staticmethod
    def target_life_is_higher(percentage: float, _actor_hero: Hero, target_hero: Hero, context: Context) -> int:
        return 1 if target_hero.current_life / target_hero.max_life > percentage / 100 else 0

    @staticmethod
    def self_life_is_higher(percentage: float, actor_hero: Hero, target_hero: Hero, context: Context) -> int:
        return 1 if actor_hero.current_life / actor_hero.max_life > percentage / 100 else 0

    @staticmethod
    def no_benefit_buff(actor_hero: Hero, target_hero: Hero, context: Context) -> int:
        for buff in target_hero.buffs:
            if buff.temp.type == BuffTypes.Benefit:
                return 0
        return 1

    @staticmethod
    def element_hero_in_range(elements: List[Elements], range_value: int, actor_hero: Hero, target_hero: Hero,
                              context: Context) -> int:
        actor_position = actor_hero.position
        count = 0
        for element in elements:
            for hero in context.heroes:
                if hero.id == actor_hero.id:
                    continue
                if hero.player_id == actor_hero.player_id:
                    if hero.temp.element == element:
                        if calculate_if_targe_in_diamond_range(actor_position, hero.position, range_value):
                            count += 1
                            break

        return 1 if count == len(elements) else 0

    @staticmethod
    def always_true() -> int:
        return 1

    @staticmethod
    def battle_with_no_element_advantage(actor_hero: Hero, target_hero: Hero, context: Context) -> int:
        action = context.get_last_action()
        if action.is_in_battle:
            actor_element = actor_hero.temp.element
            target_element = target_hero.temp.element
            if get_elemental_multiplier(actor_element, target_element, True) == 1:
                return 1
            else:
                return 0
        return 0

    @staticmethod
    def is_attacker(actor_hero: Hero, target_hero: Hero, context: Context) -> int:
        return _is_attacker(actor_hero, context)

    @staticmethod
    def life_not_full_in_range(range_value: int, actor_hero: Hero, target_hero: Hero, context: Context) -> int:
        actor_position = actor_hero.position
        for hero in context.heroes:
            if calculate_if_targe_in_diamond_range(actor_position, hero.position, range_value):
                if hero.current_life < hero.max_life:
                    return 1
        return 0

    @staticmethod
    def in_range(range_value: int, actor_hero: Hero, target_hero: Hero, context: Context) -> int:
        actor_position = actor_hero.position
        for hero in context.heroes:
            if hero.id == actor_hero.id:
                continue
            if calculate_if_targe_in_diamond_range(actor_position, hero.position, range_value):
                return 1
        return 0

    @staticmethod
    def has_partner_in_range(range_value, actor_hero: Hero, target_hero: Hero, context: Context) -> int:
        actor_position = actor_hero.position
        for hero in context.heroes:
            if hero.id == actor_hero.id:
                continue
            if hero.player_id == actor_hero.player_id:
                if calculate_if_targe_in_diamond_range(actor_position, hero.position, range_value):
                    return 1
        return 0

    @staticmethod
    def in_range_count_with_limit(range_value, maximum_count: int, actor_hero: Hero, target_hero: Hero,
                                  context: Context) -> int:
        actor_position = actor_hero.position
        count = 0
        for hero in context.heroes:
            if hero.id == actor_hero.id:
                continue
            if calculate_if_targe_in_diamond_range(actor_position, hero.position, range_value):
                count += 1
        return min(count, maximum_count)

    @staticmethod
    def enemy_in_range_count_bigger_than(range_value: int, count_requirement: int, actor_hero: Hero, target_hero: Hero,
                                         context: Context) -> int:
        actor_position = actor_hero.position
        enemy_count = 0
        for hero in context.heroes:
            if hero.id == actor_hero.id:
                continue
            if hero.player_id != actor_hero.player_id:
                if calculate_if_targe_in_diamond_range(actor_position, hero.position, range_value):
                    enemy_count += 1
        return 1 if enemy_count >= count_requirement else 0

    def attack_enemy_in_range_count_bigger_than_with_base_2(self, range_value: int, count_requirement: int,
                                                            actor_hero: Hero, target_hero: Hero,
                                                            context: Context) -> int:
        is_attacker = _is_attacker(actor_hero, context)
        if is_attacker:
            return 2 + self.enemy_in_range_count_bigger_than(range_value, count_requirement, actor_hero, target_hero,
                                                             context)
        else:
            return 2

    @staticmethod
    def has_harm_buff_partner_in_range(range_value: int, actor_hero: Hero, target_hero: Hero, context: Context) -> int:
        return check_buff_in_range(range_value, actor_hero, context, BuffTypes.Harm, True)

    @staticmethod
    def has_harm_buff_enemy_in_range(range_value: int, actor_hero: Hero, target_hero: Hero, context: Context) -> int:
        return check_buff_in_range(range_value, actor_hero, context, BuffTypes.Harm, False)

    @staticmethod
    def has_benefit_buff_partner_in_range(range_value: int, actor_hero: Hero, target_hero: Hero,
                                          context: Context) -> int:
        return check_buff_in_range(range_value, actor_hero, context, BuffTypes.Benefit, True)

    @staticmethod
    def has_benefit_buff_enemy_in_range(range_value: int, actor_hero: Hero, target_hero: Hero, context: Context) -> int:
        return check_buff_in_range(range_value, actor_hero, context, BuffTypes.Benefit, False)

    @staticmethod
    def self_has_benefit_buff(actor_hero: Hero, target_hero: Hero, context: Context) -> int:
        return check_buff_on_target(actor_hero, target_hero, BuffTypes.Benefit, True)

    @staticmethod
    def target_has_benefit_buff(actor_hero: Hero, target_hero: Hero, context: Context) -> int:
        return check_buff_on_target(actor_hero, target_hero, BuffTypes.Benefit, False)

    @staticmethod
    def self_has_harm_buff(actor_hero: Hero, target_hero: Hero, context: Context) -> int:
        return check_buff_on_target(actor_hero, target_hero, BuffTypes.Harm, True)

    @staticmethod
    def target_has_harm_buff(actor_hero: Hero, target_hero: Hero, context: Context) -> int:
        return check_buff_on_target(actor_hero, target_hero, BuffTypes.Harm, False)

    @staticmethod
    def life_not_full(actor_hero: Hero, target_hero: Hero, context: Context) -> int:
        return 1 if actor_hero.current_life < actor_hero.max_life else 0

    @staticmethod
    def life_is_full(actor_hero: Hero, target_hero: Hero, context: Context) -> int:
        return 1 if actor_hero.current_life == actor_hero.max_life else 0

    @staticmethod
    def target_harm_buff_count(actor_hero: Hero, target_hero: Hero, context: Context) -> int:
        harm_buff_count = 0
        for buff in target_hero.buffs:
            if buff.temp.type == BuffTypes.Harm:
                harm_buff_count += 1
        return min(3, harm_buff_count)

    @staticmethod
    def self_harm_buff_count_smaller_than(count: int, actor_hero: Hero, target_hero: Hero, context: Context) -> int:
        harm_buff_count = 0
        for buff in actor_hero.buffs:
            if buff.temp.type == BuffTypes.Harm:
                harm_buff_count += 1
        return 1 if harm_buff_count < count else 0

    @staticmethod
    def target_harm_buff_count_bigger_than(count: int, actor_hero: Hero, target_hero: Hero, context: Context) -> int:
        harm_buff_count = 0
        for buff in target_hero.buffs:
            if buff.temp.type == BuffTypes.Harm:
                harm_buff_count += 1
        return 1 if harm_buff_count > count else 0
