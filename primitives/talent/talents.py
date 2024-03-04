from functools import partial

from calculation.ModifierAttributes import ModifierAttributes as ma
from primitives.effects.ModifierEffect import ModifierEffect
from primitives.RequirementCheck.RequirementsCheck import RequirementCheck as RS
from primitives.effects.EventListener import EventListener
from calculation.Effects import Effects
from primitives.effects.Event import EventTypes
from primitives.talent.Talent import Talent


class Talents:
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
                partial(
                    Effects.add_enemies_harm_buff_and,
                    additional_buff_name="youjin",
                    enemy_number=2,
                    buff_number=1,
                    range=7,
                    duration=2,
                ),
            )
        ],
    )
