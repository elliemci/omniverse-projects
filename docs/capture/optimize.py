"""Palette-quantize raw captures into docs/media/<subproject>/ (PNG, 256 colours, <= 8 MB)."""
import os, sys
from PIL import Image

MAP = {
    "intro_factory_lite": "intro/factory-lite.png",
    "intro_factory_layout": "intro/factory-layout.png",
    "ext_before_spawn": "python-extension/before-spawn.png",
    "ext_after_spawn": "python-extension/after-spawn.png",
    "dt_conveyor_physics_0": "digital-twin/conveyor-start.png",
    "dt_conveyor_physics_1": "digital-twin/conveyor-later.png",
    "dt_spawned_boxes": "digital-twin/spawned-boxes.png",
}
raw, out = sys.argv[1], sys.argv[2]
for src, dst in MAP.items():
    im = Image.open(os.path.join(raw, src + ".png")).convert("RGB")
    q = im.quantize(256, method=Image.MEDIANCUT, dither=Image.FLOYDSTEINBERG)
    path = os.path.join(out, dst)
    q.save(path, optimize=True)
    size = os.path.getsize(path)
    assert size <= 8 * 1024 * 1024, path
    print(f"{dst}: {size/1024:.0f} KB")
