from enum import Enum
from calculation.ModifierAttributes import ModifierAttributes as Ma
from primitives.RequirementCheck.RequirementsCheck import RequirementCheck as Rs
from primitives.effects.ModifierEffect import ModifierEffect
from functools import partial


class Stone:
    def __init__(self, id, effect, value, percentage):
        self.id = id
        self.effect = effect  # [天, 地, 荒]
        self.value = value  # [带两个, 带三个]
        self.percentage = []


class Stones(Enum):
    # wumian = Stone(
    #     effect = ["life", attack", "defense", "magic_attack", "magic_defense", "luck"],
    #     value = [0, 0, 0, 0, 0],
    #     percentage = [0, 0, 0, 0, 0]
    # )
    @classmethod
    def get_stone_by_id(cls, stone_id):
        for stone in cls:
            if stone.value.id == stone_id:
                return stone.value
        return None

    wumian = Stone(
        id="wumian",
        effect=[
            [747, 403, 0, 0, 0],
            [0, 0, 282, 0, 242],
            [868, 363, 0, 0, 0],
        ],
        value=[
            [
                ModifierEffect(Rs.always_true, {Ma.luck_percentage: 25}),
                ModifierEffect(
                    # partial(Rs.self_is_battler_attacker_and_luck_is_higher),
                    Rs.always_true,
                    {Ma.battle_damage_percentage: 10, Ma.critical_percentage: 10},
                ),
            ]
        ],
        percentage=[0, 0, 0, 0, 0],
    )

    miwang = Stone(
        id="miwang",
        effect=[
            [747, 403, 0, 0, 0],
            [0, 0, 242, 0, 282],
            [868, 363, 0, 0, 0],
        ],
        value=[
            [
                ModifierEffect(Rs.always_true, {Ma.luck_percentage: 10}),
                ModifierEffect(
                    # partial(Rs.miwang_requires_check),
                    Rs.always_true,
                    {
                        Ma.attack_percentage: 3,
                        Ma.magic_attack_percentage: 3,
                        Ma.defense_percentage: 3,
                        Ma.magic_defense_percentage: 3,
                        Ma.luck_percentage: 3,
                    },
                ),
            ]
        ],
        percentage=[0, 0, 0, 0, 0],
    )

    # 三枚	对友方使用绝学后，40%概率使目标获得1个随机「有益状态」。
    minkui = Stone(
        id="minkui",
        effect=[
            [706, 0, 0, 363, 0],
            [0, 0, 262, 0, 343],
            [807, 0, 0, 323, 0],
        ],
        value=[
            [
                ModifierEffect(Rs.always_true, {Ma.life_percentage: 10}),
                ModifierEffect(
                    # partial(Rs.self_is_battler_attacker_and_luck_is_higher),
                    Rs.always_true,
                    {Ma.battle_damage_percentage: 10, Ma.critical_percentage: 10},
                ),
            ]
        ],
        percentage=[0, 0, 0, 0, 0],
    )