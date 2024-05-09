from functools import partial
from enum import Enum

from calculation.ModifierAttributes import ModifierAttributes as ma
from primitives.effects.ModifierEffect import ModifierEffect
from primitives.RequirementCheck.RequirementsCheck import RequirementCheck as RS
from primitives.RequirementCheck.TalentRequirementChecks import (
    TalentRequirementChecks as TRs,
)
from primitives.effects.EventListener import EventListener
from calculation.Effects import Effects
from calculation.TalentEffect import TalentEffects
from primitives.effects.Event import EventTypes
from primitives.talent.Talent import Talent


class Talents(Enum):
    # 律: 面圣礼拜: 主动攻击「对战中」物攻提高15%。行动结束时，对十字7格范围2个敌方施加1个随机「有害状态」和「幽禁」状态，持续2回合
    mianshenglibai = Talent(
        "mianshenglibai",
        "lv",
        [ModifierEffect(RS.always_true, {ma.battle_damage_percentage: 15})],
        [
            EventListener(
                EventTypes.action_end,
                1,
                RS.always_true,
                partial(TalentEffects.take_effect_of_lv),
            )
        ],
    )

    # 苍狼: 荒原狼神: 代替相邻1格内友方承受所有攻击，自身3格范围内每存在1个其他友方免伤提高15%，护卫范围提升1格（最多提升30%/2格），当达上限时，自身双防额外提升20%。造成伤害后，施加「裂伤」状态，持续2回合。主动攻击或遭受攻击前，若目标携带「裂伤」状态，则获得「循血」状态，持续1回合（每回合只能触发1次）。
    huangyuanlangshen = Talent(
        "huangyuanlangshen",
        "canglang",
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.physical_protect_range: 1,
                    ma.magic_protect_range: 1,
                },
            ),
            ModifierEffect(
                partial(RS.PositionChecks.in_range_partner_count_with_limit, 3, 2),
                {ma.physical_protect_range: 1, ma.magic_protect_range: 1},
            ),
            ModifierEffect(
                partial(RS.PositionChecks.partner_in_range_count_bigger_than, 3, 2),
                {ma.defense_percentage: 20, ma.magic_defense_percentage: 20},
            ),
        ],
        [
            EventListener(
                EventTypes.damage_end,
                1,
                RS.always_true,
                partial(Effects.add_buffs, ["lieshang"], 2),
            ),
            EventListener(
                EventTypes.damage_end,
                1,
                partial(TRs.huangyuanlangshen_requires_check),
                partial(Effects.add_self_buffs, "xunxue", 1),
            ),
            EventListener(
                EventTypes.under_damage_end,
                1,
                partial(TRs.huangyuanlangshen_requires_check),
                partial(Effects.add_self_buffs, "xunxue", 1),
            ),
            EventListener(
                EventTypes.turn_start,
                1,
                RS.always_true,
                partial(TalentEffects.refresh_Talent_trigger),
            ),
        ],
    )

    # 冰蝉玉剑: 寒蝉出鞘:「对战中」伤害、物防提升20%。受到伤害时，承受本次伤害量的80%，并将其转化为「匿鞘」状态施加给自身，持续2回合。主动使用伤害绝学造成伤害后，消耗「匿鞘」状态对目标额外造成1次伤害（「匿鞘」存储量的50%，无法被减免）。
    # hanchanchuqiao = Talent(
    #     "hanchanchuqiao",
    #     "bingchanyujian",
    #     [
    #         ModifierEffect(
    #             partial(RS.is_in_battle),
    #             {ma.defense_percentage: 20, ma.magic_defense_percentage: 20},
    #         ),
    #     ],
    #     [
    #         EventListener(
    #             EventTypes.under_damage_end,
    #             1,
    #             RS.always_true,
    #             partial(Effects.add_self_buffs, "niqiao", 2),  # 做减伤操作
    #         ),
    #     ],
    # )

    # 赛特: 火神降临: 气血越高，伤害、炎属相免伤越高（最高25%）。主动攻击造成伤害后，对目标施加「燃烧」状态，持续2回合。主动攻击「对战中」有概率（气血越高，概率越高（最高100%））触发「重击·崩山」。
    huoshenjianglin = Talent(
        "huoshenjianglin",
        "saite",
        [
            ModifierEffect(
                partial(RS.LifeChecks.self_life_is_higher_percentage, 0),
                {
                    ma.battle_damage_percentage: 25,
                    ma.fire_damage_reduction_percentage: 25,
                },
            ),
        ],
        [
            EventListener(
                EventTypes.damage_end,
                1,
                RS.always_true,
                partial(Effects.add_buffs, ["ranshao"], 2),
            ),
            EventListener(
                EventTypes.battle_start,
                1,
                partial(RS.LifeChecks.self_life_is_higher_percentage, 0),
                partial(Effects.add_self_buffs, "zhongjibengshan", 1),
            ),
        ],
    )

    # 妮可： 蜕魔灭道： 行动结束时，若相邻1格不存在其他友方，获得「挽弓」状态，反之则获得「灭道」状态。主动攻击目标后，有概率（气血越高，概率越高（最高100%））触发「重击·散魂」。
    tuimomiedao = Talent(
        "tuimomiedao",
        "nike",
        [],
        [
            EventListener(
                EventTypes.action_end,
                1,
                RS.always_true,
                partial(Effects.add_self_buffs, "wangong", 1),
            ),
            EventListener(
                EventTypes.action_end,
                1,
                partial(RS.PositionChecks.in_range_partner_count_with_limit, 1, 1),
                partial(Effects.add_self_buffs, "miedao", 1),
            ),
            EventListener(
                EventTypes.battle_start,
                1,
                partial(RS.LifeChecks.self_life_is_higher_percentage, 0),
                partial(Effects.add_self_buffs, "zhongjibengshan", 1),
            ),
        ],
    )

    # 李靖: 执法天将: 自身3格内每存在1个敌方，法攻和法术免伤提高6%（最多提高18%）。敌方主动攻击后若处于自身3格内，对攻击者造成1次法术伤害（法攻的0.3倍）并施加「战引」状态，持续1回合（每回合最多触发2次）。主动攻击或遭受对战攻击时有概率（气血越高，概率越高（最高100%））触发「重击·神威」。
    zhifatianjiang = Talent(
        "zhifatianjiang",
        "lijing",
        [
            ModifierEffect(
                partial(RS.PositionChecks.in_range_enemy_count_with_limit, 3, 3),
                {
                    ma.magic_attack_percentage: 6,
                    ma.magic_damage_reduction_percentage: 6,
                },
            ),
        ],
        [
            EventListener(
                EventTypes.enemy_battle_end,
                1,
                partial(RS.PositionChecks.enemy_attack_in_caster_range, 3),
                partial(TalentEffects.take_effect_zhifatianjiang),
            ),
            EventListener(
                EventTypes.turn_start,
                1,
                partial(RS.always_true),
                partial(TalentEffects.refresh_Talent_trigger),
            ),
            EventListener(
                EventTypes.battle_start,
                1,
                partial(RS.LifeChecks.self_life_is_higher_percentage, 0),
                partial(Effects.add_self_buffs, "zhongjibengshan", 1),
            ),
        ],
    )

    # 雪芝: 瑶池仙首: 3格范围内存在携带「仙罪」状态的敌方，自身物攻、法防提高20%。回合开始时，自身获得「仙灵」状态。主动攻击或遭受攻击后，给敌方施加1层「仙罪」状态，持续3回合。若攻击前目标已携带3层「仙罪」状态，则战后额外造成1次「固定伤害」（目标已损失气血的30%）
    yaochixianshou = Talent(
        "yaochixianshou",
        "xuezhi",
        [
            ModifierEffect(
                partial(TRs.yaochixianshou_requires_check),
                {ma.attack_percentage: 20, ma.magic_defense_percentage: 20},
            ),
        ],
        [
            EventListener(
                EventTypes.turn_start,
                1,
                RS.always_true,
                partial(Effects.add_self_buffs, "xianling", 1),
            ),
            EventListener(
                EventTypes.normal_attack_start,
                1,
                RS.always_true,
                partial(Effects.add_buffs, ["xianzui"], 3),
            ),
            EventListener(
                EventTypes.skill_attack_start,
                1,
                RS.always_true,
                partial(Effects.add_buffs, ["xianzui"], 3),
            ),
            EventListener(
                EventTypes.normal_attack_start,
                2,
                partial(RS.BuffChecks.target_buff_stack_reach, "xianzui", 3),
                partial(Effects.add_fixed_damage_by_target_lose_life, 0.3),
            ),
            EventListener(
                EventTypes.skill_attack_start,
                2,
                partial(RS.BuffChecks.target_buff_stack_reach, "xianzui", 3),
                partial(Effects.add_fixed_damage_by_target_lose_life, 0.3),
            ),
        ],
    )

    # 瞿牧之: 文昌星运: 场上每有1个其他角色使用伤害绝学后，自身获得1层「昌明」状态。使用非伤害绝学后，若自身携带大于等于2层「昌明」状态，则获得再行动（2格），本次再行动结束时减少2层「昌明」状态（间隔2回合触发）。
    # wenchangxingyun = Talent(
    #     "wenchangxingyun",
    #     "qumuzhi",
    #     [],
    #     [
    #         EventListener(
    #             EventTypes.partner_damage_skill_start,
    #             1,
    #             partial(Effects.add_self_buffs, "changming", 1),
    #         ),
    #         EventListener(
    #             EventTypes.no_damage_skill_end,
    #             2,
    #             partial(TRs.wenchangxingyun_requires_check),
    #             partial(TalentEffects.take_effect_of_wenchangxingyun),
    #         ),
    #     ],
    # )

    # 双曜冰璃: 幽煌冥华: 移动力+2，自身气血越高/低，物防/物攻数值越高，最多提高30%。行动结束时，获得「幽霜」状态，持续3回合（间隔3回合触发）。受到致命伤害时免除死亡，气血恢复50%，若携带「幽霜」状态，则额外对自身3格范围内所有敌人造成1次「固定伤害」（（物攻+物防）的50%），施加「无摧·迟缓III」状态，持续2回合（每场战斗最多触发1次）。
    youhuangminhua = Talent(
        "youhuangminhua",
        "shuangyao",
        [
            ModifierEffect(RS.always_true, {ma.move_range: 2}),
            ModifierEffect(
                partial(RS.LifeChecks.self_life_is_higher_percentage, 0),
                {ma.defense_percentage: 30},
            ),
            ModifierEffect(
                partial(RS.LifeChecks.self_life_is_lower_percentage, 0),
                {ma.attack_percentage: 30},
            ),
        ],
        [
            EventListener(
                EventTypes.action_end,
                1,
                partial(TRs.talent_is_ready),
                partial(TalentEffects.take_effect_of_youhuangminhua, stage=1),
            ),
            EventListener(
                EventTypes.hero_death,
                1,
                RS.always_true,
                partial(TalentEffects.take_effect_of_youhuangminhua, stage=2),
            ),
        ],
    )
    # 瑶姬: 䔄草灵华: 自身3格范围内存在未满血友方时，自身治疗效果和物理免伤提高20%。行动结束前，可释放绝学（「种生」/「育杀」）（间隔1回合触发）。主动使用绝学后，为携带「生息」状态的友方驱散1个「有害状态」，恢复气血（恢复量为施术者法攻的0.3倍），使携带「命杀」状态的友方随机伤害绝学冷却-1。
    # yaocaolinghua = Talent(
    #     "yaocaolinghua",
    #     "yaoji",
    #     [
    #         ModifierEffect(
    #             partial(TRs.take_effect_of_yaocaolinghua),
    #             {ma.heal_percentage: 20, ma.physical_damage_reduction_percentage: 20},
    #         ),
    #     ],
    #     [
    #         EventListener(
    #             EventTypes.action_end,
    #             1,
    #             partial(TRs.talent_is_ready),
    #             partial(TalentEffects.take_effect_of_yaocaolinghua, state=1),
    #         ),
    #         EventListener(
    #             EventTypes.skill_end,
    #             1,
    #             RS.always_true,
    #             partial(TalentEffects.take_effect_of_yaocaolinghua, state=2),
    #         ),
    #     ],
    # )

    # 剑魂·天尊: 千仞横铁: 自身「有害状态」小于3时，物攻、会心提升20%。主动攻击「对战后」附加1次50%「剑意激荡」。自身死亡时，化身为「九仪天尊剑」可被拾取（不可被清除）。
    # qianrenhengtie = Talent(
    #     "qianrenhengtie",
    #     "jianhun",
    #     [
    #         ModifierEffect(
    #             partial(RS.BuffChecks.self_harm_buff_count_smaller_than, "youhai", 3),
    #             {ma.attack_percentage: 20, ma.critical_percentage: 20},
    #         ),
    #     ],
    #     [
    #         EventListener(
    #             EventTypes.battle_end,
    #             1,
    #             RS.always_true,
    #             partial(
    #                 TalentEffects.add_fixed_damage_by_talent_owner_physical_and_magic_attack,
    #                 0.5,
    #             ),
    #         ),
    #         EventListener(
    #             EventTypes.hero_death,
    #             1,
    #             RS.always_true,
    #             partial(TalentEffects.take_effect_of_qianrenhengtie),
    #         ),
    #     ],
    # )

    # 月孛: 暗月处决: 主动攻击时伤害和物理穿透提高15%。场上有角色死亡时获得「处刑」状态，持续2回合。主动攻击若击杀敌人则重置随机1个伤害绝学冷却时间。
    anyuechujue = Talent(
        "anyuechujue",
        "yuebei",
        [
            ModifierEffect(
                partial(RS.is_attacker),
                {
                    ma.physical_damage_percentage: 15,
                    ma.magic_damage_percentage: 15,
                    ma.physical_penetration_percentage: 15,
                },
            ),
        ],
        [
            EventListener(
                EventTypes.other_hero_death,
                1,
                RS.always_true,
                partial(Effects.add_self_buffs, "chuxing", 2),
            ),
            # EventListener(
            #     EventTypes.damage_end,
            #     1,
            #     partial(TalentEffects.reset_random_damage_skill_cooldown),
            # ),
        ],
    )

    # 朱瑾: 旗临穹宇: 自身周围3格范围内存在非「铁卫」、「祝由」职业的敌方时，伤害、物理免伤提高18%。若自身处于「持旗」状态，行动结束前可选择绝学「布旗」进行释放。自身落位于「金乌旗」2格范围内时，将拾取「金乌旗」，获得「持旗」状态。死亡后，将移除场上我方朱槿布置的「金乌旗」。
    qilinqiongyu = Talent(
        "qilinqiongyu",
        "zhujin",
        [
            ModifierEffect(
                partial(TRs.linqiqiongyu_requires_check),
                {
                    ma.physical_damage_percentage: 18,
                    ma.magic_damage_percentage: 18,
                    ma.physical_damage_reduction_percentage: 18,
                },
            ),
        ],
        [
            EventListener(
                EventTypes.action_end,
                2,
                partial(RS.BuffChecks.self_has_certain_buff_in_list, ["chiqi"]),
                partial(TalentEffects.take_effect_of_qilinquanyu, 1),
            ),
            EventListener(
                EventTypes.action_end,
                1,
                partial(RS.PositionChecks.self_in_certain_terrian, "jinwuqi"),
                partial(TalentEffects.take_effect_of_qilinquanyu, 2),
            ),
            EventListener(
                EventTypes.hero_death,
                1,
                RS.always_true,
                partial(TalentEffects.take_effect_of_qilinquanyu, 3),
            ),
        ],
    )

    # 萧熇： 御战无双： 自身3格内存在敌方时，物防提高25%。遭受攻击时，获得1层「御敌」状态（上限4层），持续1回合，受到追击或连击时额外获得1层。「御敌」状态消失时，以3格范围内物攻/法攻最高的敌人为中心，对其2格范围内所有敌方造成1次「固定伤害」伤害（最大气血的12%），并施加1层「燃烧」状态，持续2回合。
    yuzhanwushuang = Talent(
        "yuzhanwushuang",
        "xiaohe",
        [
            ModifierEffect(
                partial(RS.PositionChecks.in_range_enemy_count_with_limit, 3, 1),
                {ma.physical_damage_reduction_percentage: 25},
            ),
        ],
        [
            EventListener(
                EventTypes.under_skill_attack_end,
                1,
                RS.always_true,
                partial(Effects.add_self_buffs, "yudi", 1),
            ),
            EventListener(
                EventTypes.under_normal_attack_end,
                1,
                RS.always_true,
                partial(Effects.add_self_buffs, "yudi", 1),
            ),
            EventListener(
                EventTypes.under_double_attack_end,
                1,
                RS.always_true,
                partial(Effects.add_self_buffs, "yudi", 1),
            ),
            EventListener(
                EventTypes.under_chase_attack_end,
                1,
                RS.always_true,
                partial(Effects.add_self_buffs, "yudi", 1),
            ),
        ],
    )

    # 太玄灵狐: 狐踪千里: 目标气血低于90%时，「对战中」伤害提高30%。自身相邻1格内开启「引导区域」：「咒师」「羽士」「祝由」职业的友方移动力消耗-1。若3格范围内任意友方受到伤害，则自身获得「警觉」状态，持续1回合（每回合触发2次）。
    huzongqianli = Talent(
        "huzongqianli",
        "taixuan",
        [
            ModifierEffect(
                partial(RS.LifeChecks.target_life_is_below, 90),
                {ma.battle_damage_percentage: 30},
            ),
        ],
        [
            EventListener(
                EventTypes.game_start,
                1,
                RS.always_true,
                partial(TalentEffects.init_talent_field_buff, "huzongqianli"),
            ),
        ],
    )

    # 九色鹿: 鹿步生莲: 自身气血越高伤害和暴击率越高（最高提高20%）。对主动移动后的格子施加「莲云」效果，持续2回合。自身在已存在的友方「莲云」地形上移动时不消耗移动力。
    lubushenglian = Talent(
        "lubushenglian",
        "jiuselu",
        [
            ModifierEffect(
                partial(RS.LifeChecks.self_life_is_higher_percentage, 0),
                {ma.battle_damage_percentage: 20, ma.critical_percentage: 20},
            ),
        ],
        [],
    )

    # 伎乐飞天: 乳海双生: 3格范围内存在其他友方时法攻、会心提升15%。自身为雷/光属相时激活领域「天鼓法华」/「叹妙摩耶」。行动结束前，可额外使用绝学「光·自在」/「雷·自在」（间隔2回合触发，使用后将切换所有专属绝学并刷新冷却时间且保留当前气力）
    ruhaishuangsheng = Talent(
        "ruhaishuangsheng",
        "jilefeitian",
        [
            ModifierEffect(
                partial(RS.PositionChecks.in_range_partner_count_with_limit, 3, 1),
                {ma.magic_attack_percentage: 15, ma.critical_percentage: 15},
            ),
        ],
        [
            EventListener(
                EventTypes.game_start,
                1,
                RS.always_true,
                partial(TalentEffects.init_talent_field_buff, "ruhaishuangsheng"),
            ),
            EventListener(
                EventTypes.action_end,
                1,
                partial(TRs.ruhaishuangsheng_requires_check, 1),
                partial(Effects.add_extra_skill, "guangzizai"),
            ),
            EventListener(
                EventTypes.action_end,
                1,
                partial(TRs.ruhaishuangsheng_requires_check, 2),
                partial(Effects.add_extra_skill, "leizizai"),
            ),
            EventListener(
                EventTypes.action_end,
                1,
                partial(RS.self_use_certain_skill, "guangzizai"),
                partial(TalentEffects.take_effect_of_ruhaishuangsheng, 1),
            ),
            EventListener(
                EventTypes.skill_end,
                1,
                partial(RS.self_use_certain_skill, "leizizai"),
                partial(TalentEffects.take_effect_of_ruhaishuangsheng, 2),
            ),
        ],
    )

    # 安逸: 炼火灼剑: 伤害提高15%，使用伤害绝学前获得「注能」状态，持续2回合。使用绝学后，在自身2格范围内制造「真炎」地形，持续2回合。
    # liuhuozhuojian = Talent(
    #     "liuhuozhuojian",
    #     "anyi",
    #     [
    #         ModifierEffect(RS.always_true, {ma.physical_damage_percentage: 15, ma.magic_damage_percentage: 15}),
    #     ],
    #     [
    #         EventListener(
    #             EventTypes.skill_start,
    #             1,
    #             RS.always_true,
    #             partial(Effects.add_self_buffs, "zhuneng", 2),
    #         ),
    #         EventListener(
    #             EventTypes.skill_end,
    #             1,
    #             RS.always_true,
    #             partial(Effects.add_terrain, "zhenyan", 2),
    #         ),
    #     ],
    # )

    # 御卿: 幽明慈心: 3格内存在未结束行动的其他友方角色时，治疗效果提高20%。使用绝学后使气血全满的友方目标「有益状态」等级提升1级。3格内友方「对战后」若气血小于等于50%，恢复该角色气血（恢复量为施术者法攻的0.5倍）（每回合发动2次）。
    youmingcixin = Talent(
        "youmingcixin",
        "yuqing",
        [
            ModifierEffect(
                partial(TRs.youmingcixin_requires_check),
                {ma.heal_percentage: 20},
            ),
        ],
        [
            EventListener(
                EventTypes.skill_end,
                1,
                RS.always_true,
                partial(TalentEffects.take_effect_of_youmingcixin),
            ),
            EventListener(
                EventTypes.turn_start,
                1,
                RS.always_true,
                partial(TalentEffects.refresh_Talent_trigger),
            ),
        ],
    )

    # 双双: 上善道心: 每携带1个「有益状态」伤害和法术免伤提高5%（最多提高20%）。行动结束前，若2格内有其他友方，可选择「关切」或「授业」中的1个绝学进行释放，并复制身上的3个「有益状态」给目标（间隔1回合触发）
    shangshandaoxin = Talent(
        "shangshandaoxin",
        "shuangshuang",
        [
            ModifierEffect(
                partial(RS.BuffChecks.self_benefit_buff_count, 4),
                {
                    ma.battle_damage_percentage: 5,
                    ma.magic_damage_reduction_percentage: 5,
                },
            ),
        ],
        [
            EventListener(
                EventTypes.action_end,
                1,
                partial(RS.PositionChecks.has_partner_in_range, 2),
                partial(TalentEffects.take_effect_of_shangshandaoxin),
            ),
        ],
    )

    # 霸熊高戚: 怒熊之威: 除气血外全属性提高15%，遭受物理/法术攻击时，若自身物防/法防大于等于目标物攻/法攻的50%/40%，则免伤额外提高15%。使用绝学后，对3格范围所有敌人施加1个随机「有害状态」，且自身获得「暗铠」状态，开启「威慑」领域，持续1回合。
    nuxiongzhiwei = Talent(
        "nuxiongzhiwei",
        "baxionggaoqi",
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.attack_percentage: 15,
                    ma.defense_percentage: 15,
                    ma.magic_attack_percentage: 15,
                    ma.magic_defense_percentage: 15,
                    ma.luck_percentage: 15,
                },
            ),
        ],
        [
            EventListener(
                EventTypes.skill_end,
                1,
                RS.always_true,
                partial(TalentEffects.take_effect_of_nuxiongzhiwei),
            ),
        ],
    )

    # 归棹: 占风望向: 主动攻击「对战前」，每移动1格，伤害提高6%（最多提高30%）。行动结束时，基于自身剩余移动力格数获得对应等级的「神行」类状态（「神行I」「神行II」「神行III」），持续1回合。
    zhanfengwangxiang = Talent(
        "zhanfengwangxiang",
        "guizhao",
        [
            ModifierEffect(
                partial(RS.get_moves_before_battle, 5),
                {ma.battle_damage_percentage: 6},
            )
        ],
        [
            EventListener(
                EventTypes.action_end,
                1,
                RS.always_true,
                partial(TalentEffects.take_effect_of_zhanfengwangxiang),
            ),
        ],
    )

    # 罗渊女皇: 无上女皇: 自身携带「有益状态」大于等于3时，伤害、暴击抗性提升15%。使用伤害绝学后，夺取自身3格范围内每个敌方最多2个「有益状态」，若夺取数量达上限则获得一层「餍足」状态。「餍足」状态达到5层时消耗所有「餍足」状态转化为「极乐」状态，持续2回合。
    wushangnvhuan = Talent(
        "wushangnvhuan",
        "luoyuannvhuang",
        [
            ModifierEffect(
                partial(RS.BuffChecks.self_benefit_buff_count, 3),
                {
                    ma.battle_damage_percentage: 15,
                    ma.suffer_critical_damage_percentage: 15,
                },
            ),
        ],
        [],
    )

    # 幽篁: 玄阴祭魂: 使用绝学造成伤害后，自身获得1层「魂魄之力」状态。携带「魂魄之力」大于3层时，立刻获得「超载」状态，持续3回合。「超载」消失时，损失3层「魂魄之力」，获得「虚弱」状态，持续1回合。
    xuanyinjihun = Talent(
        "xuanyinjihun",
        "youhuang",
        [],
        [
            EventListener(
                EventTypes.damage_end,
                1,
                RS.self_is_used_active_skill,
                partial(Effects.add_self_buffs, "hunpozhili", 15),
            ),
            EventListener(
                EventTypes.action_start,
                1,
                partial(RS.BuffChecks.self_benefit_buff_count, 3),
                partial(Effects.add_self_buffs, "chaozai", 3),
            ),
        ],
    )

    # 朝歌: 红颜媚骨: 与「非女性角色」作战，「对战中」伤害提高25%。主动攻击每命中1个目标，获得1层「盈尾」状态。使用绝学后，行动结束时，消耗「盈尾」层数对2格范围内随机敌方造成对应次数「固定伤害」（法攻的10%）并驱散1个「有益状态」，若有敌方被「盈尾」连续攻击2次及以上，则被立刻施加「魅惑」状态，持续1回合。
    # 「盈尾」：盈盈佳人笑，百媚倾城欢（无法驱散，上限6层）。
    # 「魅惑」：受到暴击概率+30%，无法选中施加者（无法驱散）。
    hongyanmeigu = Talent(
        "hongyanmeigu",
        "chaoge",
        [
            ModifierEffect(
                partial(RS.in_battle_with_non_female),
                {ma.battle_damage_percentage: 25},
            ),
        ],
        [
            EventListener(
                EventTypes.damage_end,
                1,
                RS.always_true,
                partial(TalentEffects.take_effects_of_hongyanmeigu, 1),
            ),
            EventListener(
                EventTypes.action_end,
                1,
                RS.always_true,
                partial(TalentEffects.take_effects_of_hongyanmeigu, 2),
            ),
        ],
    )

    # 露葵: 聆海抒涛: 伤害提高15%，主动攻击后，对选取的目标格子周围1格范围内所有敌方造成1次物理伤害（0.3倍物攻）并制造「霜冻」地形，持续2回合。
    linghaishutao = Talent(
        "linghaishutao",
        "lukui",
        [
            ModifierEffect(
                RS.always_true,
                {ma.physical_damage_percentage: 15, ma.magic_damage_percentage: 15},
            ),
        ],
        [
            EventListener(
                EventTypes.damage_end,
                1,
                RS.always_true,
                partial(TalentEffects.take_effect_of_linghaishutao),
            ),
        ],
    )

    # 殷千炀： 荒神凶魄： 若气血大于等于50%，物攻和暴击率提高15%，与携带「慑服」状态的敌方「对战中」触发闪避。使用主动绝学后，行动结束时对十字5格范围内物攻/法攻属性最高的2个敌方施加「慑服」状态，持续2回合。
    huangshenxiongpo = Talent(
        "huangshenxiongpo",
        "yinqianyang",
        [
            ModifierEffect(
                partial(RS.LifeChecks.self_life_is_higher, 50),
                {ma.attack_percentage: 15, ma.critical_percentage: 15},
            ),
            ModifierEffect(
                partial(RS.BuffChecks.target_has_certain_buff, "shefu"),
                {ma.is_dodge_attack: True},
            ),
        ],
        [
            EventListener(
                EventTypes.action_end,
                1,
                partial(RS.self_is_used_active_skill),
                partial(TalentEffects.take_effect_of_huangshenxiongpo),
            ),
        ],
    )

    # 胧夜: 破晦深孚: 无视光属相克制。气血越高伤害、物理免伤越高（最高25%） 受到伤害后，对攻击者施加1个随机「有害状态」和「血魂」状态，持续2回合。（每回合最多触发3次）。
    pohuishenfu = Talent(
        "pohuishenfu",
        "longye",
        [
            ModifierEffect(
                partial(RS.LifeChecks.self_life_is_higher_percentage, 0),
                {
                    ma.battle_damage_percentage: 25,
                    ma.physical_damage_reduction_percentage: 25,
                },
            ),
            ModifierEffect(
                RS.always_true,
                {ma.ignore_element_advantage: True},
            ),
        ],
        [
            EventListener(
                EventTypes.under_damage_end,
                1,
                RS.always_true,
                partial(TalentEffects.take_effect_of_pohuishenfu),
            ),
            EventListener(
                EventTypes.turn_start,
                1,
                RS.always_true,
                partial(TalentEffects.refresh_Talent_trigger),
            ),
        ],
    )

    # 少侠应奉仁: 天玄耀威: 气血百分比高于3格范围内任意角色时，伤害提高20%。主动攻击每造成1次伤害后，获得1层「剑威」状态（上限3层），行动结束时，若携带3层「剑威」状态，则消耗所有「剑威」状态对自身3格范围内所有敌人造成1次「固定伤害」（物攻的30%）并获得再行动。（该效果间隔3回合发动）
    tianxuanyaowei = Talent(
        "tianxuanyaowei",
        "shaoxia",
        [
            ModifierEffect(
                partial(RS.LifeChecks.self_life_is_higher_than_target_in_range),
                {ma.physical_damage_percentage: 20, ma.magic_damage_percentage: 20},
            ),
        ],
        [
            EventListener(
                EventTypes.damage_end,
                1,
                RS.always_true,
                partial(Effects.add_self_buffs, "jianwei"),
            ),
            EventListener(
                EventTypes.action_end,
                1,
                partial(RS.BuffChecks.self_buff_stack_reach, 3, "jianwei"),
                partial(TalentEffects.take_effect_of_tianxuanyaowei),
            ),
        ],
    )

    # 傅雅鱼: 神武奇谋: 不携带「有害状态」时，治疗效果提高20%，对友方释放非伤害绝学后，驱散2个「有害状态」，并施加「清流」状态。
    shenwuqimou = Talent(
        "shenwuqimou",
        "fuyayu",
        [
            ModifierEffect(
                partial(RS.BuffChecks.self_harm_buff_count_smaller_than, 1),
                {ma.heal_percentage: 20},
            ),
        ],
        [
            EventListener(
                EventTypes.skill_end,
                1,
                partial(RS.skill_is_no_damage_and_target_is_partner),
                partial(Effects.add_buffs, ["qingliu"], 15),
            ),
        ],
    )

    # 公孙七月: 人小鬼大: 物攻提高15%。行动结束前，若3格范围内有敌方，选择「横财」或「迷窍」中一个技能释放。行动结束时，如果处于敌方危险范围内且未造成伤害（「横财」「迷窍」除外），则获得再行动（间隔2回合触发）。
    # renxiaoguidai = Talent(
    #     "renxiaoguidai",
    #     "gongsunqiye",
    #     [
    #         ModifierEffect(RS.always_true, {ma.attack_percentage: 15}),
    #     ],
    #     [
    #         EventListener(
    #             EventTypes.action_end,
    #             1,
    #             partial(RS.PositionChecks.enemy_in_range_count_bigger_than, 3, 0),
    #             partial(TalentEffects.take_effect_of_renxiaoguidai),
    #         ),
    #     ],
    # )

    # 星占贤者: 经纬星穹: 每携带1个「有益状态」，法攻提高6%（最多提高18%）。场上每有一个友方角色使用绝学后，获得1点「星屑」（上限10点）。当携带足量「星屑」时行动结束前，可选「天枢」「天权」（「天枢」「天权」任一绝学被使用后，将替换为「玉衡」「开阳」「摇光」中的1个绝学进行释放并消耗「星屑」（当结界自然消失或被覆盖后，将进入2回合冷却时间）。「摇光破军界」持续时，暴击率提高15%，射程提高1。
    # jingweixingqiong = Talent(
    #     "jingweixingqiong",
    #     "xingzhanxianzhe",
    #     [
    #         ModifierEffect(
    #             partial(RS.BuffChecks.self_benefit_buff_count, 3),
    #             {ma.magic_attack_percentage: 6},
    #         ),
    #     ],
    #     [
    #         EventListener(
    #             EventTypes.partner_damage_skill_end,
    #             1,
    #             RS.always_true,
    #             partial(Effects.add_self_buffs, "xingxie", 1),
    #         ),
    #         EventListener(
    #             EventTypes.action_end,
    #             1,
    #             partial(RS.BuffChecks.self_benefit_buff_count, 10),
    #             partial(Effects.add_extra_skill, "tianquan"),
    #         ),
    #         EventListener(
    #             EventTypes.action_end,
    #             1,
    #             partial(RS.BuffChecks.self_benefit_buff_count, 10),
    #             partial(Effects.add_extra_skill, "tianshu"),
    #         ),
    #         EventListener(
    #             EventTypes.action_end,
    #             1,
    #             partial(RS.self_use_certain_skill, "tianquan"),
    #             partial(TalentEffects.take_effect_of_jingweixingqiong),
    #         ),
    #         EventListener(
    #             EventTypes.action_end,
    #             1,
    #             partial(RS.self_use_certain_skill, "tianshu"),
    #             partial(TalentEffects.take_effect_of_jingweixingqiong),
    #         ),
    #     ],
    # )

    # 西莉亚: 命运意志: 全场每存在1名友方，免伤提高5%（最多提高20%）。每场战斗开始时，获得1次免死机会，受到致命伤害时免除死亡，自身恢复50%气血，为3格范围内其他友方恢复30%气血，并立即激活「圣枪之力」状态。（每场战斗只能触发1次）。自身与其他友方每有1个受到伤害累积1层「觉醒之力」，当累积6层「觉醒之力」时，将激活「圣枪之力」状态，持续2回合。
    mingyunyizhi = Talent(
        "mingyunyizhi",
        "xiliya",
        [
            ModifierEffect(
                partial(RS.all_partners_live_count, 4),
                {
                    ma.physical_damage_reduction_percentage: 20,
                    ma.magic_damage_reduction_percentage: 20,
                },
            ),
        ],
        [
            EventListener(
                EventTypes.game_start,
                1,
                RS.always_true,
                partial(TalentEffects.init_talent_field_buff, "mingyunyizhi"),
            ),
        ],
    )

    # 白素贞: 和雨如润: 战斗开始获得3层「法力」，每次使用伤害绝学时，暴击率提高15%，消耗2层「法力」，若本回合未使用伤害绝学，则行动结束时获得1层「法力」。自身携带大于等于2层「法力」时，可获得「施咒」和「神算」效果。
    heyururun = Talent(
        "heyururun",
        "baisuzhen",
        [
            ModifierEffect(
                partial(TRs.heyururun_requires_check), {ma.critical_percentage: 15}
            ),
        ],
        [
            EventListener(
                EventTypes.battle_start,
                1,
                RS.always_true,
                partial(Effects.add_self_buffs, "fali", 3),
            ),
            EventListener(
                EventTypes.under_battle_start,
                1,
                RS.always_true,
                partial(Effects.add_self_buffs, "fali", 3),
            ),
            EventListener(
                EventTypes.skill_end,
                1,
                partial(TRs.heyururun_requires_check),
                partial(Effects.reduce_actor_certain_buff_stack, "fali", 2),
            ),
            EventListener(
                EventTypes.action_end,
                1,
                partial(RS.action_is_not_active_skill),
                partial(Effects.reduce_actor_certain_buff_stack, "fali", 2),
            ),
        ],
    )

    # 青: 潜影妙洄: 与携带「有害状态」角色作战时，「对战中」目标每有1个「有害状态」自身物攻、伤害提高5%（最高15%）使用绝学后，行动结束时可以额外使用绝学[[绝学/复初|「复初」]]（间隔2回合释放）
    qianyinmiaomiao = Talent(
        "qianyinmiaomiao",
        "qing",
        [
            ModifierEffect(
                partial(RS.BuffChecks.target_harm_buff_count),
                {ma.attack_percentage: 5, ma.battle_damage_percentage: 5},
            ),
        ],
        [
            EventListener(
                EventTypes.action_end,
                1,
                partial(RS.self_is_used_active_skill),
                partial(Effects.add_extra_skill, "fuchu"),
            ),
        ],
    )

    # 法海: 普渡教谕: 伤害提高20%，主动攻击时目标每多携带一个「有益状态」降低3%（最多9%）。主动攻击前，驱散目标1个「有益状态」，若为单体攻击额外驱散2个。行动结束时，对2格内随机1名未携带「有益状态」的敌方施加「晕眩」状态，持续1回合（间隔2回合触发）
    pudujiaoyu = Talent(
        "pudujiaoyu",
        "fahai",
        [
            ModifierEffect(
                RS.always_true,
                {ma.battle_damage_percentage: 20},
            ),
            ModifierEffect(
                partial(RS.BuffChecks.target_benefit_buff_count),
                {ma.battle_damage_percentage: 3},
            ),
        ],
        [
            EventListener(
                EventTypes.damage_start,
                1,
                RS.always_true,
                partial(Effects.remove_target_benefit_buffs, 1),
            ),
            EventListener(
                EventTypes.damage_start,
                2,
                partial(RS.target_is_single),
                partial(Effects.remove_target_benefit_buffs, 2),
            ),
            EventListener(
                EventTypes.action_end,
                1,
                RS.always_true,
                partial(TalentEffects.take_effect_of_pudujiaoyu),
            ),
        ],
    )

    # 阿秋: 墨矩神机: 对处于自身直线位置的目标造成伤害和暴击率提高15%。使用绝学对目标造成暴击，施加「电流」状态，持续2回合，若被暴击目标处于自身直线位置，绝学释放后，使目标被传送至其身后2格的空格位置。
    mojushenji = Talent(
        "mojushenji",
        "aqiu",
        [
            ModifierEffect(
                partial(RS.PositionChecks.in_the_same_line),
                {ma.battle_damage_percentage: 15, ma.critical_percentage: 15},
            ),
        ],
        [
            EventListener(
                EventTypes.critical_damage_end,
                1,
                partial(RS.self_is_used_active_skill),
                partial(Effects.add_buffs, ["dianliu"], 2),
            ),
        ],
    )

    # 呼延朔: 三尺坤舆: 主动攻击造成击杀后，获得「遁地」状态，持续2回合。敌方行动结束时，位于呼延朔附近1格时，则「遁地」状态提前结束。非「遁地」状态下，物攻+15%。
    sanchikunyu = Talent(
        "sanchikunyu",
        "huyanshuo",
        [
            ModifierEffect(
                partial(RS.BuffChecks.self_has_no_certain_buff, "dundi"),
                {ma.attack_percentage: 15},
            ),
        ],
        [
            EventListener(
                EventTypes.kill_enemy_end,
                1,
                RS.always_true,
                partial(Effects.add_self_buffs, "dundi", 2),
            ),
        ],
    )

    # 巴艾迩: 昭星神降: 主动攻击时，物攻提高15%。自身及周围3格范围内友方主动攻击时，每对1个目标造成暴击，获得1层「灵辉」，每击杀1个目标立即获得7层「灵辉」（最多叠加14层）。
    zhaoxingshenjiang = Talent(
        "zhaoxingshenjiang",
        "baaini",
        [
            ModifierEffect(
                partial(RS.is_attacker),
                {ma.attack_percentage: 15},
            ),
        ],
        [
            EventListener(
                EventTypes.damage_end,
                1,
                RS.always_true,
                partial(Effects.add_self_buffs, "linghui"),
            ),
            EventListener(
                EventTypes.kill_enemy_end,
                2,
                RS.always_true,
                partial(Effects.increase_actor_certain_buff_stack, "linghui"),
            ),
        ],
    )

    # 卓尔: 诡秘权谋: 4格范围内同时存在其他友方和敌方时，自身伤害和会心提高20%。 在首次行动结束前，可选择[[绝学/挑拨离间|「挑拨离间」]]或[[绝学/传风煽火|「传风煽火」]]或[[绝学/聚众成势|「聚众成势」]]中的1个绝学进行释放（间隔3回合释放）
    guiyiquanmou = Talent(
        "guiyiquanmou",
        "zhuoer",
        [
            ModifierEffect(
                partial(RS.PositionChecks.in_range_partner_count_with_limit, 4, 1),
                {ma.battle_damage_percentage: 20, ma.critical_percentage: 20},
            ),
        ],
        [
            # EventListener(
            #     EventTypes.action_end,
            #     1,
            #     partial(RS.PositionChecks.has_partner_and_enemy_in_range, 4, 1),
            #     partial(TalentEffects.take_effect_of_guiyiquanmou),
            # ),
        ],
    )

    # 神阙青衣: 神缕缠心: 物攻提高15%，使用绝学造成伤害后，施加「万缕」状态，持续2回合。行动结束时，若自身处于两个携带「万缕」状态敌人直线方向的中间位置，则剪断「万缕」，神阙青衣剪断「万缕」状态时获得「闪避」状态，持续2回合。若对方携带「万缕」状态，受到神阙青衣的伤害提高15%。
    shenlvchanxin = Talent(
        "shenlvchanxin",
        "shenqueqingyi",
        [
            ModifierEffect(
                RS.always_true,
                {ma.attack_percentage: 15},
            ),
        ],
        [
            EventListener(
                EventTypes.skill_end,
                1,
                partial(RS.self_is_used_active_skill),
                partial(Effects.add_buffs, ["wanlv"], 2),
            ),
            # EventListener(
            #     EventTypes.action_end,
            #     2,
            #     RS.always_true,
            #     partial(TalentEffects.take_effect_of_shenqueqingyi),
            # ),
        ],
    )

    # 真胤: 金轮法天: 2格内每存在1名其他友方，免伤和暴击伤害减免提高5%（最多提高15%）。代替相邻1格内友方承受所有攻击，使用绝学后护卫范围提高到2格，持续2回合。
    # 使用非伤害绝学后，行动结束时以自身为阵眼，开启2格范围的法阵「回灵界」且在范围内空格上随机生成2个「回灵阵式」，持续1回合。使用伤害绝学后，行动结束时以被选取目标为阵眼，开启2格范围的法阵「眩灭界」且在范围内空格上随机生成2个「眩灭阵式」，持续1回合。
    jinlunfatian = Talent(
        "jinlunfatian",
        "zhenyin",
        [
            ModifierEffect(
                partial(RS.PositionChecks.in_range_partner_count_with_limit, 2, 1),
                {
                    ma.physical_damage_reduction_percentage: 15,
                    ma.magic_damage_reduction_percentage: 15,
                },
            ),
            ModifierEffect(
                RS.always_true,
                {ma.physical_protect_range: 1, ma.magic_protect_range: 1},
            ),
        ],
        [
            EventListener(
                EventTypes.skill_end,
                1,
                RS.always_true,
                partial(Effects.add_self_buffs, ["huwei"], 2),
            ),
            EventListener(
                EventTypes.skill_end,
                2,
                partial(RS.skill_has_no_damage),
                partial(Effects.add_self_field_buff, "huilingjie", 1),
            ),
            EventListener(
                EventTypes.skill_end,
                2,
                partial(RS.skill_has_damage),
                partial(Effects.add_self_field_buff, "xuanmiejie", 1),
            ),
        ],
    )

    # 魔化皇甫申: 闇星逆行: 气血大于70%时，伤害和免伤提高20%。行动结束时，获得「绝心」状态。若自身2圈范围内同时存在其他「雷」和「暗」的角色时，则额外获得1层「绝心」状态，若达到5层，则转化为「执戮」状态，持续3回合。死亡时对自身2圈范围内1个气血百分比最低的敌人造成1次固定伤害（物攻的90%）
    anxingnixing = Talent(
        "anxingnixing",
        "mohuahuangfushen",
        [
            ModifierEffect(
                partial(RS.LifeChecks.self_life_is_higher, 70),
                {
                    ma.battle_damage_percentage: 20,
                    ma.physical_damage_reduction_percentage: 20,
                    ma.magic_damage_reduction_percentage: 20,
                },
            ),
        ],
        [
            EventListener(
                EventTypes.action_end,
                1,
                RS.always_true,
                partial(TalentEffects.take_effect_of_anxingnixing, 1),
            ),
            EventListener(
                EventTypes.hero_death,
                1,
                RS.always_true,
                partial(TalentEffects.take_effect_of_anxingnixing, 2),
            ),
        ],
    )

    # 允迦: 光闇对宫: 伤害提升25%，攻击前每移动1格伤害降低4%(最多降低12%）,使用绝学后，在自身周围2格张开领域「转厄生天」。
    guanganduigong = Talent(
        "guanganduigong",
        "yunjia",
        [
            ModifierEffect(
                partial(RS.get_moves_before_battle, 3),
                {ma.battle_damage_reduction_percentage: 4},
            ),
            ModifierEffect(
                RS.always_true,
                {ma.battle_damage_percentage: 25},
            ),
        ],
        [
            EventListener(
                EventTypes.skill_end,
                1,
                RS.always_true,
                partial(Effects.add_self_buffs, ["zhuaneshengtian"], 2),
            ),
        ],
    )

    # 展昭: 烜赫京畿: 3格内存在未满血的单位时，自身除气血外全属性增加15%。主动普攻攻击处于友方「剑牢」地形的目标时，触发「追击」（0.4倍伤害）。3格内的敌方主动攻击前，在以攻击者为中心的1圈内生成
    xuehejingji = Talent(
        "xuehejingji",
        "zhanzhao",
        [
            ModifierEffect(
                partial(RS.PositionChecks.life_not_full_in_range, 3),
                {
                    ma.attack_percentage: 15,
                    ma.defense_percentage: 15,
                    ma.magic_attack_percentage: 15,
                    ma.magic_defense_percentage: 15,
                    ma.luck_percentage: 15,
                },
            ),
        ],
        [],
    )

    # 霍雍: 幽氛化神: 4格内若存在冰炎暗属相的角色（包含自身），回合开始时分别获得「寒岚」「焚狱」「玄幽」状态，每种状态提升自身6%法攻和法防（最高提升18%）。
    youfenhuashen = Talent(
        "youfenhuashen",
        "huoyong",
        [
            ModifierEffect(
                partial(RS.BuffChecks.self_has_certain_buff_in_list, ["hanlan", "fenyu", "xuanyou"]),
                {ma.magic_attack_percentage: 6, ma.magic_defense_percentage: 6},
            ),
        ],
        [
            EventListener(
                EventTypes.action_start,
                1,
                partial(TRs.youfenghuashen_requires_check),
                partial(Effects.add_self_buffs, ["hanlan", "fenyu", "xuanyou"], 15),
            ),
        ],
    )