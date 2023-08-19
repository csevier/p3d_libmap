from .map_parser import MapParser
from .geo_generator import GeoGenerator
from panda3d.core import (GeomVertexFormat,
                          GeomVertexData,
                          Geom,
                          GeomVertexWriter,
                          GeomTriangles,
                          GeomNode,
                          CollisionNode,
                          GeomVertexReader,
                          CollisionPolygon,
                          TransformState)


def load_map(map_name, parent, generate_collisions=True, override_texture_location=None):
    mp = MapParser()
    mp.parser_load(f"./mapquest/test_maps/{map_name}")
    mp.map_data.load_texture_data(override_texture_location)
    geo_gen = GeoGenerator(mp.map_data)
    geo_gen.run()
    print("loaded starting panda conversion")
    for entity_idx, entity_geo in enumerate(mp.map_data.entity_geo):
        for brush_idx, brush in enumerate(entity_geo.brushes):
            for face_idx, face in enumerate(brush.faces):
                vdata = GeomVertexData('name', GeomVertexFormat.getV3n3t2(), Geom.UHStatic)
                vertex = GeomVertexWriter(vdata, 'vertex')
                normal = GeomVertexWriter(vdata, 'normal')
                texcoord = GeomVertexWriter(vdata, 'texcoord')
                prim = GeomTriangles(Geom.UHStatic)
                for vert in face.vertices:
                    vertex.addData3(vert.vertex.x, vert.vertex.y, vert.vertex.z)
                    normal.addData3(vert.normal.x, vert.normal.y, vert.normal.z)
                    texcoord.addData2(vert.uv.u, vert.uv.v)
                for indice in face.indices:
                    prim.addVertex(indice)

                prim.closePrimitive()
                geom = Geom(vdata)
                geom.addPrimitive(prim)
                node = GeomNode('brush_face')
                node.addGeom(geom)
                texture_id = mp.map_data.get_entities()[entity_idx].brushes[brush_idx].faces[face_idx].texture_idx
                texture = mp.map_data.get_texture(texture_id)
                np = parent.attachNewNode(node)
                # set texture
                np.setTexture(texture.p3d_texture, 1)
                np.setScale(0.01)
                collision_node = CollisionNode(node.name)
                collision_mesh = np.attach_new_node(collision_node)
                transform = TransformState.make_identity()
                min = None
                max = None
                for geom in node.get_geoms():
                    if geom.primitive_type != Geom.PT_polygons:
                        continue

                    vertex = GeomVertexReader(geom.get_vertex_data(), 'vertex')

                    geom = geom.decompose()
                    geom.transform_vertices(transform.get_mat())

                    for prim in geom.get_primitives():
                        for i in range(0, prim.get_num_vertices(), 3):
                            vertex.set_row(prim.get_vertex(i))
                            v1 = vertex.get_data3()
                            vertex.set_row(prim.get_vertex(i + 1))
                            v2 = vertex.get_data3()
                            vertex.set_row(prim.get_vertex(i + 2))
                            v3 = vertex.get_data3()
                            origin = (v1 + v2 + v3) * (1.0 / 3)
                            if min is None:
                                min = origin
                                max = origin
                            else:
                                min = min.fmin(origin)
                                max = max.fmax(origin)
                            solid = CollisionPolygon(v1, v2, v3)
                            collision_node.add_solid(solid)
