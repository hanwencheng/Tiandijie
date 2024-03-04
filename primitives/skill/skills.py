from calculation.Range import RangeType, Range
from primitives.effects.SkillListener import SkillListener
from primitives.hero.Element import Elements
from primitives.skill.Distance import Distance, DistanceType
from primitives.skill.Skill import Skill, SkillType
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
        2,
        Distance(DistanceType.NORMAL, 1),
        Range(RangeType.POINT, 0, 1, 1),
        1.3,
        [ModifierEffect(RS.always_true, {ma.is_ignore_protector: 1})],
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
                {ma.is_ignore_protector: 1, ma.physical_penetration_percentage: 30},
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
                    Effects.extend_enemy_harm_buffs, buff_number=2, range=2, duration=2
                ),
            ),
            EventListener(
                EventTypes.move_end,
                1,
                RS.always_true,
                partial(
                    Effects.extend_partner_benefit_buffs,
                    buff_number=2,
                    range=2,
                    duration=2,
                ),
            ),
        ],
    )
