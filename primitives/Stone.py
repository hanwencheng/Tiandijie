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
        self.stack = 1


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
            {
                "life": 747,
                "attack": 403,
                "defense": 0,
                "magic_attack": 0,
                "magic_defense": 0,
            },
            {
                "life": 0,
                "attack": 0,
                "defense": 282,
                "magic_attack": 0,
                "magic_defense": 242,
            },
            {
                "life": 868,
                "attack": 363,
                "defense": 0,
                "magic_attack": 0,
                "magic_defense": 0,
            },
        ],
        value=[
            [
                ModifierEffect(Rs.always_true, {Ma.luck_percentage: 25}),
            ],
            [
                ModifierEffect(
                    partial(Rs.self_is_batter_attacker_and_luck_is_higher),
                    {Ma.battle_damage_percentage: 10, Ma.critical_percentage: 10},
                ),
            ],
        ],
        percentage=[0, 0, 0, 0, 0],
    )

    wanghuan = Stone(
        id="wanghuan",
        effect=[
            {
                "life": 747,
                "attack": 403,
                "defense": 0,
                "magic_attack": 0,
                "magic_defense": 0,
            },
            {
                "life": 0,
                "attack": 0,
                "defense": 242,
                "magic_attack": 0,
                "magic_defense": 282,
            },
            {
                "life": 868,
                "attack": 363,
                "defense": 0,
                "magic_attack": 0,
                "magic_defense": 0,
            },
        ],
        value=[
            [
                ModifierEffect(Rs.always_true, {Ma.luck_percentage: 10}),
            ],
            [
                ModifierEffect(
                    # partial(Rs.wanghuan_requires_check),
                    Rs.always_true,
                    {
                        Ma.attack_percentage: 3,
                        Ma.magic_attack_percentage: 3,
                        Ma.defense_percentage: 3,
                        Ma.magic_defense_percentage: 3,
                        Ma.luck_percentage: 3,
                    },
                ),
            ],
        ],
        percentage=[0, 0, 0, 0, 0],
    )

    # 三枚	对友方使用绝学后，40%概率使目标获得1个随机「有益状态」。
    minkui = Stone(
        id="minkui",
        effect=[
            {
                "life": 706,
                "attack": 0,
                "defense": 0,
                "magic_attack": 363,
                "magic_defense": 0,
            },
            {
                "life": 0,
                "attack": 0,
                "defense": 262,
                "magic_attack": 0,
                "magic_defense": 343,
            },
            {
                "life": 807,
                "attack": 0,
                "defense": 0,
                "magic_attack": 343,
                "magic_defense": 0,
            },
        ],
        value=[
            [
                ModifierEffect(Rs.always_true, {Ma.life_percentage: 10}),
            ],
            [
                ModifierEffect(
                    # partial(Rs.self_is_battler_attacker_and_luck_is_higher),
                    Rs.always_true,
                    {Ma.battle_damage_percentage: 10, Ma.critical_percentage: 10},
                ),
            ],
        ],
        percentage=[0, 0, 0, 0, 0],
    )
