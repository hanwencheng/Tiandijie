from typing import List

from primitives.map.Terrain import Terrain
from primitives.map.TerrainType import TerrainType

type TerrainMap = List[List[Terrain]]


class BattleMap:
    def __init__(self, width, height, terrain_map):
        self.width = width
        self.height = height
        self.map: TerrainMap = [[self._init_terrain_by_type_id(terrain_map[j][i]) for i in range(width)] for j in
                                range(height)]

    @staticmethod
    def _init_terrain_by_type_id(type_id) -> Terrain:
        init_terrain_type = TerrainType.NORMAL
        for terrain_type in TerrainType:
            if terrain_type.value[0] == type_id:
                init_terrain_type = terrain_type
        return Terrain(init_terrain_type)

    def display_map(self):
        for row in self.map:
            print(' '.join(str(cell.terrain_type.value[0]) for cell in row))

    def set_map(self, terrain_map: TerrainMap):
        if len(terrain_map) == self.height and len(terrain_map[0]) == self.width:
            self.map = [[self._init_terrain_by_type_id(terrain_map[j][i]) for i in range(len(terrain_map[0]))] for j in range(len(terrain_map))]
