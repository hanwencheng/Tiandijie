from functools import partial

from primitives.effects.Event import EventTypes
from primitives.effects.EventListener import EventListener
from primitives.effects.ModifierEffect import ModifierEffect
from primitives.fieldbuff.FieldBuffTemp import FieldBuffTemp
from primitives.buff.BuffTemp import BuffTemp, BuffTypes

from calculation.Effects import Effects
from primitives.RequirementCheck.RequirementsCheck import RequirementCheck as RS
from calculation.ModifierAttributes import ModifierAttributes as ma

from typing import List, Any


class FieldBuffs:
    # 慑服	其他	不可驱散	不可扩散	不可偷取	行动结束时若处于施加者3格内，反转自身1个「有益状态」并发生1格内「扰动」效果（不可驱散，触发后移除）。
    shefu = FieldBuffTemp("shefu", "yinqianyang", 3, [], [])

    # 优先攻击
    # 送清明	其他	不可驱散	不可扩散	不可偷取	自身2格范围内，友方主动发起对战，且优先攻击时，则在「对战前」为其施加「命蕴」效果，持续2回合（每回合只能触发2次）[若协攻对象为聂小倩，则「对战前」为其施加「极意II」「神护II」效果，持续1回合，且聂小倩所有主动绝学冷却时间减少1回合]
    songqingming = FieldBuffTemp(
        "songqingming",
        "ningcaichen",
        2,
        [
            [],
        ],
        [
            EventListener(
                EventTypes.battle_start,
                1,
                partial(RS.self_is_first_attack),
                partial(Effects.take_effect_of_songqingming),
            )
        ],
    )

    # 寻猎	其他	不可驱散	不可扩散	不可偷取	若队友主动攻击自身2格范围内的敌人，且优先攻击时，则在「对战中」双方交战后，立刻对敌方造成额外一次0.3倍物攻伤害（每回合只能触发1次）
    xunlie = FieldBuffTemp(
        "xunlie",
        "xiaoshuang",
        2,
        [],
        [
            EventListener(
                EventTypes.battle_end,
                1,
                partial(RS.self_is_first_attack),
                partial(Effects.take_effect_of_xunlie),
            )
        ],
    )

    # 灭破空间	其他	不可驱散	不可扩散	不可偷取	自身2格范围内，友方主动发起对战，且优先攻击时，「对战中」伤害提高10%，若攻击者气血不满额外提升15%。（1回合限定发动2次）
    miepokongjian = FieldBuffTemp(
        "miepokongjian",
        "zhenyi",
        2,
        [
            ModifierEffect(partial(RS.self_is_first_attack), {ma.battle_damage_percentage: 10}),
            ModifierEffect(partial(RS.miepokongjian_requires_check), {ma.battle_damage_percentage: 15}),
        ],
        [
        ],
    )

    # 号令	其他	不可驱散	不可扩散	不可偷取	自身两格范围内，若有友方主动发起对战，且优先攻击时，伤害提高10%，
    haoling = FieldBuffTemp(
        "haoling",
        "yinma",
        2,
        [ModifierEffect(partial(RS.self_is_first_attack), {ma.battle_damage_percentage: 10})],
        [],
    )

    # 焕焱烈阵	其他	不可驱散	不可扩散	不可偷取	自身2格范围内，若有友方主动发起对战，且优先攻击时，使其本次战斗中伤害提高15%，若目标携带「燃烧」状态，伤害额外提高15%（每回合发动3次）
    huanyanliezhen = FieldBuffTemp(
        "huanyanliezhen",
        "yunxiang",
        2,
        [
            ModifierEffect(partial(RS.self_is_first_attack), {ma.battle_damage_percentage: 15}),
            ModifierEffect(partial(RS.huanyanliezhen_requires_check), {ma.battle_damage_percentage: 15}),
        ],
        [],
    )

    # 炎狱空间	其他	不可驱散	不可扩散	不可偷取	自身2格范围内，友方角色主动发起对战，且优先攻击时，「对战中」伤害提高10%，对雷属相敌人额外提升10%。（1回合限定发动2次）
    # 炎狱空间·壹	其他	不可驱散	不可扩散	不可偷取	自身2格范围内，友方角色主动发起对战，且优先攻击时，「对战中」暴击率、伤害提高10%，对雷属相敌人额外提升10%。（1回合限定发动2次）
    # 炎狱空间·贰	其他	不可驱散	不可扩散	不可偷取	自身2格范围内，友方角色主动发起对战，且优先攻击时，「对战中」暴击率、伤害提高10%，对雷属相敌人额外提升15%。（1回合限定发动3次）
    yanyukongjian = FieldBuffTemp(
        "yanyukongjian",
        "xiahouyi",
        2,
        [
            [
                ModifierEffect(partial(RS.self_is_first_attack), {ma.battle_damage_percentage: 10}),
                ModifierEffect(partial(RS.yanyukongjian_requires_check), {ma.battle_damage_percentage: 10}),
            ],
            [
                ModifierEffect(partial(RS.self_is_first_attack), {ma.critical_percentage: 10, ma.battle_damage_percentage: 10}),
                ModifierEffect(partial(RS.yanyukongjian_requires_check), {ma.battle_damage_percentage: 10}),
            ],
            [
                ModifierEffect(partial(RS.self_is_first_attack), {ma.critical_percentage: 10, ma.battle_damage_percentage: 10}),
                ModifierEffect(partial(RS.yanyukongjian_requires_check), {ma.battle_damage_percentage: 15}),
            ],
        ],
        [],
    )

    # 护象	其他	不可驱散	不可扩散	不可偷取	范围内所有友方遭受「固定伤害」减免50% ，且施术者自身免伤额外提高10%（无法驱散）
    huxiang = FieldBuffTemp(
        "huxiang",
        "chunlan",
        2,
        [
            ModifierEffect(RS.always_true, {ma.fixed_damage_reduction_percentage: 10}),
        ],
        [],
    )
    # 空性	其他	不可驱散	不可扩散	不可偷取	物攻的15%附加至物防、法防上，自身3格范围内友方受到攻击后，对攻击者造成1次物理伤害（受击人数（上限5人）*（物攻的0.4倍）），并进入「报怒」状态，持续2回合（不可驱散）
    kongxing = FieldBuffTemp(
        "kongxing",
        "wuxiangerfu",
        3,
        [],
        [
            EventListener(
                EventTypes.under_damage_end,
                1,
                partial(RS.is_attack_target),
                partial(Effects.take_effect_of_kongxing),
            )
        ],
    )

    def get_FieldBuff(self, buff_id: str):
        return getattr(self, buff_id)
