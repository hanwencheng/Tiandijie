from calculation.Range import RangeType, Range
from primitives.effects.SkillListener import SkillListener
from primitives.hero.Element import Elements
from primitives.skill.Distance import Distance, DistanceType
from primitives.skill.Skill import Skill
from primitives.skill.SkillTypes import SkillType, SkillTargetTypes
from primitives.buff.buffs import *
from calculation.ModifierAttributes import ModifierAttributes as ma
from primitives.effects.ModifierEffect import ModifierEffect
from primitives.RequirementCheck.RequirementsCheck import RequirementCheck as RS
from primitives.skill.SkillTemp import SkillTemp


class Skills(Enum):
    # normal_attack = SkillTemp(1, True),

    #  疾风快刃	 消耗： 2
    #  类别：物攻伤害	 冷却：2回合
    #  射程：1格	 范围：单体
    #  无视护卫攻击单个敌人，造成1.3倍伤害，若目标满血则「对战前」造成1次0.3倍物攻伤害。
    jifengkuairen = SkillTemp(
        "jifengkuairen",
        2,
        Elements.NONE,
        SkillType.Physical,
        SkillTargetTypes.ENEMY_SINGLE,
        2,
        Distance(DistanceType.NORMAL, 1),
        Range(RangeType.POINT, 0, 1, 1),
        1.3,
        [ModifierEffect(RS.always_true, {ma.is_ignore_protector: True})],
        [],
    )

    #  纵命格杀	 消耗： 2
    #  类别：物攻伤害	 冷却：2回合
    #  射程：1格	 范围：单体
    #  攻击单个敌人，造成1.3倍伤害，「对战前」施加「幽阙」状态，持续2回合。若目标周围1格没有友方则本次攻击无视护卫且物理穿透提高30%。
    zongmingesha = SkillTemp(
        "zongmingesha",
        2,
        Elements.ETHEREAL,
        SkillType.Physical,
        SkillTargetTypes.ENEMY_SINGLE,
        2,
        Distance(DistanceType.NORMAL, 1),
        Range(RangeType.POINT, 0, 1, 1),
        1.3,
        [
            ModifierEffect(
                partial(
                    RS.PositionChecks.no_partners_in_target_range,
                    1,
                ),
                {ma.is_ignore_protector: True, ma.physical_penetration_percentage: 30},
            )
        ],
        [],
    )

    # 律隙万变	 消耗： 1
    #  类别：再动	 冷却：3回合
    #  射程：4格	 范围：单体
    #  主动使用，传送到1个目标身周的指定空格，使自身2格范围友方/敌方的「有益状态」/「有害状态」持续时间增加1回合。自身获得再行动（2格）。
    lvxiwanbian = SkillTemp(
        "lvxiwanbian",
        1,
        Elements.ETHEREAL,
        SkillType.Move,
        SkillTargetTypes.ENEMY_SINGLE,
        3,
        Distance(DistanceType.NORMAL, 4),
        Range(RangeType.POINT, 0, 1, 1),
        0,
        [],
        [
            EventListener(
                EventTypes.move_end,
                1,
                RS.always_true,
                partial(
                    Effects.extend_enemy_harm_buffs,
                    buff_number=2,
                    range_value=2,
                    duration=1,
                ),
            ),
            EventListener(
                EventTypes.move_end,
                1,
                RS.always_true,
                partial(
                    Effects.extend_partner_benefit_buffs,
                    buff_number=2,
                    range_value=2,
                    duration=1,
                ),
            ),
        ],
    )

    # 雷引万宇	 消耗： 2
    # 类别：物攻伤害	 冷却：3回合
    # 射程：自身	 范围：2圈
    # 对范围内所有敌人造成0.3倍伤害，吸引范围内敌人到身边，若2格内存在3个及以上敌人，触发原地再行动。使用后切换为「天闪乱魂」。
    # 「天闪乱魂」：攻击单个敌人，造成1.3倍伤害，战后使目标身周1圈内所有敌人发生1圈内「扰动」状态，使用后切换为「雷引万宇」
    leiyinwanyu = SkillTemp(
        "leiyinwanyu",
        2,
        Elements.DARK,
        SkillType.Physical,
        SkillTargetTypes.ENEMY_RANGE,
        3,
        Distance(DistanceType.NORMAL, 0),
        Range(RangeType.SQUARE, 0, 2, 2),
        0.3,
        [
            # ModifierEffect(
            #     RS.always_true,
            #     {ma.is_attract: True},
            # ),
        ],
        [],
    )

    # 天闪乱魂	 消耗： -
    # 类别：物攻伤害	 冷却：-
    # 射程：2格	 范围：单体
    # 攻击单个敌人，造成1.3倍伤害，战后使目标身周1圈内所有敌人发生1圈内「扰动」状态，使用后切换为「雷引万宇」
    tianshanluanhun = SkillTemp(
        "tianshanluanhun",
        0,
        Elements.DARK,
        SkillType.Physical,
        SkillTargetTypes.ENEMY_SINGLE,
        0,
        Distance(DistanceType.NORMAL, 2),
        Range(RangeType.POINT, 0, 1, 1),
        1.3,
        [
            # ModifierEffect(
            #     RS.always_true,
            #     {ma.is_attract: True},
            # ),
        ],
        [],
    )

    # 暗霎幽琰	 消耗： 2
    # 类别：物攻伤害	 冷却：2回合
    # 射程：1格	 范围：单体
    # 攻击单个敌人，造成1.5倍伤害，「对战前」自身获得3层「绝心」状态，「对战前」施加「禁疗」状态，持续2回合。
    anshayouyan = SkillTemp(
        "anshayouyan",
        2,
        Elements.DARK,
        SkillType.Physical,
        SkillTargetTypes.ENEMY_SINGLE,
        2,
        Distance(DistanceType.NORMAL, 1),
        Range(RangeType.POINT, 0, 1, 1),
        1.5,
        [],
        [
            # EventListener(
            #     EventTypes.battle_start,
            #     1,
            #     RS.always_true,
            #     partial(Effects.take_effect_of_anshayouyan),
            # )
        ],
    )

    # 神气流转	 消耗： 2
    # 类别：治疗	 冷却：1回合
    # 射程：3格	 范围：菱形2格
    # 主动使用，恢复范围内所有友方气血（恢复量为施术者法攻的0.75倍），驱散1个「有害状态」。
    shenqiliuzhuan = SkillTemp(
        "shenqiliuzhuan",
        2,
        Elements.NONE,
        SkillType.Heal,
        SkillTargetTypes.PARTNER_RANGE,
        1,
        Distance(DistanceType.NORMAL, 3),
        Range(RangeType.DIAMOND, 2, 5, 5),
        0.75,
        [],
        [
            EventListener(
                EventTypes.battle_start,
                1,
                RS.always_true,
                partial(Effects.remove_partner_harm_buffs_in_range, 1, 2),
            )
        ],
    )
    # 载舟号令	 消耗： 2
    # 类别：支援	 冷却：3回合
    # 射程：自身	 范围：菱形3格
    # 主动使用，对范围内的所有友方施加「神护I」「固元I」状态，持续3回合。
    zaizhouhaoling = SkillTemp(
        "zaizhouhaoling",
        2,
        Elements.NONE,
        SkillType.Support,
        SkillTargetTypes.PARTNER_RANGE,
        3,
        Distance(DistanceType.NORMAL, 0),
        Range(RangeType.DIAMOND, 3, 7, 7),
        0,
        [],
        [
            EventListener(
                EventTypes.skill_start,
                1,
                RS.always_true,
                partial(Effects.add_buffs, ["shenhu", "guyuan"], 3),
            )
        ],
    )

    # 力挽狂澜	 消耗： 2
    # 类别：治疗	 冷却：3回合
    # 射程：3格	 范围：菱形4格
    # 主动使用，驱散范围内所有友方身上2个「有害状态」，并恢复气血（恢复量为施术者法攻的1倍），自身获得「微澜」「芬芳I」状态，持续2回合。
    liwankuanglan = SkillTemp(
        "liwankuanglan",
        2,
        Elements.NONE,
        SkillType.Heal,
        SkillTargetTypes.PARTNER_RANGE,
        3,
        Distance(DistanceType.NORMAL, 3),
        Range(RangeType.DIAMOND, 4, 5, 5),
        1,
        [],
        [
            EventListener(
                EventTypes.skill_end,
                1,
                RS.always_true,
                partial(Effects.add_self_buffs, ["weilan", ["fenfang"]], 2),
            ),
            EventListener(
                EventTypes.skill_start,
                1,
                RS.always_true,
                partial(Effects.remove_target_harm_buffs_in_range, 2, 4),
            ),
        ],
    )