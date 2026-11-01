"""Shared helpers for headless viewport captures (run inside Kit via --exec).

Reads its job from environment variables so the project files stay untouched:
  CAP_STAGE   absolute path of the USD stage to open
  CAP_OUT     output PNG path (a "{n}" placeholder is replaced per frame)
  CAP_FRAMES  comma list of timeline seconds to capture (default "0")
  CAP_SPAWN   number of random spawns via ellies.python_ui_extension (default 0)
"""
import asyncio
import os

import omni.kit.app
import omni.timeline
import omni.usd
from omni.kit.viewport.utility import capture_viewport_to_file, get_active_viewport
from pxr import Gf, Sdf, Usd, UsdGeom


async def pump(n=1):
    app = omni.kit.app.get_app()
    for _ in range(n):
        await app.next_update_async()


async def open_stage(path):
    ctx = omni.usd.get_context()
    await ctx.open_stage_async(path)
    await pump(10)
    return ctx.get_stage()


def apply_stage_camera(stage):
    """Use the Perspective camera the scene author saved in customLayerData."""
    data = stage.GetRootLayer().customLayerData.get("cameraSettings", {})
    persp = data.get("Perspective")
    if not persp:
        return False
    cam = UsdGeom.Camera.Get(stage, "/OmniverseKit_Persp")
    if not cam:
        return False
    eye, tgt = Gf.Vec3d(*persp["position"]), Gf.Vec3d(*persp["target"])
    m = Gf.Matrix4d(1).SetLookAt(eye, tgt, Gf.Vec3d(0, 0, 1)).GetInverse()
    xf = UsdGeom.Xformable(cam.GetPrim())
    xf.ClearXformOpOrder()
    xf.AddTransformOp().Set(m)
    return True


async def wait_render(frames=240):
    # RTX needs many updates to stream textures/materials before a capture is clean.
    await pump(frames)


async def grab(out_path):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    vp = get_active_viewport()
    cap = capture_viewport_to_file(vp, out_path)
    await cap.wait_for_result(completion_frames=30)
    await pump(5)


def finish(code=0):
    omni.kit.app.get_app().post_quit(code)
    # Headless RTX shutdown can hang; force exit after a short grace period.
    import threading
    threading.Timer(15, lambda: os._exit(code)).start()
