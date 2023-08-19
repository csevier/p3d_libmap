from enum import Enum
from panda3d.core import Vec3


class EntitySpawnType(Enum):
    WORLDSPAWN = 0
    MERGE_WORLDSPAWN = 1
    ENTITY = 2
    GROUP = 3


class Entity:
    def __init__(self, properties=None, brushes=None, center=None, spawn_type=EntitySpawnType.WORLDSPAWN):
        if properties is None:
            self.properties = {}
        else:
            self.properties = properties
        if brushes is None:
            self.brushes = []
        else:
            self.brushes = brushes
        if center is None:
            self.center = Vec3()
        else:
            self.center = center
        self.spawn_type = spawn_type
