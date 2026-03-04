# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

import omni.ext
import omni.ui as ui
import omni.kit.ui

# packages for functionality to extension command code
import omni
import omni.kit.commands
import omni.usd
from pxr import Sdf

# packages for spawning randomly chosen types of boxes
import random
from pxr import Gf, UsdGeom


# Functions and vars are available to other extensions as usual in python:
# `ellies.python_ui_extension.some_public_function(x)`
def some_public_function(x: int):
    """This is a public function that can be called from other extensions."""
    print(f"[ellies.python_ui_extension] some_public_function was called with {x}")
    return x ** x

# Any class derived from `omni.ext.IExt` in the top level module (defined in
# `python.modules` of `extension.toml`) will be instantiated when the extension
# gets enabled, and `on_startup(ext_id)` will be called. Later when the
# extension gets disabled on_shutdown() is called.
class MyExtension(omni.ext.IExt):

    def spawn_from_asset_map(self, asset_map: dict):
        """ Generic spawn function with random transformation of the selected assets """

        stage = omni.usd.get_context().get_stage()

        if not stage:
            print("No stage found")
            return

        # asset random choice
        chosen_asset = random.choice(list(asset_map.keys()))
        asset_path = asset_map[chosen_asset]

        base_path = f"/World/{chosen_asset}"
        prim_path = omni.usd.get_stage_next_free_path(stage, base_path, False)

        # create an empty transform prim
        xform = UsdGeom.Xform.Define(stage, prim_path)
        prim = xform.GetPrim()

        # add reference, which is the actual content of the Xform container
        prim.GetReferences().AddReference(asset_path)

        # random translation
        tx = random.uniform(-200, 200)
        ty = random.uniform(-200, 200)
        xform.AddTranslateOp().Set(Gf.Vec3f(tx, ty, 0))

        # random rotation around Z-axis only
        rot_z = random.uniform(0, 360)
        xform.AddRotateZOp().Set(rot_z)

        # random scale
        scale_value = random.uniform(0.8, 1.5)
        xform.AddScaleOp().Set(Gf.Vec3f(scale_value, scale_value, scale_value))

        print(f"Spawned {chosen_asset} at {prim_path}")

    # ext_id is current Extension id. It can be used with Extension manager to query additional information, like where this Extension is located on filesystem.
    def on_startup(self, ext_id):

        print(">>> Ellie's Extension Loaded Successfully <<<")

        # Initialize some properties
        self._count = 0
        self._window = None
        self._menu = None

        # Create a menu item inside the already existing "Window" menu.
        editor_menu = omni.kit.ui.get_editor_menu()
        if editor_menu:
            self._menu = editor_menu.add_item("Window/Ellie's Window", self.show_window, toggle=True, value=False)

        # define asset maps for the randomly transformed spawned cardboards or pallets
        self.cardbox_assets = {
            "Cardbox_A1": "http://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/ArchVis/Industrial/Containers/Cardboard/Cardbox_A1.usd",
            "Cardbox_A2": "http://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/ArchVis/Industrial/Containers/Cardboard/Cardbox_A2.usd",
            "Cardbox_A3": "http://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/ArchVis/Industrial/Containers/Cardboard/Cardbox_A3.usd",
}

        self.pallet_assets = {
            "Pallets_A1": "http://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/ArchVis/Industrial/Piles/Pallets_A1.usd",
            "Pallets_A2": "http://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/ArchVis/Industrial/Piles/Pallets_A2.usd",
            "Pallers_A3": "http://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/ArchVis/Industrial/Piles/Pallets_A3.usd"
        }

    def on_shutdown(self):
        # clear the extension on shut down
        self._window = None
        self._menu = None

    def show_window(self, menu_path: str, visible: bool):
        """ Function that tells the application what to do with the
            extention whilie it is visible and sets the window size """

        if visible:
            # Create window
            self._window = ui.Window("Ellie's Window", width=300, height=300)

            with self._window.frame:

                # Omni UI uses context manager to define layout containers:

                # Window
                #   └── VStack
                #   ├── Button 1
                #   ├── Button 2
                #   └── HStack
                #           ├── Button 3
                #           └── Button 4
                # rendering
                # [Button 1]
                # [Button 2]
                # [Button 3] [Button 4]

                with ui.VStack():
                    # everythin inside the block is a child of this layout container
                    # stack UI wedgets under each other
                    # generate buttons dynamically with lambda n=name, p=path: ... which defers execution until clicked
                    omni.ui.Button(
                        "Add Random Chardbox",
                        clicked_fn=lambda: self.spawn_from_asset_map(self.cardbox_assets)
                    )

                    omni.ui.Button(
                        "Add Random Pallets",
                        clicked_fn=lambda: self.spawn_from_asset_map(self.pallet_assets)
                    )

                    # use HStaack if adding buttons like "Spawn" and "Clear"
                    #with ui.HStack():
                        # ui.Button("Spawn")
                        # ui.Button("Clear")

            self._window.set_visibility_changed_fn(self._visiblity_changed_fn)

        else:
            if self._window:
                # remove window
                self._window = None

        # create a menu item inside the already existing "Window" menu
        editor_menu = omni.kit.ui.get_editor_menu()
        if editor_menu:
            editor_menu.set_value("Window/Ellie's Window", visible)


    def _visiblity_changed_fn(self, visible):
        # function that tells the application what to do when the visibility of the window is changed
        editor_menu = omni.kit.ui.get_editor_menu()
        if editor_menu:
            # Toggle the checked state of the menu item
            editor_menu.set_value("Window/Ellie's Window", visible)
