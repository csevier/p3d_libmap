from enum import Enum
from entity import EntitySpawnType


class Surface:
    def __init__(self, vertices=None, indices=None):
        if vertices is None:
            self.vertices = []
        else:
            self.vertices = vertices

        if indices is None:
            self.indices = []
        else:
            self.indices = indices


class SurfaceSplitType(Enum):
    NONE = 0
    ENTITY = 1
    BRUSH = 2


class SurfaceGatherer:
    def __init__(self, map_data):
        self.map_data = map_data
        self.split_type = SurfaceSplitType.NONE
        self.entity_filter_idx = -1
        self.texture_filter_idx = -1
        self.brush_filter_texture_idx = -1
        self.face_filter_texture_idx = -1
        self.filter_worldspawn_layers = True
        self.out_surfaces = []

    def set_split_type(self, split_type):
        self.split_type = split_type

    def set_entity_index_filter(self, entity_idx):
        self.entity_filter_idx = entity_idx

    def set_texture_filter(self, texture_name):
        self.texture_filter_idx = self.map_data.find_texture(texture_name)

    def set_brush_filter_texture(self, texture_name):
        self.brush_filter_texture_idx = self.map_data.find_texture(texture_name)

    def set_face_filter_texture(self, texture_name):
        self.face_filter_texture_idx = self.map_data.find_texture(texture_name)

    def set_worldspawn_layer_filter(self, world_spawn_filter):
        self.filter_worldspawn_layers = world_spawn_filter

    def run(self):
        self.reset_state()
        index_offset = 0
        surf_inst = None
        if self.split_type == SurfaceSplitType.NONE:
            index_offset = 0
            surf_inst = self.add_surface()

        for entity_idx, entity_inst, entity_geo_inst in enumerate(zip(self.map_data.get_entities(), self.map_data.entity_geo)):
            if self.filter_entity(entity_idx):
                continue

            if self.split_type == SurfaceSplitType.ENTITY:
                if entity_inst.spawn_type == EntitySpawnType.MERGE_WORLDSPAWN:
                    self.add_surface()
                    surf_inst = self.out_surfaces[0]
                    index_offset = len(surf_inst.vertices)
                else:
                    surf_inst = self.add_surface()
                    index_offset = len(surf_inst.vertices)

            for brush_idx, brush in enumerate(entity_inst.brushes):
                brush_geo = entity_geo_inst.brushes[brush_idx]
                if self.filter_brush(entity_idx, brush_idx):
                    continue

                if self.split_type == SurfaceSplitType.BRUSH:
                    index_offset = 0
                    surf_inst = self.add_surface()

                for face_idx, face in enumerate(brush.faces):
                    face_geo = brush_geo.faces[face_idx]
                    if self.filter_face(entity_idx, brush_idx, face_idx):
                        continue
                    for face_vertex in face_geo.vertices:
                        if entity_inst.spawn_type == EntitySpawnType.ENTITY or entity_inst.spawn_type == EntitySpawnType.GROUP:
                            face_vertex = face_vertex.vertex - entity_inst.center

                        surf_inst.vertices.appen(face_vertex)

                    for i in range(0, (len(face_geo.vertices) - 2) * 3):
                        surf_inst.indices.append(face_geo.indices[i] + index_offset)

                    index_offset += len(face_geo.vertices)

    def fetch(self):
        return self.out_surfaces

    def filter_entity(self, entity_idx):
        entity = self.map_data.get_entities()[entity_idx] # wtf?

        if self.entity_filter_idx != -1 and self.entity_filter_idx != entity_idx:
            return True

        return False

    def filter_brush(self, entity_idx, brush_idx):
        brush = self.map_data.get_entities()[entity_idx].brushes[brush_idx]
        if self.brush_filter_texture_idx != -1:
            fully_textured = True
            for face in brush.faces:
                if face.texture_idx != self.brush_filter_texture_idx:
                    fully_textured = False
                    break

            if fully_textured:
                return True

        for face in brush.faces:
            for layer in self.map_data.worldspawn_layers:
                if face.texture_idx == layer.texture_idx:
                    return self.filter_worldspawn_layers

        return False

    def filter_face(self, entity_idx, brush_idx, face_idx):
        entities = self.map_data.get_entities()
        face = entities[entity_idx].brushes[brush_idx].faces[face_idx]
        face_geo = self.map_data.entity_geo[entity_idx].brushes[brush_idx].faces[face_idx]

        if len(face_geo.vertices) < 3:
            return True

        if self.face_filter_texture_idx != -1 and face.texture_idx == self.face_filter_texture_idx:
            return True

        if self.texture_filter_idx != -1 and face.texture_idx != self.texture_filter_idx:
            return True

        return False

    def add_surface(self):
        surface = Surface()
        self.out_surfaces.append(surface)
        return surface

    def reset_state(self):
        self.out_surfaces.clear()

    def reset_params(self):
        self.split_type = SurfaceSplitType.NONE
        self.entity_filter_idx = -1
        self.texture_filter_idx = -1
        self.brush_filter_idx = -1
        self.face_filter_texture_idx = -1
        self.filter_worldspawn_layers = True