from enum import Enum
from functools import partial

from calculation.Effects import Effects
from primitives.buff.BuffTemp import BuffTemp, BuffTypes
from primitives.effects.Event import EventTypes
from primitives.effects.EventListener import EventListener
from calculation.ModifierAttributes import ModifierAttributes as ma
from primitives.effects.ModifierEffect import ModifierEffect
from primitives.RequirementCheck.RequirementsCheck import RequirementCheck as RS


class BuffTemps(Enum):
    @classmethod
    def get_buff_temp_by_id(cls, buff_id):
        """Return the BuffTemp with the specified ID, or None if not found."""
        for buff_temp in cls:
            if buff_temp.value["id"] == buff_id:
                return buff_temp.value
        return None

    # 无摧·封脉	有害	不可驱散	不可扩散	不可偷取	所有被动「绝学」失效（不可驱散）
    wucui_fengmai = BuffTemp(
        "wucui_fengmai",
        BuffTypes.Harm,
        False,
        False,
        False,
        [ModifierEffect(RS.always_true, {ma.is_passives_disabled: True})],
    )

    # 迟缓I	有害	可驱散	可扩散	不可偷取	移动力-1，无法护卫
    chihuan = BuffTemp(
        "chihuan",
        BuffTypes.Harm,
        True,
        True,
        False,
        [
            [
                ModifierEffect(
                    RS.always_true,
                    {
                        ma.physical_protect_range: 0,
                        ma.magic_protect_range: 0,
                        ma.move_range: -1,
                    },
                )
            ],
            [
                ModifierEffect(
                    RS.always_true,
                    {
                        ma.physical_protect_range: 0,
                        ma.magic_protect_range: 0,
                        ma.move_range: -2,
                    },
                )
            ],
            [
                ModifierEffect(
                    RS.always_true,
                    {
                        ma.physical_protect_range: 0,
                        ma.magic_protect_range: 0,
                        ma.move_range: -3,
                    },
                )
            ],
        ],
    )

    # 封劲	有害	可驱散	可扩散	可偷取	主动绝学射程-1
    fengjing = BuffTemp(
        "fengjing",
        BuffTypes.Harm,
        True,
        True,
        True,
        [ModifierEffect(RS.always_true, {ma.attack_range: -1})],
    )

    # 幽霜	其他	不可驱散	不可扩散	不可偷取	免伤+20%，主动造成伤害后，对目标造成1次「固定伤害」（（物攻+物防）的30%），并施加「迟缓I」状态，持续2回合
    youshuang = BuffTemp(
        "youshuang",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.magic_damage_reduction_percentage: 20,
                    ma.physical_damage_reduction_percentage: 20,
                },
            )
        ],
        [
            EventListener(
                EventTypes.damage_end,
                1,
                RS.always_true,
                partial(
                    Effects.add_fixed_damage_with_attack_and_defense,
                    multiplier=0.3,
                    is_magic=False,
                ),
            ),
            EventListener(
                EventTypes.damage_end,
                2,
                RS.always_true,
                partial(
                    Effects.add_target_harm_buffs, buff_temp=["chihuan"], duration=2
                ),
            ),
        ],
    )

    # 禁闭 其他 不可驱散	不可扩散	不可偷取	无法行动，且在对战中无法进行反击。行动结束时，对周围2格内所有友方施加1个随机「有害状态」（不可驱散，队友行动结束若处于自身1格范围移除）
    jinbi = BuffTemp(
        "jinbi",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.is_action_disabled: True, ma.is_counterattack_disabled: True},
            )
        ],
        [
            EventListener(
                EventTypes.damage_end,
                1,
                RS.always_true,
                partial(
                    Effects.add_partner_harm_buffs, buff_number=2, range=2, duration=2
                ),
            ),
            EventListener(
                EventTypes.partner_action_end,
                1,
                partial(RS.PositionChecks.in_range, 1),
                partial(Effects.remove_target_certain_buff, buff_id="jinbi"),
            ),
        ],
    )

    # 幽禁 其他 不可驱散  不可扩散	不可偷取  若自身1格内无其他友方，行动力-1。与律「对战中」攻击、免伤降低15%
    youjin = BuffTemp(
        "youjin",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                partial(RS.PositionChecks.no_partners_in_range, 1), {ma.move_range: -1}
            ),
            ModifierEffect(
                partial(RS.battle_with_certain_hero, "lv"),
                {ma.battle_damage_reduction_percentage: -15},
            ),
        ],
    )

    # 三昧真火	有害	可驱散	不可扩散	不可偷取	法防-15%，行动结束时，遭受1次法术伤害（施加者法攻的50%）
    sanmei_zhenhuo = BuffTemp(
        "sanmei_zhenhuo",
        BuffTypes.Harm,
        True,
        False,
        False,
        [ModifierEffect(RS.always_true, {ma.magic_defense_percentage: -15})],
        [
            EventListener(
                EventTypes.action_end,
                1,
                RS.always_true,
                partial(Effects.take_magic_damage_of_buff_caster, multiplier=0.5),
            )
        ],
    )

    # 中毒	有害	可驱散	可扩散	可偷取	行动结束时，损失10%气血，若每多移动1格，则额外损失5%气血（最多15%）
    zhongdu = BuffTemp(
        "zhongdu",
        BuffTypes.Harm,
        True,
        True,
        True,
        [],
        [
            EventListener(
                EventTypes.action_end,
                1,
                RS.always_true,
                partial(Effects.take_fixed_damage_by_percentage, percentage=0.1),
            ),
            EventListener(
                EventTypes.action_end,
                1,
                RS.always_true,
                partial(
                    Effects.take_fixed_damage_by_percentage_per_each_move,
                    percentage=0.05,
                ),
            ),
        ],
    )

    # 乱神I	有害	可驱散	可扩散	不可偷取	伤害-10%, 乱神II	有害	可驱散	可扩散	不可偷取	伤害-20%
    luanshen = BuffTemp(
        "luanshen",
        BuffTypes.Harm,
        True,
        True,
        False,
        [
            [
                ModifierEffect(
                    RS.always_true,
                    {
                        ma.physical_damage_percentage: -10,
                        ma.magic_damage_percentage: -10,
                    },
                )
            ],
            [
                ModifierEffect(
                    RS.always_true,
                    {
                        ma.physical_damage_percentage: -0,
                        ma.magic_damage_percentage: -20,
                    },
                )
            ],
        ],
    )

    # 仙灵	其他	不可驱散	不可扩散	不可偷取	移动力+1，气血大于等于80%时，无法被敌方选中（主动攻击「对战后」移除）。
    xianling = BuffTemp(
        "xianling",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(RS.always_true, {ma.move_range: 1}),
            ModifierEffect(
                partial(RS.LifeChecks.self_life_is_higher, 80),
                {ma.is_non_selectable: 1},
            ),
        ],
        [],
    )

    # 仙罪	其他	不可驱散	不可扩散	不可偷取	与「雪芝」「对战中」伤害、免伤-10%（上限3层）。主动绝学都在冷却中时，移动力-1。
    xianzui = BuffTemp(
        "xianzui",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                partial(RS.battle_with_certain_hero, "xuezhi"),
                {
                    ma.battle_damage_reduction_percentage: 10,
                    ma.battle_damage_percentage: 10,
                },
            ),
            ModifierEffect(partial(RS.all_skills_in_cooldown), {ma.move_range: -1}),
        ],
    )

    # 仙躯	其他	不可驱散	不可扩散	不可偷取	法术免伤提高20%，代替2格内友方承受法术攻击（遭受攻击「对战后」消失并回复50%气血）
    xianqu = BuffTemp(
        "xianqu",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.magic_damage_reduction_percentage: 20, ma.magic_protect_range: 2},
            )
        ],
        [
            EventListener(
                EventTypes.battle_end,
                3,
                RS.always_true,
                partial(Effects.remove_actor_certain_buff, "xianqu"),
            )
        ],
    )

    #  余蕴幽香	其他	不可驱散	不可扩散	不可偷取	若自身气血低于100%，则对友方使用绝学后同时为自己恢复气血（恢复量为施术者法攻的1倍）
    yuyunyouxiang = BuffTemp(
        "yuyunyouxiang",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.skill_for_partner_end,
                1,
                partial(RS.LifeChecks.life_not_full),
                partial(Effects.heal_self, multiplier=1),
            )
        ],
    )

    #  侠义	其他	不可驱散	不可扩散	不可偷取	行动结束前，若携带3层「侠义」状态，则获得再移动4格，并消耗2层。（上限3层，无法驱散）
    xiayi = BuffTemp(
        "xiayi",
        BuffTypes.Others,
        False,
        False,
        False,
        3,
        [
            EventListener(
                EventTypes.action_end,
                1,
                partial(RS.BuffChecks.buff_stack_reach, 3, buff_id="xiayi"),
                partial(Effects.add_additional_move_and_consume_xiayi),
            )
        ],
    )

    #  信步	有益	可驱散	可扩散	可偷取	免疫「移动力降低」
    xinbu = BuffTemp("xinbu", BuffTypes.Benefit, True, True, True, [], [])

    # 光铠	有益	可驱散	可扩散	可偷取	遭受范围绝学攻击时，受到伤害降低20%，并为自身驱散1个「有害状态」（遭受范围绝学攻击后消失）
    guangkai = BuffTemp(
        "guangkai",
        BuffTypes.Benefit,
        True,
        True,
        True,
        [
            ModifierEffect(
                RS.always_true, {ma.range_skill_damage_reduction_percentage: 20}
            )
        ],
        [
            EventListener(
                EventTypes.skill_range_damage_start,
                1,
                RS.always_true,
                partial(Effects.remove_target_harm_buffs, 1),
            ),
            EventListener(
                EventTypes.skill_range_damage_end,
                1,
                RS.always_true,
                partial(Effects.remove_target_certain_buff, "guangkai"),
            ),
        ],
    )

    # 冰之力	其他	不可驱散	不可扩散	不可偷取	攻击携带「迟缓」类状态的目标时，战斗中伤害额外提高20%。
    bingzhili = BuffTemp(
        "bingzhili",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                partial(RS.BuffChecks.target_has_certain_buff, "chihuan"),
                {ma.physical_damage_percentage: 20},
            )
        ],
        [],
    )

    # 冰劫	其他	不可驱散	不可扩散	不可偷取	主动移动时，若移动距离小于等于1格，行动结束时，将「冰劫」替换为「晕眩」，持续1回合。
    bingjie = BuffTemp(
        "bingjie",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.move_end,
                1,
                partial(RS.move_less_or_equal_than, 1),
                partial(Effects.replace_buff, "bingjie", "xuanyun"),
            )
        ],
    )

    # 冰清	有益	可驱散	可扩散	可偷取	免疫所有有害效果
    bingqing = BuffTemp("bingqing", BuffTypes.Benefit, True, True, True, [], [])

    # 刺骨I	有益	可驱散	可扩散	可偷取	暴击率+20%
    cigu = BuffTemp(
        "cigu",
        BuffTypes.Benefit,
        True,
        True,
        True,
        [
            [ModifierEffect(RS.always_true, {ma.critical_percentage: 20})],
            [ModifierEffect(RS.always_true, {ma.critical_percentage: 25})],
        ],
        [],
    )

    # 固元I	有益	可驱散	可扩散	可偷取	法术免伤+10%
    guyuan = BuffTemp(
        "guyuan",
        BuffTypes.Benefit,
        True,
        True,
        True,
        [
            [
                ModifierEffect(
                    RS.always_true, {ma.magic_damage_reduction_percentage: 10}
                )
            ],
            [
                ModifierEffect(
                    RS.always_true, {ma.magic_damage_reduction_percentage: 20}
                )
            ],
            [
                ModifierEffect(
                    RS.always_true, {ma.magic_damage_reduction_percentage: 25}
                )
            ],
        ],
        [],
    )

    # 失智I	有害	可驱散	可扩散	可偷取	法术免伤-10%
    shizhi = BuffTemp(
        "shizhi",
        BuffTypes.Harm,
        True,
        True,
        True,
        [
            [
                ModifierEffect(
                    RS.always_true, {ma.magic_damage_reduction_percentage: -10}
                )
            ],
            [
                ModifierEffect(
                    RS.always_true, {ma.magic_damage_reduction_percentage: -20}
                )
            ],
            [
                ModifierEffect(
                    RS.always_true, {ma.magic_damage_reduction_percentage: -25}
                )
            ],
        ],
        [],
    )

    # 御魔I	有益	可驱散	可扩散	可偷取	法防+30%
    yumou = BuffTemp(
        "yumou",
        BuffTypes.Benefit,
        True,
        True,
        True,
        [
            [ModifierEffect(RS.always_true, {ma.magic_defense_percentage: 30})],
            [ModifierEffect(RS.always_true, {ma.magic_defense_percentage: 35})],
        ],
        [],
    )

    # 披甲I	有益	可驱散	可扩散	可偷取	物防+20%
    pijia = BuffTemp(
        "pijia",
        BuffTypes.Benefit,
        True,
        True,
        True,
        [
            [
                ModifierEffect(
                    RS.always_true, {ma.physical_damage_reduction_percentage: 20}
                )
            ],
            [
                ModifierEffect(
                    RS.always_true, {ma.physical_damage_reduction_percentage: 25}
                )
            ],
        ],
        [],
    )

    # 断刺I	有害	可驱散	可扩散	不可偷取	暴击率-20%
    duanci = BuffTemp(
        "duanci",
        BuffTypes.Harm,
        True,
        True,
        False,
        [
            [ModifierEffect(RS.always_true, {ma.critical_percentage: -20})],
            [ModifierEffect(RS.always_true, {ma.critical_percentage: -25})],
        ],
        [],
    )

    # 极意I	有益	可驱散	可扩散	可偷取	伤害+10%
    jiyi = BuffTemp(
        "jiyi",
        BuffTypes.Benefit,
        True,
        True,
        True,
        [
            [ModifierEffect(RS.always_true, {ma.physical_damage_percentage: 10})],
            [ModifierEffect(RS.always_true, {ma.physical_damage_percentage: 20})],
            [ModifierEffect(RS.always_true, {ma.physical_damage_percentage: 25})],
        ],
        [],
    )

    # 疲弱I	有害	可驱散	可扩散	不可偷取	物攻，法攻-20%
    piruo = BuffTemp(
        "piruo",
        BuffTypes.Harm,
        True,
        True,
        False,
        [
            [
                ModifierEffect(
                    RS.always_true,
                    {ma.attack_percentage: -20, ma.magic_attack_percentage: -20},
                )
            ],
            [
                ModifierEffect(
                    RS.always_true,
                    {ma.attack_percentage: -25, ma.magic_attack_percentage: -25},
                )
            ],
        ],
        [],
    )

    # 神护I	有益	可驱散	可扩散	可偷取	物理免伤+10%
    shenhu = BuffTemp(
        "shenhu",
        BuffTypes.Benefit,
        True,
        True,
        True,
        [
            [
                ModifierEffect(
                    RS.always_true, {ma.physical_damage_reduction_percentage: 10}
                )
            ],
            [
                ModifierEffect(
                    RS.always_true, {ma.physical_damage_reduction_percentage: 20}
                )
            ],
            [
                ModifierEffect(
                    RS.always_true, {ma.physical_damage_reduction_percentage: 25}
                )
            ],
        ],
        [],
    )

    # 神睿I	有益	可驱散	可扩散	可偷取	物攻、法攻+20%
    shenrui = BuffTemp(
        "shenrui",
        BuffTypes.Benefit,
        True,
        True,
        True,
        [
            [
                ModifierEffect(
                    RS.always_true,
                    {ma.attack_percentage: 20, ma.magic_attack_percentage: 20},
                )
            ],
            [
                ModifierEffect(
                    RS.always_true,
                    {ma.attack_percentage: 25, ma.magic_attack_percentage: 25},
                )
            ],
        ],
        [],
    )

    # 神行I	其他	不可驱散	不可扩散	不可偷取	移动力+1，使用伤害绝学造成暴击，该绝学冷却时间-1
    shenxing = BuffTemp(
        "shenxing",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            [ModifierEffect(RS.always_true, {ma.move_range: 1})],
            [ModifierEffect(RS.always_true, {ma.move_range: 2})],
            [ModifierEffect(RS.always_true, {ma.move_range: 3})],
        ],
        [
            EventListener(
                EventTypes.critical_damage_end,
                1,
                RS.always_true,
                partial(Effects.reduce_skill_cooldown, 1),
            )
        ],
    )

    # 芬芳I	有益	可驱散	可扩散	可偷取	治疗效果提高20%
    fenfang = BuffTemp(
        "fenfang",
        BuffTypes.Benefit,
        True,
        True,
        True,
        [
            [ModifierEffect(RS.always_true, {ma.heal_percentage: 20})],
            [ModifierEffect(RS.always_true, {ma.heal_percentage: 30})],
        ],
        [],
    )

    # 虚损I	有害	可驱散	可扩散	不可偷取	物理免伤-10%
    xusun = BuffTemp(
        "xusun",
        BuffTypes.Harm,
        True,
        True,
        False,
        [
            [
                ModifierEffect(
                    RS.always_true, {ma.physical_damage_reduction_percentage: -10}
                )
            ],
            [
                ModifierEffect(
                    RS.always_true, {ma.physical_damage_reduction_percentage: -20}
                )
            ],
            [
                ModifierEffect(
                    RS.always_true, {ma.physical_damage_reduction_percentage: -25}
                )
            ],
        ],
        [],
    )

    # 蚀御I	有害	可驱散	可扩散	不可偷取	物防-20%
    shiyu = BuffTemp(
        "shiyu",
        BuffTypes.Harm,
        True,
        True,
        False,
        [
            [
                ModifierEffect(
                    RS.always_true, {ma.physical_damage_reduction_percentage: -20}
                )
            ],
            [
                ModifierEffect(
                    RS.always_true, {ma.physical_damage_reduction_percentage: -25}
                )
            ],
        ],
        [],
    )

    # 蚀魔I	有害	可驱散	可扩散	不可偷取	法防-30%
    shimo = BuffTemp(
        "shimo",
        BuffTypes.Harm,
        True,
        True,
        False,
        [
            [ModifierEffect(RS.always_true, {ma.magic_defense_percentage: -30})],
            [ModifierEffect(RS.always_true, {ma.magic_defense_percentage: -35})],
        ],
        [],
    )

    # 迅捷I	有益	可驱散	可扩散	可偷取	移动力+1
    xunjie = BuffTemp(
        "xunjie",
        BuffTypes.Benefit,
        True,
        True,
        True,
        [
            [ModifierEffect(RS.always_true, {ma.move_range: 1})],
            [ModifierEffect(RS.always_true, {ma.move_range: 2})],
            [ModifierEffect(RS.always_true, {ma.move_range: 3})],
        ],
        [],
    )

    # 迅目I	有益	可驱散	可扩散	可偷取	会心+30%
    xunmu = BuffTemp(
        "xunmu",
        BuffTypes.Benefit,
        True,
        True,
        True,
        [
            [ModifierEffect(RS.always_true, {ma.luck_percentage: 30})],
            [ModifierEffect(RS.always_true, {ma.luck_percentage: 40})],
        ],
        [],
    )

    #  圣耀	其他	不可驱散	不可扩散	不可偷取	3格内的敌人行动结束时获得「魂创」状态，并恢复施加者30%最大气血。
    shengyao = BuffTemp(
        "shengyao",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.enemy_action_end,
                1,
                partial(RS.PositionChecks.in_range_of_enemy_caster, range_value=3),
                partial(Effects.add_buffs, buff_temp=["hunchuang"]),
            ),
            EventListener(
                EventTypes.enemy_action_end,
                1,
                partial(RS.PositionChecks.in_range_of_enemy_caster, range_value=3),
                partial(Effects.heal_self, multiplier=0.3),
            ),
        ],
    )

    #  圣耀·贰	其他	不可驱散	不可扩散	不可偷取	自身免伤+15%，3格内的敌人行动结束时获得「魂创」状态，驱散施加者1个「有害状态」并恢复施加者30%最大气血。
    shengyao2 = BuffTemp(
        "shengyao2",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.magic_damage_reduction_percentage: 20,
                    ma.physical_damage_reduction_percentage: 20,
                },
            )
        ],
        [
            EventListener(
                EventTypes.enemy_action_end,
                1,
                partial(RS.PositionChecks.in_range_of_enemy_caster, range_value=3),
                partial(Effects.add_buffs, buff_temp=["hunchuang"]),
            ),
            EventListener(
                EventTypes.enemy_action_end,
                1,
                partial(RS.PositionChecks.in_range_of_enemy_caster, range_value=3),
                partial(Effects.heal_self, multiplier=0.3),
            ),
            EventListener(
                EventTypes.enemy_action_end,
                1,
                partial(RS.PositionChecks.in_range_of_enemy_caster, range_value=3),
                partial(Effects.remove_caster_harm_buff, buff_count=1),
            ),
        ],
    )

    #   地火焚狱	其他	不可驱散	不可扩散	不可偷取	若敌人行动结束时，位于施加者3格范围内，驱散2个「有益状态」，并受到1次「固定伤害」（施术者物攻的15%）
    dihuofenyu = BuffTemp(
        "dihuofenyu",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.enemy_action_end,
                1,
                partial(RS.PositionChecks.in_range_of_enemy_caster, range_value=3),
                partial(Effects.remove_actor_benefit_buffs, buff_count=2),
            ),
            EventListener(
                EventTypes.action_end,
                1,
                partial(RS.PositionChecks.in_range_of_enemy_caster, range_value=3),
                partial(
                    Effects.add_fixed_damage_with_attack,
                    multiplier=0.15,
                    is_magic=False,
                ),
            ),
        ],
    )

    # 堕罪	有害	不可驱散	不可扩散	不可偷取	无法获得「有益状态」，遭受施加者攻击时，法术免伤-10%。
    duozui = BuffTemp(
        "duozui",
        BuffTypes.Harm,
        False,
        False,
        False,
        [
            ModifierEffect(
                partial(RS.attacked_by_caster),
                {ma.magic_damage_reduction_percentage: -10},
            )
        ],
        [],
    )

    # 处刑    其他 不可驱散   不可扩散   不可偷取   射程和移动力+1，主动攻击后使目标携带的「有害状态」等级提升1级。
    chuxing = BuffTemp(
        "chuxing",
        BuffTypes.Others,
        False,
        False,
        False,
        [ModifierEffect(RS.always_true, {ma.attack_range: 1, ma.move_range: 1})],
        [
            EventListener(
                EventTypes.damage_end,
                1,
                RS.always_true,
                partial(Effects.increase_target_harm_buff_level, buff_level=1),
            )
        ],
    )

    # 复仇	有益	可驱散	可扩散	可偷取	反击伤害提高30%
    fuchou = BuffTemp(
        "fuchou",
        BuffTypes.Benefit,
        True,
        True,
        True,
        [ModifierEffect(RS.always_true, {ma.counterattack_damage_percentage: 30})],
        [],
    )

    # 天玑印	有益	可驱散	不可扩散	不可偷取	免疫所有「有害状态」，获得来自施加者触发的天赋效果（不可复制，不可偷取）
    # 自身3格范围内每多1个其他友方，法攻提高6%（最多提高18%）。若本回合主动造成伤害，则行动结束时，为3格范围内其他友方恢复气血（恢复量为施术者法攻的0.5倍）；反之为自身3格范围内4个其他友方施加1个随机「有益状态」。
    tianjiyin = BuffTemp(
        "tianjiyin",
        BuffTypes.Benefit,
        True,
        False,
        False,
        [
            ModifierEffect(
                partial(RS.PositionChecks.in_range_partner_count_with_limit, 3, 3),
                {ma.magic_attack_percentage: 6},
            ),
        ],
        [
            EventListener(
                EventTypes.action_end,
                1,
                partial(RS.PositionChecks.in_range, 3),
                partial(Effects.take_effect_of_tianjiyin),
            )
        ],
    )

    # 天魔护铠	其他	不可驱散	不可扩散	不可偷取	免伤提高50%（受到伤害后消失）
    tianmohukai = BuffTemp(
        "tianmohukai",
        BuffTypes.Others,
        False,
        False,
        False,
        [ModifierEffect(RS.always_true, {ma.magic_damage_reduction_percentage: 50})],
        [
            EventListener(
                EventTypes.damage_end,
                1,
                RS.always_true,
                partial(Effects.remove_actor_certain_buff, "tianmohukai"),
            )
        ],
    )

    # 天鼓法华	其他	不可驱散	不可扩散	不可偷取	3格范围内的友方行动结束时，获得「迅捷I」状态，持续1回合。
    tiangufahua = BuffTemp(
        "tiangufahua",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.partner_action_end,
                1,
                partial(RS.PositionChecks.in_range, 3),
                partial(Effects.add_buffs, buff_temp=["xunjie"], duration=1),
            )
        ],
    )

    # 如燕	其他	不可驱散	不可扩散	不可偷取	主动攻击「对战中」暴击率提高20%，移动力+1，可跨越障碍（不可驱散）
    ruyan = BuffTemp(
        "ruyan",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                partial(RS.is_attacker),
                {
                    ma.critical_percentage: 20,
                    ma.move_range: 1,
                    ma.is_ignore_obstacle: True,
                },
            )
        ],
        [],
    )

    # 威慑	其他	不可驱散	不可扩散	不可偷取	自身反击射程+1，3格范围内所有敌人除气血外全属性降低10%，且具有轻功能力的角色翻越障碍能力失效
    weishe = BuffTemp(
        "weishe",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.counterattack_range: 1},
            ),
            ModifierEffect(
                partial(RS.PositionChecks.in_range_of_enemy, "xiongbagaoqi", 3),
                {
                    ma.magic_defense: -10,
                    ma.defense: -10,
                    ma.attack: -10,
                    ma.magic_attack: -10,
                    ma.luck: -10,
                    ma.is_ignore_obstacle: False,
                },
            ),
        ],
    )

    # 定身	有害	不可驱散	不可扩散	不可偷取	无法移动，无法护卫
    dingshen = BuffTemp(
        "dingshen",
        BuffTypes.Harm,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.current_move_range: 0,
                    ma.physical_protect_range: 0,
                    ma.magic_protect_range: 0,
                },
            )
        ],
        [],
    )

    # 冲阵	其他	不可驱散	不可扩散	不可偷取	移动力+1，伤害和免伤提高12%（上限2层）
    chongzhen = BuffTemp(
        "chongzhen",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.move_range: 1,
                    ma.physical_damage_percentage: 12,
                    ma.magic_damage_percentage: 12,
                    ma.physical_damage_reduction_percentage: 12,
                    ma.magic_damage_reduction_percentage: 12,
                },
            )
        ],
        [],
    )

    # 凝冰	有益	不可驱散	不可扩散	不可偷取	伤害提高1%，物理穿透提高1%（上限4层）
    ningbing = BuffTemp(
        "ningbing",
        BuffTypes.Benefit,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.physical_damage_percentage: 1,
                    ma.magic_damage_percentage: 1,
                    ma.physical_penetration_percentage: 1,
                },
            )
        ],
        [],
    )

    # 叹妙摩耶	其他	不可驱散	不可扩散	不可偷取	3格范围内的友方行动结束时，反转1个「有害状态」。
    miaotanmoye = BuffTemp(
        "miaotanmoye",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.partner_action_end,
                1,
                partial(RS.PositionChecks.in_range, 3),
                partial(Effects.reverse_actor_harm_buffs, 1),
            )
        ],
    )

    # 剑意激荡	其他	不可驱散	不可扩散	不可偷取	目标（物攻+法攻）的伤害（无法被减免）
    jianyijidang = BuffTemp(
        "jianyijidang",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.damage_end,
                1,
                RS.always_true,
                partial(
                    Effects.add_fixed_damage_with_physical_and_magic_attack,
                    multiplier=1,
                ),
            )
        ],
    )

    # 剑气	其他	不可驱散	不可扩散	不可偷取	造成伤害提升24%，遭受伤害降低24%
    jianqi = BuffTemp(
        "jianqi",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.physical_damage_percentage: 24,
                    ma.magic_damage_percentage: 24,
                    ma.physical_damage_reduction_percentage: 24,
                    ma.magic_damage_reduction_percentage: 24,
                },
            )
        ],
        [],
    )

    # 剑绝霜狱	其他	不可驱散	不可扩散	不可偷取	周围2格内所有敌人移动力-3，且无法护卫（无法驱散）
    jianjueshuangyu = BuffTemp(
        "jianjueshuangyu",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                partial(RS.PositionChecks.in_range_of_enemy, "yinwuxie", 2),
                {
                    ma.move_range: -3,
                    ma.physical_protect_range: 0,
                    ma.magic_protect_range: 0,
                },
            ),
        ],
        [],
    )

    # 劫烬	其他	不可驱散	不可扩散	不可偷取	全属性提升20%
    jiejin = BuffTemp(
        "jiejin",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.life: 20,
                    ma.attack: 20,
                    ma.defense: 20,
                    ma.magic_attack: 20,
                    ma.magic_defense: 20,
                    ma.luck: 20,
                },
            )
        ],
        [],
    )

    # 化形·反啄I	有益	不可驱散	不可扩散	不可偷取	反击射程+1，与远程作战「对战中」物防、法防提升20%
    huaxing_fanzhuo = BuffTemp(
        "huaxing_fanzhuo",
        BuffTypes.Benefit,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.counterattack_range: 1},
            ),
            ModifierEffect(
                partial(RS.target_is_battle_in_remote),
                {
                    ma.defense_percentage: 20,
                    ma.magic_defense_percentage: 20,
                },
            ),
        ],
        [],
    )

    # 压制	其他	不可驱散	不可扩散	不可偷取	无法进行反击或先攻（不可驱散，遭受攻击「对战后」消失）
    yazhi = BuffTemp(
        "yazhi",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.is_counterattack_disabled: True, ma.is_counterattack_first: False},
            ),
        ],
        [
            EventListener(
                EventTypes.damage_end,
                1,
                RS.always_true,
                partial(Effects.remove_actor_certain_buff, "yazhi"),
            )
        ],
    )

    # 同归	其他	不可驱散	不可扩散	不可偷取	暴击率提高100%，行动结束死亡
    tonggui = BuffTemp(
        "tonggui",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(RS.always_true, {ma.critical_percentage: 100}),
        ],
        [
            EventListener(
                EventTypes.action_end,
                1,
                RS.always_true,
                partial(Effects.kill_self),
            )
        ],
    )

    # 启智	其他	不可驱散	不可扩散	不可偷取	遭受单体伤害绝学攻击时气血越高免伤和暴击抗性越高（最高提升20%）（遭受单体伤害绝学后移除）
    qizhi = BuffTemp(
        "qizhi",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                partial(RS.skill_is_single_target_damage_and_life_is_higher_percentage),
                {ma.battle_damage_reduction_percentage: 20},
            ),
        ],
        [
            EventListener(
                EventTypes.skill_single_damage_end,
                1,
                RS.always_true,
                partial(Effects.remove_actor_certain_buff, "qizhi"),
            )
        ],
    )

    # 命蕴	有益	可驱散	可扩散	可偷取	行动结束时，恢复20%气血
    mingyun = BuffTemp(
        "mingyun",
        BuffTypes.Benefit,
        True,
        True,
        True,
        [],
        [
            EventListener(
                EventTypes.action_end,
                1,
                RS.always_true,
                partial(Effects.heal_self, multiplier=0.2),
            )
        ],
    )

    # 宿魂	其他	不可驱散	不可扩散	不可偷取	携带「执戮」状态时，若受到致命伤害时免除死亡，自身恢复30%气血（每场战斗触发1次）
    suhun = BuffTemp(
        "suhun",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(RS.always_true, {ma.prevent_death: True}),
        ],
        [],
    )

    # 寒岚	其他	不可驱散	不可扩散	不可偷取	使用冰属相绝学攻击时提高10%法穿（使用冰属相绝学后移除）。
    hanlan = BuffTemp(
        "hanlan",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                partial(RS.skill_is_water_element),
                {ma.magic_penetration_percentage: 10},
            ),
        ],
        [
            EventListener(
                EventTypes.damage_end,
                1,
                partial(RS.skill_is_water_element),
                partial(Effects.remove_actor_certain_buff, "hanlan"),
            )
        ],
    )

    # 封劲	有害	可驱散	可扩散	可偷取	主动绝学射程-1
    fengjin = BuffTemp(
        "fengjin",
        BuffTypes.Harm,
        True,
        True,
        True,
        [ModifierEffect(RS.always_true, {ma.active_skill_range: -1})],
        [],
    )

    # 封咒	有害	可驱散	可扩散	不可偷取	无法使用主动「绝学」
    fengzhou = BuffTemp(
        "fengzhou",
        BuffTypes.Harm,
        True,
        True,
        False,
        [ModifierEffect(RS.always_true, {ma.is_active_skill_disabled: True})],
        [],
    )

    # 封缄	有害	可驱散	可扩散	可偷取	范围绝学的范围-1
    fengjian = BuffTemp(
        "fengjian",
        BuffTypes.Harm,
        True,
        True,
        True,
        [ModifierEffect(RS.always_true, {ma.range_skill_range: -1})],
        [],
    )

    # 封脉	有害	可驱散	可扩散	不可偷取	所有被动「绝学」失效
    fengmai = BuffTemp(
        "fengmai",
        BuffTypes.Harm,
        True,
        True,
        False,
        [ModifierEffect(RS.always_true, {ma.is_passives_disabled: True})],
    )

    # 屠戮	其他	不可驱散	不可扩散	不可偷取	无法护卫队友，主动攻击「对战后」造成1次「固定伤害」（物攻的50%）若目标气血低于50%，则本次「固定伤害」翻倍（下一次主动攻击「对战后」触发消耗）
    tulu = BuffTemp(
        "tulu",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.physical_protect_range: 0, ma.magic_protect_range: 0},
            ),
        ],
        [
            EventListener(
                EventTypes.damage_end,
                1,
                RS.always_true,
                partial(Effects.add_fixed_damage_with_attack, multiplier=0.5),
            ),
            EventListener(
                EventTypes.damage_end,
                1,
                partial(RS.LifeChecks.target_life_is_below, 50),
                partial(Effects.add_fixed_damage_with_attack, multiplier=0.5),
            ),
        ],
    )

    # 巨影	其他	不可驱散	不可扩散	不可偷取	主动攻击「对战中」免伤提高15%，且「对战后」恢复自身气血（恢复量为本次伤害的50%）（不可驱散）
    juying = BuffTemp(
        "juying",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                partial(RS.is_attacker),
                {ma.battle_damage_reduction_percentage: 15},
            ),
        ],
        [
            EventListener(
                EventTypes.battle_end,
                1,
                partial(RS.is_attacker),
                partial(Effects.heal_self, multiplier=0.5),
            )
        ],
    )

    # 幽煌邪焰	其他	不可驱散	不可扩散	不可偷取	除气血外所有属性提高10%
    youhuangxieyan = BuffTemp(
        "youhuangxieyan",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.attack: 10,
                    ma.defense: 10,
                    ma.magic_attack: 10,
                    ma.magic_defense: 10,
                    ma.luck: 10,
                },
            )
        ],
        [],
    )

    # 幽阙	有害	不可驱散	不可扩散	不可偷取	无法获得治疗（无法驱散）
    youque = BuffTemp(
        "youque",
        BuffTypes.Harm,
        False,
        False,
        False,
        [ModifierEffect(RS.always_true, {ma.is_non_healable: True})],
        [],
    )

    # 幽魂	其他	不可驱散	不可扩散	不可偷取	移动力+1，行动时无视敌方角色阻挡（不可驱散
    youhun = BuffTemp(
        "youhun",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.move_range: 1, ma.is_ignore_block: True},
            )
        ],
        [],
    )

    # 异心	其他	不可驱散	不可扩散	不可偷取	3格内每有1名其他友方行动结束时携带者受到1次「固定伤害」（当前气血的30%）并获得1个随机「有害状态」（不可驱散）
    yixin = BuffTemp(
        "yixin",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.partner_action_end,
                1,
                partial(RS.PositionChecks.in_range, 3),
                partial(Effects.receive_fixed_damage_with_life_by_self, multiplier=0.3),
            ),
            EventListener(
                EventTypes.partner_action_end,
                1,
                partial(RS.PositionChecks.in_range, 3),
                partial(Effects.add_self_random_harm_buff, 1),
            ),
        ],
    )

    # 归依	其他	不可驱散	不可扩散	不可偷取	行动结束时，使施加者恢复3格内所有施加者友方的气血（恢复量为施加者法攻的0.5倍）并施加1个随机「有益状态」（不可驱散）
    guiyi = BuffTemp(
        "guiyi",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.action_end,
                1,
                partial(RS.PositionChecks.in_range, 3),
                partial(
                    Effects.heal_partner_and_add_benefit_buff_by_caster, multiplier=0.5
                ),
            ),
        ],
    )

    # 影遁	其他	不可驱散	不可扩散	不可偷取	伤害和暴击率提高12%，无法被敌人普通攻击及绝学锁定为目标（遭受1次范围伤害或造成伤害后，或行动结束时，自身2格范围内存在敌人时，该状态消失）
    yingdun = BuffTemp(
        "yingdun",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.physical_damage_percentage: 12,
                    ma.magic_damage_percentage: 12,
                    ma.critical_percentage: 12,
                    ma.is_targetable_by_enemy: False,
                },
            ),
        ],
        [
            EventListener(
                EventTypes.skill_range_damage_end,
                1,
                RS.always_true,
                partial(Effects.remove_actor_certain_buff, "yingdun"),
            ),
            EventListener(
                EventTypes.damage_end,
                1,
                partial(RS.is_attacker),
                partial(Effects.remove_actor_certain_buff, "yingdun"),
            ),
            EventListener(
                EventTypes.action_end,
                1,
                partial(RS.PositionChecks.enemy_in_range_count_bigger_than, 2, 1),
                partial(Effects.remove_actor_certain_buff, "yingdun"),
            ),
        ],
    )

    # 御敌	其他	不可驱散	不可扩散	不可偷取	每层伤害、免伤+15%（上限4层）。
    yudi = BuffTemp(
        "yudi",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.physical_damage_percentage: 15,
                    ma.magic_damage_percentage: 15,
                    ma.physical_damage_reduction_percentage: 15,
                    ma.magic_damage_reduction_percentage: 15,
                },
            ),
        ],
        [],
    )

    # 御火	其他	不可驱散	不可扩散	不可偷取	火属相免伤80%，受到攻击后消失。
    yuhuo = BuffTemp(
        "yuhuo",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                partial(RS.is_attacked_by_fire_element),
                {ma.magic_damage_reduction_percentage: 80},
            ),
        ],
        [
            EventListener(
                EventTypes.damage_end,
                1,
                RS.always_true,
                partial(Effects.remove_actor_certain_buff, "yuhuo"),
            )
        ],
    )

    # 心莲	其他	不可驱散	不可扩散	不可偷取	免伤+30%，状态消失时恢复自身气血（恢复量为施术者法攻的0.7倍）受到伤害后消失。
    xinlian = BuffTemp(
        "xinlian",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.magic_damage_reduction_percentage: 30},
            ),
        ],
        [
            EventListener(
                EventTypes.damage_end,
                1,
                RS.always_true,
                partial(Effects.remove_actor_certain_buff, "xinlian"),
            ),
            EventListener(
                EventTypes.buff_end,
                1,
                RS.always_true,
                partial(Effects.heal_self_by_magic_attack, multiplier=0.7),
            ),
        ],
    )

    # 忘时	有害	不可驱散	不可扩散	不可偷取	行动结束时，自身1个初始冷却时间最长地伤害绝学冷却时间+1（不可驱散）
    wangshi = BuffTemp(
        "wangshi",
        BuffTypes.Harm,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.action_end,
                1,
                RS.always_true,
                partial(Effects.increase_self_loongest_skill_cooldown, 1),
            )
        ],
    )

    # 怒意	其他	不可驱散	不可扩散	不可偷取	除气血外全属性提高10%
    nuyi = BuffTemp(
        "nuyi",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.attack: 10,
                    ma.defense: 10,
                    ma.magic_attack: 10,
                    ma.magic_defense: 10,
                    ma.luck: 10,
                },
            )
        ],
        [],
    )

    # 怒火	有益	不可驱散	不可扩散	不可偷取	物攻提高30%，主动攻击「对战后」自身所有主动绝学冷却时间-1
    nuhuo = BuffTemp(
        "nuhuo",
        BuffTypes.Benefit,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.attack_percentage: 30,
                },
            )
        ],
        [
            EventListener(
                EventTypes.damage_end,
                1,
                RS.always_true,
                partial(Effects.reduce_self_all_skill_cooldown, 1),
            )
        ],
    )

    # 怯懦	其他	不可驱散	不可扩散	不可偷取	除气血外全属性降低20%，遭受鲜于超主动攻击「对战中」受到伤害提升20%，且无法反击
    qienou = BuffTemp(
        "qienou",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.attack: -20,
                    ma.defense: -20,
                    ma.magic_attack: -20,
                    ma.magic_defense: -20,
                    ma.luck: -20,
                },
            ),
            ModifierEffect(
                partial(RS.battle_with_certain_hero, "xianyuchao"),
                {
                    ma.physical_damage_reduction_percentage: -20,
                    ma.magic_damage_reduction_percentage: -20,
                    ma.is_counterattack_disabled: True,
                },
            ),
        ],
        [],
    )

    # 怵惕	其他	不可驱散	不可扩散	不可偷取	每层物理伤害、暴击率-20%，携带者主动攻击后，叠加1层（上限3层，不可驱散）。
    chuti = BuffTemp(
        "chuti",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.physical_damage_percentage: -20,
                    ma.critical_percentage: -20,
                },
            ),
        ],
        [
            EventListener(
                EventTypes.damage_end,
                1,
                RS.always_true,
                partial(Effects.add_buffs, "chuti"),
            )
        ],
    )
    # 恩念	其他	不可驱散	不可扩散	不可偷取	主动攻击「对战后」自身受到1次「固定伤害」（当前气血的50%）（不可驱散）
    ennian = BuffTemp(
        "ennian",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.damage_end,
                1,
                RS.always_true,
                partial(Effects.receive_fixed_damage_with_life_by_self, multiplier=0.5),
            )
        ],
    )

    # 惶乱	有害	不可驱散	不可扩散	不可偷取	遭受攻击受到暴击后，获得1个随机「有害状态」，并对施加者施加1个随机「有益状态」（不可驱散）
    huangluan = BuffTemp(
        "huangluan",
        BuffTypes.Harm,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.critical_damage_end,
                1,
                RS.always_true,
                partial(Effects.add_self_random_harm_buff, 1),
            ),
            EventListener(
                EventTypes.critical_damage_end,
                1,
                RS.always_true,
                partial(Effects.add_caster_random_benefit_buff, 1),
            ),
        ],
    )

    # 愈合	有益	可驱散	可扩散	可偷取	「对战后」恢复15%气血
    yuhe = BuffTemp(
        "yuhe",
        BuffTypes.Benefit,
        True,
        True,
        True,
        [],
        [
            EventListener(
                EventTypes.damage_end,
                1,
                RS.always_true,
                partial(Effects.heal_self, multiplier=0.15),
            )
        ],
    )

    # 愤怒	其他	不可驱散	不可扩散	不可偷取	射程+2，除气血外全属性提升20%
    fennv = BuffTemp(
        "fennv",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.attack: 20,
                    ma.defense: 20,
                    ma.magic_attack: 20,
                    ma.magic_defense: 20,
                    ma.luck: 20,
                    ma.attack_range: 2,
                },
            )
        ],
        [],
    )

    # 执剑	其他	不可驱散	不可扩散	不可偷取	遭受非飞行角色攻击时，「对战前」夺取敌方1个「有益状态」，「对战中」免伤和暴击抗性提高15%
    zhijian = BuffTemp(
        "zhijian",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                partial(RS.is_attacked_by_non_flyer),
                {
                    ma.battle_damage_reduction_percentage: 15,
                    ma.critical_percentage_reduction: 15,
                },
            ),
        ],
        [
            EventListener(
                EventTypes.battle_start,
                1,
                partial(RS.is_attacked_by_non_flyer),
                partial(Effects.steal_target_benefit_buff, 1),
            )
        ],
    )

    # 执念	其他	不可驱散	不可扩散	不可偷取	伤害+4%，暴击率+4%（上限4层）
    zhinian = BuffTemp(
        "zhinian",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.physical_damage_percentage: 4,
                    ma.magic_damage_percentage: 4,
                    ma.critical_percentage: 4,
                },
            ),
        ],
        [],
    )

    # 护佑	其他	不可驱散	不可扩散	不可偷取	双防+20%，遭受暴击后恢复30%气血
    huyou = BuffTemp(
        "huyou",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.defense_percentage: 20, ma.magic_defense_percentage: 20},
            ),
        ],
        [
            EventListener(
                EventTypes.critical_damage_end,
                1,
                RS.always_true,
                partial(Effects.heal_self, multiplier=0.3),
            )
        ],
    )

    # 护卫	其他	不可驱散	不可扩散	不可偷取	代替相邻2格距离的队友承受攻击（不可驱散）
    huwei = BuffTemp(
        "huwei",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.physical_protect_range: 2, ma.magic_protect_range: 2},
            ),
        ],
        [],
    )

    # 护法	其他	不可驱散	不可扩散	不可偷取	法术免伤提高20%，代替2格内友方承受法术攻击（「对战后」消失）
    hufa = BuffTemp(
        "hufa",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.magic_damage_reduction_percentage: 20, ma.magic_protect_range: 2},
            ),
        ],
        [
            EventListener(
                EventTypes.battle_start,
                1,
                partial(RS.PositionChecks.in_range, 2),
                partial(Effects.remove_actor_certain_buff, "hufa"),
            )
        ],
    )

    # 报怒	其他	不可驱散	不可扩散	不可偷取	移除「空性」状态，伤害+20%，克制攻击加成+15%，移动力+1（不可驱散）
    baonu = BuffTemp(
        "baonu",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.physical_damage_percentage: 20,
                    ma.magic_damage_percentage: 20,
                    ma.move_range: 1,
                },
            ),
            ModifierEffect(
                partial(RS.attack_to_advantage_elements),
                {ma.physical_damage_percentage: 15, ma.magic_damage_percentage: 15},
            ),
        ],
        [
            EventListener(
                EventTypes.action_start,
                1,
                partial(RS.PositionChecks.in_range, 2),
                partial(Effects.remove_actor_certain_buff, "kongxing"),
            )
        ],
    )

    # 担因	其他	不可驱散	不可扩散	不可偷取	物理免伤+20%，代替2格内友方承受1次物攻（「对战后」消失）
    danyin = BuffTemp(
        "danyin",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.physical_damage_reduction_percentage: 20,
                    ma.physical_protect_range: 2,
                },
            ),
        ],
        [
            EventListener(
                EventTypes.battle_end,
                1,
                partial(RS.PositionChecks.in_range, 2),
                partial(Effects.remove_actor_certain_buff, "danyin"),
            )
        ],
    )

    # 拉弓	其他	不可驱散	不可扩散	不可偷取	下一次普攻必定发动连击（0.3倍伤害，触发后消失）
    lagong = BuffTemp(
        "lagong",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.is_double_attack: True},
            ),
        ],
        [],
    )

    # 拢烟	其他	不可驱散	不可扩散	不可偷取	主动攻击每命中1个敌人给施加者回复1点气力（最多3点，不可驱散）
    longyan = BuffTemp(
        "longyan",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [],
    )

    # 持旗	其它	不可偷取	不可偷取	不可偷取	相邻1格内开启「限制区域」：敌方移动 力消耗+1。主动攻击前驱散敌方1个「有益状态」，并施加「燃烧」状态，持续2 回合。
    chiqi = BuffTemp(
        "chiqi",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [],
    )

    # 障眼I	有害	可驱散	可扩散	不可偷取	会心-30%
    zhangyan = BuffTemp(
        "zhangyan",
        BuffTypes.Harm,
        True,
        True,
        False,
        [
            [
                ModifierEffect(
                    RS.always_true,
                    {ma.critical_percentage_reduction: 30},
                ),
            ],
            [
                ModifierEffect(
                    RS.always_true,
                    {ma.critical_percentage_reduction: 35},
                ),
            ],
        ],
        [],
    )

    # 雷劫	其他	不可驱散	不可扩散	不可偷取	行动结束时，如果自身菱形2格内有其它友方单位，则将「雷劫」替换为「晕眩」，持续1回合。
    leijie = BuffTemp(
        "leijie",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.action_end,
                1,
                partial(RS.PositionChecks.in_range, 2),
                partial(Effects.remove_actor_certain_buff, "leijie"),
            ),
            EventListener(
                EventTypes.action_end,
                1,
                partial(RS.PositionChecks.in_range, 2),
                partial(Effects.add_buffs, buff_temp=["yunxuan"], duration=1),
            ),
        ],
    )

    # 雷场	其他	不可驱散	不可扩散	不可偷取	遭受暴击概率+20%
    leichang = BuffTemp(
        "leichang",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.suffer_critical_percentage: 20},
            ),
        ],
        [],
    )

    # 挽弓	其他	不可驱散	不可扩散	不可偷取	伤害提高20%，射程+1（不可驱散，主动使用伤害绝学后消耗）
    wangong = BuffTemp(
        "wangong",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.physical_damage_percentage: 20, ma.attack_range: 1},
            ),
        ],
        [
            EventListener(
                EventTypes.skill_single_damage_end,
                1,
                RS.always_true,
                partial(Effects.remove_actor_certain_buff, "wangong"),
            ),
            EventListener(
                EventTypes.skill_range_damage_end,
                1,
                RS.always_true,
                partial(Effects.remove_actor_certain_buff, "wangong"),
            ),
        ],
    )

    # 探敌	其他	不可驱散	不可扩散	不可偷取	移动力+1，主动攻击造成伤害时为施加者增加1层「御敌」状态，持续1回合，且施加者立刻触发1次天赋的「御敌」效果（每回合最多触发1次）
    tandi = BuffTemp(
        "tandi",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.move_range: 1},
            ),
        ],
        [
            EventListener(
                EventTypes.damage_end,
                1,
                RS.always_true,
                partial(Effects.add_buffs, buff_temp=["yudi"], duration=1),
            ),
        ],
    )
