from enum import Enum


class DistanceType(Enum):
    NORMAL = 0
    CROSS = 1


class Distance:
    def __init__(self, distance_type: DistanceType, distance_value: int):
        self.distance_type = distance_type
        self.distance_value = distance_value
