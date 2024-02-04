from primitives.map.TerrainBuff import TerrainBuff


class Collectable:
    pass


class Terrain:
    def __init__(self, terrain_type):
        self.terrain_type = terrain_type
        self.buff: TerrainBuff or None = None
        self.collectable: Collectable or None = None
