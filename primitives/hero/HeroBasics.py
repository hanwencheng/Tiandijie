import enum


class Gender(enum.IntEnum):
    MALE = 1
    FEMALE = 2


class Professions(enum.Enum):
    # ID，RANGE, MOVE
    GUARD = (1, 1, 3)
    SWORDSMAN = (2, 1, 3)
    SORCERER = (3, 2, 3)
    PRIEST = (4, 2, 3)
    ARCHER = (5, 2, 3)
    RIDER = (6, 1, 5)
    WARRIOR = (7, 1, 4)

