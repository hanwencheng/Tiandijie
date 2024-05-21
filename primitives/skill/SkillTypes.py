import enum


class SkillTargetTypes(enum.Enum):
    ENEMY = 0
    PARTNER = 1
    TERRAIN = 3
    SELF = 4


class SkillType(enum.IntEnum):
    Physical = 0
    Magical = 1
    Move = 2
    Heal = 3
    Support = 4
    EFFECT_ENEMY = 5
