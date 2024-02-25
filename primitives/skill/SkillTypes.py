import enum


class SkillTargetTypes(enum.Enum):
    ENEMY_SINGLE = 0
    ENEMY_RANGE = 1
    PARTNER_SINGLE = 2
    PARTNER_RANGE = 3
    SELF = 4
    TERRAIN = 5


class SkillType(enum.IntEnum):
    Physical = 0
    Magical = 1
    Move = 2
