"""Generic job: open CAP_STAGE, optionally spawn assets, play timeline, capture frames."""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import capture_common as cc  # noqa: E402
import omni.timeline  # noqa: E402


async def main():
    try:
        stage = await cc.open_stage(os.environ["CAP_STAGE"])
        cc.apply_stage_camera(stage)
        n_spawn = int(os.environ.get("CAP_SPAWN", "0"))
        if n_spawn:
            import random
            random.seed(7)
            from ellies.python_ui_extension.extension import MyExtension
            ext = MyExtension()
            ext.on_startup("capture")
            for i in range(n_spawn):
                ext.spawn_from_asset_map(ext.cardbox_assets if i % 2 else ext.pallet_assets)
        await cc.wait_render(int(os.environ.get("CAP_SETTLE", "300")))
        tl = omni.timeline.get_timeline_interface()
        for n, t in enumerate(float(x) for x in os.environ.get("CAP_FRAMES", "0").split(",")):
            if t > 0:
                tl.set_current_time(t)
                tl.play()
                await cc.pump(int(t * 60))
                tl.pause()
                await cc.pump(30)
            await cc.grab(os.environ["CAP_OUT"].replace("{n}", str(n)))
        cc.finish(0)
    except Exception as e:  # report and exit so the runner never hangs
        import traceback
        traceback.print_exc()
        cc.finish(1)


asyncio.ensure_future(main())
