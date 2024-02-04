
from calculation.Range import RangeType, Range
from primitives.skill.SkillTemp import SkillTemp
from primitives.buff.buffs import *
from calculation.Effects import Effects

normal_attack = SkillTemp(1, True)

zhijianfongyou = SkillTemp(0.7, False)
# 灭剑罗渊
miejianluoyuan = SkillTemp(0.7, Range(RangeType.DIRECTIONAL, 0, 4, 3), [],
                           [
                        partial(Effects.reduce_target_benefit_buff_duration, 2),
                        partial(Effects.add_target_harm_buffs, [BuffTemps.fengjing], 2),
                        partial(Effects.check_buff_conditional_add_target_buff(youshuang, wucui_fengmai, 2))
                        ])

# 幽剑鬼狱
youjian_guiyu = SkillTemp(0.3, Range(RangeType.DIRECTIONAL, 0, 5, 1),
                          [partial(attack_all, knockback=2)],
                          [partial(1, min_targets=2, movement=5, buff_duration_preserved=True)],
                          next_skill='juejian_xionghao')

# 绝剑凶号
juejian_xionghao = SkillTemp(1.6, Range(RangeType.SELF, 0, 0, 0),
                             [partial(consume_hp, percentage=20), partial(apply_buff, jinbi, 1)],
                             next_skill='youjian_guiyu')
