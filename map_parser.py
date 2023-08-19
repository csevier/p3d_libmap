from .map_data import MapData
from .entity import Entity, EntitySpawnType
from .face import Face
from .brush import Brush
from enum import Enum


class ParseScope(Enum):
    FILE = 0
    COMMENT = 1
    ENTITY = 2
    PROPERTY_VALUE = 3
    BRUSH = 4
    PLANE_0 = 5
    PLANE_1 = 6
    PLANE_2 = 7
    TEXTURE = 8
    U = 9
    V = 10
    VALVE_U = 11
    VALVE_V = 12
    ROT = 13
    U_SCALE = 14
    V_SCALE = 15


class MapParser:
    def __init__(self):
        self.map_data = MapData()
        self.scope = ParseScope.FILE
        self.comment = False
        self.entity_idx = -1
        self.brush_idx = -1
        self.face_idx = -1
        self.component_idx = 0
        self.current_property = ""
        self.current_key = ""
        self.valve_uvs = False
        self.current_face = None
        self.current_brush = None
        self.current_entity = None
        self.buffer = ""

    def reset_current_face(self):
        self.current_face = Face()

    def reset_current_brush(self):
        self.current_brush = Brush()

    def reset_current_entity(self):
        self.current_entity = Entity()

    def parser_load(self, map_file):
        self.reset_current_face()
        self.reset_current_brush()
        self.reset_current_entity()
        self.scope = ParseScope.FILE
        self.comment = False
        self.entity_idx = -1
        self.brush_idx = -1
        self.face_idx = -1
        self.component_idx = 0
        self.valve_uvs = False

        with open(map_file, "r") as map:
            c = 0
            while True:
                c = map.read(1)
                if not c:
                    print("End of map file")
                    break
                if c == "\n":
                    self.token()
                    self.buffer = ""
                    self.newline()
                elif c.isspace():
                    self.token()
                    self.buffer = ""
                else:
                   self.buffer += c

    def set_scope(self, scope):
        # match scope:
        #     case ParseScope.FILE:
        #         print("Switching to FILE scope.")
        #     case ParseScope.ENTITY:
        #         print("Switching to ENTITY scope.", self.entity_idx)
        #     case ParseScope.PROPERTY_VALUE:
        #         print("Switching to PROPERTY_VALUE scope.")
        #     case ParseScope.BRUSH:
        #         print("Switching to BRUSH scope.", self.brush_idx)
        #     case ParseScope.PLANE_0:
        #         print("Switching to PLANE_0 scope.", self.face_idx)
        #     case ParseScope.PLANE_1:
        #         print("Switching to PLANE_1 scope.", self.face_idx)
        #     case ParseScope.PLANE_2:
        #         print("Switching to PLANE_2 scope.", self.face_idx)
        #     case ParseScope.TEXTURE:
        #         print("Switching to TEXTURE scope.")
        #     case ParseScope.U:
        #         print("Switching to U scope.")
        #     case ParseScope.V:
        #         print("Switching to V scope.")
        #     case ParseScope.VALVE_U:
        #         print("Switching to VALVE_U scope.")
        #     case ParseScope.VALVE_V:
        #         print("Switching to VALVE_V scope.")
        #     case ParseScope.ROT:
        #         print("Switching to ROT scope.")
        #     case ParseScope.U_SCALE:
        #         print("Switching to U_SCALE scope.")
        #     case ParseScope.V_SCALE:
        #         print("Switching to V_SCALE scope.")

        self.scope = scope

    def token(self):

        if self.comment:
            return

        if self.buffer == "//":
            self.comment = True
            return

        match self.scope:
            case ParseScope.FILE:
                if self.buffer == "{":
                    self.entity_idx += 1
                    self.brush_idx = -1
                    self.set_scope(ParseScope.ENTITY)
            case ParseScope.ENTITY:
                if self.buffer[0] == '"':
                    self.current_entity.properties[self.buffer.strip('"')] = ""
                    self.current_key = self.buffer.strip('"')
                    self.set_scope(ParseScope.PROPERTY_VALUE)
                elif self.buffer == "{":
                    self.brush_idx += 1
                    self.face_idx = -1
                    self.set_scope(ParseScope.BRUSH)
                elif self.buffer == "}":
                    self.commmit_entity()
                    self.set_scope(ParseScope.FILE)
            case ParseScope.PROPERTY_VALUE:
                is_first = self.buffer[0] == '"'
                is_last = self.buffer[len(self.buffer) - 1] == '"'
                if is_first:
                    if self.current_property != "":
                        self.current_property = ""

                self.current_property += " "
                self.current_property += self.buffer.strip('"')

                if is_last:
                    self.current_entity.properties[self.current_key] = self.current_property.strip(' ')
                    self.current_key = ""
                    self.set_scope(ParseScope.ENTITY)


            case ParseScope.BRUSH:
                if self.buffer == "(":
                    self.face_idx += 1
                    self.component_idx = 0
                    self.set_scope(ParseScope.PLANE_0)
                elif self.buffer == "}":
                    self.commit_brush()
                    self.set_scope(ParseScope.ENTITY)
            case ParseScope.PLANE_0:
                if self.buffer == ")":
                    self.component_idx = 0
                    self.set_scope(ParseScope.PLANE_1)
                else:
                    match self.component_idx:
                        case 0:
                            self.current_face.plane_points.v0.x = float(self.buffer)
                        case 1:
                            self.current_face.plane_points.v0.y = float(self.buffer)
                        case 2:
                            self.current_face.plane_points.v0.z = float(self.buffer)
                    self.component_idx += 1
            case ParseScope.PLANE_1:
                if self.buffer == "(":
                    return
                if self.buffer == ")":
                    self.component_idx = 0
                    self.set_scope(ParseScope.PLANE_2)
                else:
                    match self.component_idx:
                        case 0:
                            self.current_face.plane_points.v1.x = float(self.buffer)
                        case 1:
                            self.current_face.plane_points.v1.y = float(self.buffer)
                        case 2:
                            self.current_face.plane_points.v1.z = float(self.buffer)
                    self.component_idx += 1
            case ParseScope.PLANE_2:
                if self.buffer == "(":
                    return
                if self.buffer == ")":
                    self.component_idx = 0
                    self.set_scope(ParseScope.TEXTURE)
                else:
                    match self.component_idx:
                        case 0:
                            self.current_face.plane_points.v2.x = float(self.buffer)
                        case 1:
                            self.current_face.plane_points.v2.y = float(self.buffer)
                        case 2:
                            self.current_face.plane_points.v2.z = float(self.buffer)
                    self.component_idx += 1
            case ParseScope.TEXTURE:
                self.current_face.texture_idx = self.map_data.register_texture(self.buffer)
                self.set_scope(ParseScope.U)
            case ParseScope.U:
                if self.buffer == "[":
                    self.valve_uvs = True
                    self.component_idx = 0
                    self.set_scope(ParseScope.VALVE_U)
                else:
                    self.valve_uvs = False
                    self.current_face.uv_standard.u = float(self.buffer)
                    self.set_scope(ParseScope.V)
            case ParseScope.V:
                self.current_face.uv_standard.v = float(self.buffer)
                self.set_scope(ParseScope.ROT)
            case ParseScope.VALVE_U:
                if self.buffer == "]":
                    self.component_idx = 0
                    self.set_scope(ParseScope.VALVE_V)
                else:
                    match self.component_idx:
                        case 0:
                            self.current_face.uv_valve.u.axis.x = float(self.buffer)
                        case 1:
                            self.current_face.uv_valve.u.axis.y = float(self.buffer)
                        case 2:
                            self.current_face.uv_valve.u.axis.z = float(self.buffer)
                        case 3:
                            self.current_face.uv_valve.u.offset = float(self.buffer)
                    self.component_idx += 1
            case ParseScope.VALVE_V:
                if self.buffer == "[":
                    return
                elif self.buffer == "]":
                    self.set_scope(ParseScope.ROT)
                else:
                    match self.component_idx:
                        case 0:
                            self.current_face.uv_valve.v.axis.x = float(self.buffer)
                        case 1:
                            self.current_face.uv_valve.v.axis.y = float(self.buffer)
                        case 2:
                            self.current_face.uv_valve.v.axis.z = float(self.buffer)
                        case 3:
                            self.current_face.uv_valve.v.offset = float(self.buffer)
                    self.component_idx += 1
            case ParseScope.ROT:
                self.current_face.uv_extra.rot = float(self.buffer)
                self.set_scope(ParseScope.U_SCALE)
            case ParseScope.U_SCALE:
                self.current_face.uv_extra.scale_x = float(self.buffer)
                self.set_scope(ParseScope.V_SCALE)
            case ParseScope.V_SCALE:
                self.current_face.uv_extra.scale_y = float(self.buffer)
                self.commit_face()
                self.set_scope(ParseScope.BRUSH)


    def newline(self):
        if self.comment:
            self.comment = False

    def commit_face(self):
        v0v1 = self.current_face.plane_points.v1 - self.current_face.plane_points.v0
        v1v2 = self.current_face.plane_points.v2 - self.current_face.plane_points.v1
        self.current_face.plane_normal = v1v2.cross(v0v1).normalized()
        self.current_face.plane_dist = self.current_face.plane_normal.dot(self.current_face.plane_points.v0)
        self.current_face.is_valve_uv = self.valve_uvs
        self.current_brush.faces.append(self.current_face)
        self.reset_current_face()

    def commit_brush(self):
        self.current_entity.brushes.append(self.current_brush)
        self.reset_current_brush()

    def commmit_entity(self):
        self.current_entity.spawn_type = EntitySpawnType.ENTITY
        self.map_data.entities.append(self.current_entity)
        self.reset_current_entity()
