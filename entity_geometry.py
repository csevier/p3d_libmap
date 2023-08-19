from panda3d.core import Vec3


class VertexUV:
    def __init__(self, u=0.0, v=0.0):
        self.u = u
        self.v = v


class VertexTangent:
    def __init__(self, x=0.0, y=0.0, z=0.0, w=0.0):
        self.x = x
        self.y = y
        self.z = z
        self.w = w


class FaceVertex:
    def __init__(self, vertex=None, normal=None, uv=None, tangent=None):
        if vertex is None:
            self.vertex = Vec3()
        else:
            self.vertex = vertex
        if normal is None:
            self.normal = Vec3()
        else:
            self.normal = normal

        if uv is None:
            self.uv = VertexUV()
        else:
            self.uv = uv
        if tangent is None:
            self.tangent = VertexTangent()
        else:
            self.tangent = tangent


class FaceGeometry:
    def __init__(self, vertices=None, indices=None):
        if vertices is None:
            self.vertices = []
        else:
            self.vertices = vertices
        if indices is None:
            self.indices = []
        else:
            self.indices = indices


class BrushGeometry:
    def __init__(self, faces=None):
        if faces is None:
            self.faces = []
        else:
            self.faces = faces


class EntityGeometry:
    def __init__(self, brushes=None):
        if brushes is None:
            self.brushes = []
        else:
            self.brushes = brushes



