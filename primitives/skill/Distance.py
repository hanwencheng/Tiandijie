from enum import Enum

from primitives.hero.HeroBasics import Professions


class DistanceType(Enum):
    NORMAL = 0
    CROSS = 1
    ARCHER = 2


class Distance:
    def __init__(self, distance_type: DistanceType, distance_value: int):
        self.distance_type = distance_type
        self.distance_value = distance_value


distance_profession_dict = {
    Professions.WARRIOR: Distance(DistanceType.NORMAL, 1),
    Professions.SWORDSMAN: Distance(DistanceType.NORMAL, 1),
    Professions.ARCHER: Distance(DistanceType.ARCHER, 2),
    Professions.SORCERER: Distance(DistanceType.NORMAL, 2),
    Professions.PRIEST: Distance(DistanceType.NORMAL, 2),
    Professions.GUARD: Distance(DistanceType.NORMAL, 1),
}
