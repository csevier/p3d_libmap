from panda3d.core import Vec3


class Brush:
    def __init__(self, faces=None, center=None):
        if faces is None:
            self.faces = []
        else:
            self.faces = faces
        if center is None:
            self.center = Vec3()
        else:
            self.center = center

