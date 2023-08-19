
## Info
Port of https://github.com/QodotPlugin/libmap for Panda3d.

This module will import generic trenchbroom map files into panda3d and generate collision for solid brush geometry.

Note: It does not yet support quake maps because the textures are packe in wads. This is actually pretty straightforward to implement if youd like, I just had no need for it. I marked where to add the code you if you want it. 


## Usage:
you can use any node path where base.render is, this is the node path the map will be parented to.
```python
load_map("test_level9.map", base.render)
```

To skip collision generation:
```python
load_map("test_level9.map", base.render, generate_collisions=False)
```

By default Trenchbroom sets the path to textures depending on your game settings, this is stored in the map file as _tb_textures. p3d_libmap will use this but you can override this behavior:
```python
load_map("test_level9.map", base.render, override_texture_location="/path/to/my/textures")
```


![Alt text](/images/trenchbroom_showcase.png?raw=true "Example")


## Installation:
I dont have this packaged in a pip yet. Its coming!