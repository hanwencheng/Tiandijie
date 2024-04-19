from __future__ import annotations

from typing import TYPE_CHECKING

from calculation.damage_calculator import (
    calculate_fix_damage,
)
from calculation.OtherlCalculation import (
    calculate_fix_heal,
)
from helpers import random_select

if TYPE_CHECKING:
    from primitives.hero import Hero
    from primitives import Context
    from primitives.talent.Talent import Talent
    from calculation.Effects import Effects

from collections import Counter
from calculation.attribute_calculator import get_defense, get_attack, get_max_life


# Talents


class TalentEffects:
    @staticmethod
    def add_fixed_damage_by_talent_owner_magic_attack(
        multiplier: float,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        talent: Talent,
    ):
        talent_owner = talent.hero_id
        damage = get_attack(talent_owner, actor_instance, context, True) * multiplier
        calculate_fix_damage(damage, talent_owner, actor_instance, context)

    @staticmethod
    def add_fixed_damage_by_talent_owner_physical_and_magic_attack(
        multiplier: float,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        talent: Talent,
    ):
        talent_owner = talent.hero_id
        damage = get_attack(talent_owner, actor_instance, context, True) * multiplier
        calculate_fix_damage(damage, talent_owner, actor_instance, context)

    @staticmethod
    def init_talent_field_buff(
        field_buff_value: str,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        talent: Talent,
    ):
        field_buff_temp = context.get_field_buff_by_id(field_buff_value)
        Effects.add_self_field_buff(actor_instance, field_buff_temp, 15, context)

    @staticmethod
    def reset_random_damage_skill_cooldown(
        actor: Hero, target: Hero, context: Context, talent: Talent
    ):
        skill_list = [
            skill
            for skill in actor.enabled_skills
            if skill.is_damage_skill and skill.cool_down > 0
        ]
        if not skill_list:
            return
        skill = random_select(skill_list, 1)
        skill.cool_down = 0

    @staticmethod
    def refresh_Talent_trigger(
        actor: Hero, target: Hero, context: Context, talent: Talent
    ):
        talent.trigger = 0

    @staticmethod
    def take_effect_of_lv(
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        talent: Talent,
    ):
        targets = context.get_enemies_in_square_range(actor_instance, 7)
        selected_harm_buff_temps = random_select(context.harm_buffs, 1)
        additional_buff_temp = context.get_buff_by_id("youjin")
        if additional_buff_temp is not None:
            selected_harm_buff_temps.append(context.get_buff_by_id("youjin"))
        selected_heroes = random_select(targets, 2)
        for enemy_hero in selected_heroes:
            Effects.add_buffs(selected_harm_buff_temps, 2,actor_instance, enemy_hero, context)

    @staticmethod
    def take_effect_zhifatianjiang(
        actor_instance: Hero,
        target_instance: Hero,
        partner: Hero,
        context: Context,
        talent: Talent,
    ):
        if talent.trigger > 2:
            return
        talent.trigger += 1
        TalentEffects.add_fixed_damage_by_talent_owner_magic_attack(
            0.3, actor_instance, target_instance, context, talent
        )
        Effects.add_buffs(["zhanyin"], 1, actor_instance, target_instance, context)

    @staticmethod
    def take_effect_of_wenchangxingyun(
        actor_instance: Hero, target_instance: Hero, context: Context, talent: Talent
    ):
        action = context.get_last_action()
        Effects.reduce_actor_certain_buff_stack(
            "changming", 2, actor_instance, target_instance, context
        )
        talent.cooldown = 3

    @staticmethod
    def take_effect_of_youhuangminhua(
        stage: int,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        talent: Talent,
    ):
        if stage == 1:
            Effects.add_self_buffs(
                ["youshuang"], 3, actor_instance, actor_instance, context
            )
            talent.cooldown = 4
        else:
            if talent.trigger >= 1:
                return
            talent.trigger += 1
            actor_instance.current_life = (
                get_max_life(actor_instance, actor_instance, context) * 0.5
            )
            if actor_instance.buff["youshuang"]:
                enemies = context.get_enemies_in_diamond_range(actor_instance, 3)
                for enemy in enemies:
                    calculate_fix_damage(
                        (
                            get_attack(actor_instance, target_instance, context, False)
                            + get_defense(
                                actor_instance, target_instance, False, context
                            )
                        )
                        * 0.5,
                        actor_instance,
                        enemy,
                        context,
                    )
                    Effects.add_buffs(["wucuichihuan"], 2, actor_instance, enemy, context)

    @staticmethod
    def take_effect_of_yaocaolinghua(
        state: int,
        actor_hero: Hero,
        target_hero: Hero,
        context: Context,
        talent: Talent,
    ):
        if state == 1:
            talent.cooldown = 2
            action = context.get_last_action()
        else:
            partners = context.get_all_partners(actor_hero)
            for partner in partners:
                for buff in partner.buffs:
                    if buff.temp.id == "shengxi":
                        Effects.remove_actor_harm_buffs(
                            1, partner, target_hero, context
                        )
                        calculate_fix_heal(
                            get_attack(actor_hero, target_hero, context, True) * 0.3,
                            actor_hero,
                            partner,
                            context,
                        )
                    if buff.temp.id == "mingsha":
                        skill_list = []
                        for skill in partner.enabled_skills:
                            if skill.cool_down > 0:
                                skill_list.append(skill)
                        if len(skill_list) > 0:
                            random_select(skill_list, 1).cool_down -= 1

    # 行动结束前，可额外使用绝学「光·自在」/「雷·自在」（间隔2回合触发，使用后将切换所有专属绝学并刷新冷却时间且保留当前气力）
    @staticmethod
    def take_effect_of_ruhaishuangsheng(
        state: int,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        talent: Talent,
    ):
        ruhaishuangsheng_skill_dic = {
            "chaodufanyin": "fanyinchaodu",
            "lizanwangsheng": "wangshenglizan",
            "pusaxing": "luochadao",
            "tiangujialan": "miaotanjialan",
        }
        if state == 1:  # 光
            for i in range(len(actor_instance.enabled_skills)):
                if (
                    actor_instance.enabled_skills[i].temp.skill_temp_id
                    in ruhaishuangsheng_skill_dic
                ):
                    new_skill = context.get_skill_by_id(
                        ruhaishuangsheng_skill_dic[
                            actor_instance.enabled_skills[i].temp.skill_temp_id
                        ]
                    )
                    actor_instance.enabled_skills[i] = new_skill
        elif state == 2:
            for i in range(len(actor_instance.enabled_skills)):
                for (
                    thunder_skill_name,
                    light_skill_name,
                ) in ruhaishuangsheng_skill_dic.items():
                    if (
                        actor_instance.enabled_skills[i].temp.skill_temp_id
                        == light_skill_name
                    ):
                        new_skill = context.get_skill_by_id(thunder_skill_name)
                        actor_instance.enabled_skills[i] = new_skill

    # 使用绝学后使气血全满的友方目标「有益状态」等级提升1级。3格内友方「对战后」若气血小于等于50%，恢复该角色气血（恢复量为施术者法攻的0.5倍）（每回合发动2次）。
    @staticmethod
    def take_effect_of_youmingcixin(
        actor_instance: Hero, target_instance: Hero, context: Context, talent: Talent
    ):
        if talent.trigger >= 2:
            return
        talent.trigger += 1
        Effects.add_buffs(["youming"], 2, actor_instance, target_instance, context)

    @staticmethod
    def take_effect_of_shangshandaoxin(
        actor_instance: Hero, target_instance: Hero, context: Context, talent: Talent
    ):
        talent.cooldown = 2
        # Effects.add_extra_skill("")
        pass

    @staticmethod
    def take_effect_of_nuxiongzhiwei(
        actor_instance: Hero, target_instance: Hero, context: Context, talent: Talent
    ):
        enemies = context.get_enemies_in_diamond_range(actor_instance, 3)
        selected_harm_buff_temps = random_select(context.harm_buffs, 1)
        for enemy_hero in enemies:
            Effects.add_buffs(
                selected_harm_buff_temps, 1, actor_instance, enemy_hero, context
            )
        Effects.add_self_buffs(["ankai"], 1, actor_instance, actor_instance, context)

    @staticmethod
    def take_effect_of_zhanfengwangxiang(
        actor_instance: Hero, target_instance: Hero, context: Context, talent: Talent
    ):
        action = context.get_last_action()
        move_range = actor_instance.move_range - action.moves
        if move_range >= 1:
            Effects.add_certain_buff_with_level(
                actor_instance,
                actor_instance,
                "shenxing",
                1,
                min(move_range, 3),
                context,
            )

    @staticmethod
    def take_effects_of_hongyanmeigu(
        state: int,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        talent: Talent,
    ):
        if state == 1:
            action = context.get_last_action()
            count = len(action.targets)
            if count > 0:
                Effects.add_self_buffs(
                    ["yingwei"], 15, actor_instance, actor_instance, context
                )
                if count > 1:
                    for i in range(count - 1):
                        Effects.increase_actor_certain_buff_stack(
                            "yingwei", actor_instance, actor_instance, context
                        )
        elif state == 2:
            buff = actor_instance.get_buff_by_id("yingwei")
            enemies = context.get_enemies_in_diamond_range(actor_instance, 2)
            mark = []
            for i in range(buff.stack):
                enemy = random_select(enemies, 1)
                mark.append(enemies.index(enemy))
                Effects.add_fixed_damage_by_caster_magic_attack(
                    0.1, actor_instance, enemy, context, buff
                )
                Effects.remove_target_benefit_buffs(1, actor_instance, enemy, context)

            counts = Counter(mark)
            duplicates = [element for element, count in counts.items() if count >= 2]
            for index in duplicates:
                Effects.add_buffs(
                    ["meihuo"], 1, actor_instance, enemies[index], context
                )
