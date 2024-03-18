import enum


class Gender(enum.IntEnum):
    MALE = 1
    FEMALE = 2
    OTHER = 3


class Professions(enum.Enum):
    # ID，RANGE, MOVE
    GUARD = (1, 1, 3)  # 护卫
    SWORDSMAN = (2, 1, 3)  # 侠客
    SORCERER = (3, 2, 3)  # 咒师
    PRIEST = (4, 2, 3)  # 祝由
    ARCHER = (5, 2, 3)  # 羽士
    RIDER = (6, 1, 5)  # 御风
    WARRIOR = (7, 1, 4)  # 斗将
