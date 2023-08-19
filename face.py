from panda3d.core import Vec3


class FacePoints:
    def __init__(self, v0=None, v1=None, v2=None):
        if v0 is None:
            self.v0 = Vec3()
        else:
            self.v0 = v0
        if v1 is None:
            self.v1 = Vec3()
        else:
            self.v1 = v1
        if v2 is None:
            self.v2 = Vec3()
        else:
            self.v2 = v2

class StandardUV:
    def __init__(self, u=0.0, v=0.0):
        self.u = u
        self.v = v


class ValveTextureAxis:
    def __init__(self, axis=None, offset=0.0):
        if axis is None:
            self.axis = Vec3()
        else:
            self.axis = axis
        self.offset = offset


class ValveUV:
    def __init__(self, valve_texture_u=None, valve_texture_v=None):
        if valve_texture_u is None:
            self.u = ValveTextureAxis()
        else:
            self.u = valve_texture_u

        if valve_texture_v is None:
            self.v = ValveTextureAxis()
        else:
            self.v = valve_texture_v


class FaceUVExtra:
    def __init__(self, rot=0.0, scale_x=0.0, scale_y=0.0):
        self.rot = rot
        self.scale_x = scale_x
        self.scale_y = scale_y


class Face:
    def __init__(self, plane_points=None,
                 plane_normal=None,
                 plane_dist=0.0,
                 texture_idx=0,
                 is_valve_uv=False,
                 uv_valve=None,
                 uv_standard=None,
                 uv_extra=None):
        if plane_points is None:
            self.plane_points = FacePoints()
        else:
            self.plane_points = plane_points
        if plane_normal is None:
            self.plane_normal = Vec3()
        else:
            self.plane_normal = plane_normal

        self.plane_dist = plane_dist
        self.texture_idx = texture_idx
        self.is_valve_uv = is_valve_uv

        if uv_valve is None:
            self.uv_valve = ValveUV()
        else:
            self.uv_valve = uv_valve
        if uv_standard is None:
            self.uv_standard = StandardUV()
        else:
            self.uv_standard = uv_standard

        if uv_extra is None:
            self.uv_extra = FaceUVExtra()
        else:
            self.uv_extra = uv_extra
