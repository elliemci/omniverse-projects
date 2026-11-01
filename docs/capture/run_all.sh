#!/usr/bin/env bash
# Headless viewport captures for the README. Does not modify project files.
# Usage: docs/capture/run_all.sh [raw_output_dir]
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
RAW="${1:-$ROOT/docs/capture/raw}"
KIT="$(ls -d "$HOME"/.cache/packman/chk/kit-kernel/109*/kit | head -1)"
SRC="$ROOT/omniverse-kit-app-extensions/source"
SC="$SRC/data/OpenUSD_Lab/Assemblies"
mkdir -p "$RAW"

run() {  # name app stage frames spawn
  local name=$1 app=$2 stage=$3 frames=$4 spawn=$5
  echo "== $name"
  CAP_SETTLE="${SETTLE:-300}" CAP_STAGE="$stage" CAP_OUT="$RAW/$name.png" CAP_FRAMES="$frames" CAP_SPAWN="$spawn" \
  timeout 600 "$KIT" "$SRC/apps/$app.kit" --no-window --/app/window/hideUi=true \
    --/persistent/app/viewport/displayOptions=0 \
    --ext-folder "$SRC/extensions" --enable ellies.python_ui_extension \
    --exec "$ROOT/docs/capture/capture_stage.py" > "$RAW/$name.log" 2>&1
  echo "   exit=$?"
}

run intro_factory_lite       ellie.test_app "$SC/Factory_Lite/Factory_Lite.usda" 0 0
run intro_factory_layout     ellie.test_app "$SC/Factory_Layout/Factory_Layout.usda" 0 0
run ext_before_spawn         ellie.test_app "$SC/Factory_Lite/Factory_Lite.usda" 0 0
run ext_after_spawn          ellie.test_app "$SC/Factory_Lite/Factory_Lite.usda" 0 8
SETTLE=900 run dt_conveyor_physics_{n}  ellie.test_app "$SC/Factory_Lite/Factory_Lite_ConveyorBelt_Physics.usd" 0,4 0
# Factory_Lite_Waypoints.usd skipped: default camera does not frame the waypoint markers.
run dt_spawned_boxes         ellie.test_app "$SC/Spawned_boxes.usda" 0 0
