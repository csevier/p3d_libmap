from panda3d.core import Vec3, Mat4, Quat
from .entity_geometry import VertexTangent, VertexUV, FaceVertex, EntityGeometry, BrushGeometry, FaceGeometry
import math
import functools


class GeoGenerator:
    def __init__(self, map_data):
        self.map_data = map_data
        self.UP_VECTOR = Vec3(0, 0, 1)
        self.RIGHT_VECTOR = Vec3(0, 1, 0) # this will likely need changed for panda, forward is y.
        self.FORWARD_VECTOR = Vec3(1, 0, 0)
        self.smooth_normals = False
        self.wind_entity_idx = 0
        self.wind_brush_idx = 0
        self.wind_face_idx = 0
        self.wind_face_center = Vec3()
        self.wind_face_basis = Vec3()
        self.wind_face_normal = Vec3()
        self.EPSILON = 0.00001

    def sort_vertices_by_winding(self, lhs_in, rhs_in):
        face_inst = self.map_data.get_entities()[self.wind_entity_idx].brushes[self.wind_brush_idx].faces[self.wind_face_idx]
        face_geometry = self.map_data.entity_geo[self.wind_entity_idx].brushes[self.wind_brush_idx].faces[self.wind_face_idx]

        u = self.wind_face_basis.normalized()
        v = u.cross(self.wind_face_normal).normalized()

        local_lhs = lhs_in.vertex - self.wind_face_center
        lhs_pu = local_lhs.dot(u)
        lhs_pv = local_lhs.dot(v)

        local_rhs = rhs_in.vertex - self.wind_face_center
        rhs_pu = local_rhs.dot(u)
        rhs_pv = local_rhs.dot(v)

        lhs_angle = math.atan2(lhs_pv, lhs_pu)
        rhs_angle = math.atan2(rhs_pv, rhs_pu)

        if lhs_angle < rhs_angle:
            return 1
        elif lhs_angle > rhs_angle:
            return -1

        return 0

    def run(self):
        for e, ent_inst in enumerate(self.map_data.get_entities()):
            entity_geo_inst = EntityGeometry()
            self.map_data.entity_geo.append(entity_geo_inst)

            entity_geo_inst.brushes = []
            for b, brush_inst in enumerate(ent_inst.brushes):
                brush_geo_instance = BrushGeometry()
                entity_geo_inst.brushes.append(brush_geo_instance)
                brush_geo_instance.faces = []
                for f, face in enumerate(brush_inst.faces):
                    face_geo_inst = FaceGeometry()
                    brush_geo_instance.faces.append(face_geo_inst)

        for e, ent_inst in enumerate(self.map_data.get_entities()):
            ent_inst.center = Vec3()
            for b, brush_inst in enumerate(ent_inst.brushes):
                brush_inst.center = Vec3()
                vert_count = 0

                self.generate_brush_vertices(e, b)
                brush_geo_inst = self.map_data.entity_geo[e].brushes[b]
                for f, face in enumerate(brush_inst.faces):
                    face_geo_inst = brush_geo_inst.faces[f]
                    for v, vertex in enumerate(face_geo_inst.vertices):
                        brush_inst.center = brush_inst.center + vertex.vertex
                        vert_count += 1

                if vert_count > 0:
                    brush_inst.center = brush_inst.center / vert_count

                ent_inst.center = ent_inst.center + brush_inst.center

            if len(ent_inst.brushes) > 0:
                ent_inst.center = ent_inst.center / len(ent_inst.brushes)

        for e, entity_inst in enumerate(self.map_data.get_entities()):
            entity_geo_inst = self.map_data.entity_geo[e]
            for b, brush_inst in enumerate(entity_inst.brushes):
                brush_geo_inst = entity_geo_inst.brushes[b]
                for f, face_inst in enumerate(brush_inst.faces):
                    face_geo_inst = brush_geo_inst.faces[f]

                    if len(face_geo_inst.vertices) < 3:
                        continue

                    self.wind_entity_idx = e
                    self.wind_brush_idx = b
                    self.wind_face_idx = f

                    self.wind_face_basis = face_geo_inst.vertices[1].vertex - face_geo_inst.vertices[0].vertex
                    self.wind_face_center = Vec3()
                    self.wind_face_normal = face_inst.plane_normal

                    for v, vertex in enumerate(face_geo_inst.vertices):
                        self.wind_face_center = self.wind_face_center + vertex.vertex

                    self.wind_face_center = self.wind_face_center / len(face_geo_inst.vertices)
                    cmp = functools.cmp_to_key(self.sort_vertices_by_winding)
                    face_geo_inst.vertices.sort(key=cmp)
                    self.wind_entity_idx = 0

        for e, entity_inst in enumerate(self.map_data.get_entities()):
            entity_geo_inst = self.map_data.entity_geo[e]
            for b, brush_inst in enumerate(entity_inst.brushes):
                brush_geo_inst = entity_geo_inst.brushes[b]
                for f, face in enumerate(brush_inst.faces):
                    face_geo_inst = brush_geo_inst.faces[f]
                    if len(face_geo_inst.vertices) < 3:
                        continue

                    face_geo_inst.indices = []
                    for i in range(len(face_geo_inst.vertices) - 2): # this algo is fucked, fixed this if you get here.
                        face_geo_inst.indices.append(0)
                        face_geo_inst.indices.append(i + 1)
                        face_geo_inst.indices.append(i + 2)

    def generate_brush_vertices(self, entity_idx, brush_idx):
        entity_inst = self.map_data.get_entities()[entity_idx]
        brush_inst = entity_inst.brushes[brush_idx]

        for f0, face_inst0 in enumerate(brush_inst.faces):
            for f1, face_inst1 in enumerate(brush_inst.faces):
                for f2, face_inst2 in enumerate(brush_inst.faces):
                    is_intersecting, vertex = self.intersect_faces(face_inst0, face_inst1, face_inst2)
                    if is_intersecting:
                        if self.vertex_in_hull(brush_inst.faces, vertex):
                            face_inst = face_inst0
                            face_geo = self.map_data.entity_geo[entity_idx].brushes[brush_idx].faces[f0]

                            normal = Vec3()
                            phong_property = self.map_data.get_entity_property(entity_idx, "_phong")
                            phong = phong_property is not None and phong_property == "1"

                            if phong:
                                phong_angle_property = self.map_data.get_entity_property(entity_idx, "_phong_angle")
                                if phong_angle_property:
                                    threshold = math.cos((float(phong_angle_property) + 0.01) * 0.0174533)
                                    normal = face_inst0.plane_normal
                                    if face_inst0.plane_normal.dot(face_inst1.plane_normal) > threshold:
                                        normal = normal + face_inst1
                                    if face_inst0.plane_normal.dot(face_inst2.plane_normal) > threshold:
                                        normal = normal + face_inst2

                                    normal = normal.normalized()
                                else:
                                    normal = face_inst0.plane_normal + (face_inst1.plane_normal + face_inst2.plane_normal)
                                    normal = normal.normalized()
                            else:
                                normal = face_inst.plane_normal

                            texture = self.map_data.get_texture(face_inst.texture_idx)
                            uv = VertexUV()
                            if face_inst.is_valve_uv:
                                uv = self.get_valve_uv(vertex, face_inst, texture.width, texture.height)
                            else:
                                uv = self.get_standard_uv(vertex, face_inst, texture.width, texture.height)

                            tangent = VertexTangent()
                            if face_inst.is_valve_uv:
                                tangent = self.get_valve_tangent(face_inst)
                            else:
                                tangent = self.get_standard_tangent(face_inst)

                            unique_vertex = True
                            duplicate_index = -1

                            for v, comp_vertex in enumerate(face_geo.vertices):
                                if (vertex - comp_vertex.vertex).length() < self.EPSILON:
                                    unique_vertex = False
                                    duplicate_index = v
                                    break

                            if unique_vertex:
                                face_geo.vertices.append(FaceVertex(vertex=vertex, normal=normal, uv=uv, tangent=tangent))
                            elif phong:
                                face_geo.vertices.append(face_geo.vertices[duplicate_index].normal + normal)

    def intersect_faces(self, f0, f1, f2):
        o_vertex = Vec3()
        normal0 = f0.plane_normal
        normal1 = f1.plane_normal
        normal2 = f2.plane_normal

        denom = normal0.cross(normal1).dot(normal2)

        if denom < self.EPSILON:
            return False, o_vertex

        a = normal1.cross(normal2) * f0.plane_dist
        b = normal2.cross(normal0) * f1.plane_dist
        c = normal0.cross(normal1) * f2.plane_dist
        d = a + b
        e = d + c
        o_vertex = e / denom

        return True, o_vertex

    def vertex_in_hull(self, faces, vertex):
        for face in faces:
            proj = face.plane_normal.dot(vertex)
            a = proj > face.plane_dist
            c = abs(face.plane_dist - proj)
            b = c > 1
            if a and b:
                return False

        return True

    def get_standard_uv(self, vertex, face, texture_width, texture_height):
        uv_out = VertexUV()

        du = abs(face.plane_normal.dot(self.UP_VECTOR))
        dr = abs(face.plane_normal.dot(self.RIGHT_VECTOR))
        df = abs(face.plane_normal.dot(self.FORWARD_VECTOR))

        if du >= dr and du >= df:
            uv_out = VertexUV(vertex.x, -vertex.y)
        elif dr >= du and dr >= df:
            uv_out = VertexUV(vertex.x, -vertex.z)
        elif df >= du and df >= dr:
            uv_out = VertexUV(vertex.y, -vertex.z)

        angle = math.radians(face.uv_extra.rot)
        rotated = VertexUV()
        rotated.u = uv_out.u * math.cos(angle) - uv_out.v * math.sin(angle)
        rotated.v = uv_out.u * math.sin(angle) + uv_out.v * math.cos(angle)
        uv_out = rotated

        uv_out.u /= texture_width
        uv_out.v /= texture_height

        uv_out.u /= face.uv_extra.scale_x
        uv_out.v /= face.uv_extra.scale_y

        uv_out.u += face.uv_standard.u / texture_width
        uv_out.v += face.uv_standard.v / texture_height
        uv_out.v *= -1

        return uv_out

    def get_valve_uv(self, vertex, face, texture_width, texture_height):
        uv_out = VertexUV()
        u_axis = face.uv_valve.u.axis
        u_shift = face.uv_valve.u.offset
        v_axis = face.uv_valve.v.axis
        v_shift = face.uv_valve.v.offset

        uv_out.u = u_axis.dot(vertex)
        uv_out.v = v_axis.dot(vertex)

        uv_out.u /= texture_width
        uv_out.v /= texture_height

        uv_out.u /= face.uv_extra.scale_x
        uv_out.v /= face.uv_extra.scale_y

        uv_out.u += u_shift / texture_width
        uv_out.v += v_shift / texture_height

        return uv_out

    def get_standard_tangent(self, face):
        tangent_out = VertexTangent()
        du = face.plane_normal.dot(self.UP_VECTOR)
        dr = face.plane_normal.dot(self.RIGHT_VECTOR)
        df = face.plane_normal.dot(self.FORWARD_VECTOR)

        dua = abs(du)
        dra = abs(dr)
        dfa = abs(df)

        u_axis = None
        v_sign = 0

        if dua >= dra and dua >= dfa:
            u_axis = self.FORWARD_VECTOR
            v_sign = self.sign(du)
        elif dra >= dua and dra >= dfa:
            u_axis = self.FORWARD_VECTOR
            v_sign = -self.sign(dr)
        elif dfa >= dua and dfa >= dra:
            u_axis = self.RIGHT_VECTOR
            v_sign = self.sign(df)

        v_sign *= self.sign(face.uv_extra.scale_y)
        quat = Quat()
        quat.setFromAxisAngle(-face.uv_extra.rot * v_sign, face.plane_normal)
        u_axis = quat.xform(u_axis)

        tangent_out.x = u_axis.x
        tangent_out.y = u_axis.y
        tangent_out.z = u_axis.z
        tangent_out.w = v_sign

        return tangent_out

    def get_valve_tangent(self, face):
        tangent_out = VertexTangent()

        u_axis = face.uv_valve.u.axis.normalized()
        v_axis = face.uv_valve.v.axis.normalized()

        v_sign = -self.sign(face.plane_normal.cross(u_axis).dot(v_axis))
        tangent_out.x = u_axis.x
        tangent_out.y = u_axis.y
        tangent_out.z = u_axis.z
        tangent_out.w = v_sign

        return tangent_out

    def sign(self, v):
        if v > 0:
            return 1
        elif v < 0:
            return -1

        return 0

    def get_entities(self):
        return self.map_data.entity_geo

    def get_brush_vertex_count(self, entity_idx, brush_idx):
        brush = self.map_data.get_entities()[entity_idx].brushes[brush_idx]
        brush_geo = self.map_data.entity_geo[entity_idx].brushes[brush_idx]
        vertex_count = 0
        for face_idx, face in enumerate(brush.faces):
            face_geo = brush_geo.faces[face_idx]
            vertex_count += len(face_geo.vertices)

        return vertex_count

    def get_brush_index_count(self, entity_idx, brush_idx):
        brush = self.map_data.get_entities()[entity_idx].brushes[brush_idx]
        brush_geo = self.map_data.entity_geo[entity_idx].brushes[brush_idx]
        index_count = 0
        for face_idx, face in enumerate(brush.faces):
            face_geo = brush_geo.faces[face_idx]
            index_count += len(face_geo.indices)

        return index_count

