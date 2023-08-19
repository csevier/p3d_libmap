Port of https://github.com/QodotPlugin/libmap for Panda3d.

This module will import trenchbroom map files into panda3d and generate collision for solid brush geometry.


Use:
you can use any node path where base.render is, this is the node path the map will be parented to.
load_map("test_level9.map", base.render)

To skip collision generation:
load_map("test_level9.map", base.render, generate_collisions=False)

By default Trenchbroom sets the path to textures depending on your game settings, this is stored in the map file as _tb_textures. p3d_libmap will use this but you can override this behavior:
load_map("test_level9.map", base.render, override_texture_location="/path/to/my/textures")


![Alt text](/images/trenchbroom_showcase.png?raw=true "Example")


Note:
I dont have this packaged in a pip yet. Its coming!