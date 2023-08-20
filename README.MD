
## Info
Port of https://github.com/QodotPlugin/libmap for Panda3d.

This module will import generic trenchbroom map files into panda3d and generate collision for solid brush geometry.

Note: It does not yet support quake maps because the textures are packed in wad files. Thats the only issue. This is actually pretty straightforward to implement if youd like, I just had no need for it. I marked where to add the code you if you want it. 

## Supports:
* Solid Entities
* Brushes
* Textures
* Collision Generation
* Inserts into panda3d scene graph

## Major Needs
* A proper panda3d base .fgd
* Point entity support
    - Currently point entities are indeed parse and you can write any custom algorithm you need by just looping it. (see properties example). Its just not automatic until we come up with a great base panda3d fgd.



## Usage:
you can use any node path where base.render is, this is the node path the map will be parented to.
```python
map_data = load_map("<path>/<to>/<my>.map", base.render)
```

To skip collision generation:
```python
map_data = load_map("<path>/<to>/<my>.map", base.render, generate_collisions=False)
```

By default Trenchbroom sets the path to textures depending on your game settings, this is stored in the map file as _tb_textures. p3d_libmap will use this but you can override this behavior:
```python
map_data = load_map("<path>/<to>/<my>.map", base.render, override_texture_location="/path/to/my/textures")
```

All data is found in the map data object:
```python
map_data.entities # all entites objects
map_data.entity_geo # all generated geometry data
map_data.textures # all textures
map_data.worldspawn_layer # all worldspawn layers.
```

Get an entity properties from the property attribute:
```python
# all lights
for entity in map_data.entities:
    if entity.properties.get("classname")  == "light":
        # this would be a light entity should your fgd be formatted that way. This is how qodot defines lights.
```

## Showcase

![Alt text](/images/trenchbroom_showcase.png?raw=true "Example")


## Installation:
I dont have this packaged in a pip yet. Its coming!