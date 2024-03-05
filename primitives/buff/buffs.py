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
                        ma.physical_protect_range: 1,
                        ma.magic_protect_range: 1,
                        ma.move_range: -1,
                    },
                )
            ],
            [
                ModifierEffect(
                    RS.always_true,
                    {
                        ma.physical_protect_range: 1,
                        ma.magic_protect_range: 1,
                        ma.move_range: -2,
                    },
                )
            ],
            [
                ModifierEffect(
                    RS.always_true,
                    {
                        ma.physical_protect_range: 1,
                        ma.magic_protect_range: 1,
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
    xianzeui = BuffTemp(
        "xianzeui",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
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
    xunji = BuffTemp(
        "xunji",
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
    tianjiyin = BuffTemp(
        "tianjiyin",
        BuffTypes.Benefit,
        True,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.battle_end,
                1,
                RS.always_true,
                partial(Effects.add_actor_benefit_talent),
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
                partial(Effects.add_buffs, buff_temp=["xunji"], duration=1),
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
                RS.is_attacker,
                {
                    ma.critical_percentage: 20,
                    ma.move_range: 1,
                    ma.is_ignore_obstacle: 1,
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
        [ModifierEffect(RS.always_true, {ma.counterattack_range: 1})],
        [
            EventListener(
                EventTypes.battle_start,
                1,
                RS.always_true,
                partial(Effects.reduce_enemy_attributes_except, ["qixue"], 10),
            )
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
                    ma.move_range: 0,
                    ma.physical_protect_range: 1,
                    ma.magic_protect_range: 1,
                },
            )
        ],
        [],
    )
