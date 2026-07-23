# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Laboratory container quality inspection dataset collection tool. Controls 1 Intel RealSense + 2 Orbbec cameras to capture container/labware photos, organizing them into a hierarchical directory structure. Deployed on a lab Ubuntu machine with cameras physically connected.

## Key Scripts & Architecture

### Capture Pipeline (3 generations)

| Script | Role | Naming |
|--------|------|--------|
| `para_cap_standard.py` | **Current main script** — parallel capture (ThreadPoolExecutor, max_workers=3) | All-English standardized |
| `capture_base.py` | Generic capture engine used by `para_cap_standard.py`; provides `--dry-run` | Pluggable via config |
| `capture.py` | Original sequential capture (WARMUP_FRAMES=100, slow) | Chinese / mixed |
| `parallel_cap.py` | Parallel capture, Chinese naming (WARMUP_FRAMES=15) | Chinese / mixed |

**Relationship**: `para_cap_standard.py` is a thin entrypoint that calls `capture_base.py`'s `main()`. Config modules are dynamically loaded via `--config` (default `path_config_standard`).

### Path Config Modules (pluggable naming)

Each module defines `CONTAINERS`, `ANOMALY_TYPES`, `ANOMALY_SUBCATEGORIES`, `DATASET_ROOT`, `ORBBEC_C1_SERIAL`, `WARMUP_FRAMES`, and `build_shot_dir()`:

- `path_config_standard.py` — Full English naming, 13 containers, 8 anomaly types, full shooting points
- `path_config_beaker.py` — Beaker-only subset, English naming
- `path_config_material.py` — 3-state material hierarchy (raw_material / solution / gel) with anomaly types per state
- `path_config_cleaner.py` — (not read, but follows same pattern)

Switch with: `--config path_config_beaker`

### GUIs

- `preview_mode/preview_gui.py` — **Recommended GUI**: live 30fps preview of all 3 cameras via CameraManager, capture directly from stream, no pipeline restart. Requires Pillow. Default config: `path_config_material`.
  ```
  python -m preview_mode.preview_gui
  python -m preview_mode.preview_gui --config path_config_standard
  ```
- `gui.py` — Older basic Tkinter GUI, calls capture scripts as subprocess. Has `Container->Photo` and `Next` buttons but no live preview.

### Analysis & Data Management

- `analyze_empty_container.py` / `analyze_final.py` / `analyze_summary.py` — Three variants of dataset statistics (walk dirs, count PNGs by hierarchy). `analyze_final.py` generates a markdown report. All use hardcoded Windows paths.
- `move_subcategory.py` — Batch-move subcategory dirs across anomaly categories (`--from damage --sub crack --to stain`)
- `solve_green.py` — Fix RealSense green-tinted images caused by BGR/RGB channel order error. Usage: `python solve_green.py <root> --views stack1-004 stack1-005`
- `generate_dataset_table.mjs` — Node.js script scanning dataset → Excel (.xlsx) via `@oai/artifact-tool`
  ```
  node generate_dataset_table.mjs --input <path> --output <path>
  ```

### Interfaces

- `interfaces/delete_unusable.py` — Delete unusable images referenced in CSV lists
- `interfaces/keep_only_chosen.py` — Keep only images listed in `chosen.csv`, delete rest
- `interfaces/chosen.csv` / `interfaces/delete.csv` / `interfaces/unusable_images.csv` — Image selection CSVs

## Dataset Directory Structure

```
<DATASET_ROOT>/
  <container>/                    # e.g. beaker, multiwell_plate_06
    <anomaly_type>/               # e.g. normal, stain, damage
      <subcategory>/              # e.g. crack, water_stain (skipped for normal)
        <point>-<view>/           # e.g. magnetic_stirrer_01-001
          001_Color.png           # RealSense
          view_top_01/            # Orbbec photos subdirectory
            camera_01_rgb.png     # Orbbec C1
            camera_02_rgb.png     # Orbbec C2
```

Normal type (anomaly_type=1) has no subcategory level — subcategory arg is `-`.

## CLI Usage

All capture scripts take 6 positional arguments in fixed order:

```
python para_cap_standard.py <container_id> <anomaly_type> <subcategory> <shooting_point> <view_number> <photo_number>
```

Examples:
```bash
# beaker/normal/magnetic_stirrer_01-001/001_Color.png
python para_cap_standard.py 1 1 - magnetic_stirrer_01 1 1

# beaker/damage/crack/magnetic_stirrer_01-001/
python para_cap_standard.py 1 3 crack magnetic_stirrer_01 1 1

# List cameras
python para_cap_standard.py --list-cameras

# List container/anomaly type IDs
python para_cap_standard.py --list-types

# Validate path without connecting cameras
python para_cap_standard.py 1 1 - magnetic_stirrer_01 1 1 --dry-run
```

## Orbbec Thread Safety

Each Orbbec camera **must** use a separate `Context()` instance — required for thread safety in parallel capture. `capture_base.py` creates a new `Context()` inside `capture_orbbec_single()` per camera thread.

## Turntable Control (ROS2 Docker)

```bash
docker start ros2_VLA_robot
docker exec -it -u ros ros2_VLA_robot bash
ros2 launch lab_turntable turntables.launch.py
# Control via topic:
ros2 topic pub --once /turntable/set_angle lab_turntable_interfaces/msg/TurntableSetAngle \
  "{device_ids: [1], angle_degs: [120.0], speed: 0.0, accel: 0.0}"
```

## Container & Anomaly Reference

**13 containers** (standard): beaker (1), test_tube_model_01 (2), test_tube_model_02 (3), multiwell_plate_06 (4), multiwell_plate_11 (5), multiwell_plate_24 (6), multiwell_plate_48 (7), multiwell_plate_96_model_01 (8), multiwell_plate_96_model_02 (9), magnetic_stirrer_01 (10), magnetic_stirrer_02 (11), liquid_reservoir (12), ultrasonic_cleaner (13)

**8 anomaly types** (standard): normal (1), stain (2), damage (3), liquid_residue (4), solid_residue (5), lid_anomaly (6), label_anomaly (7), placement_error (8)

See `--list-types` for full subcategory breakdown per type. Mapping from Chinese/mixed naming to English standardized naming is documented in `folder_name_mapping.md`.

## Constraints

- **No requirements.txt / pyproject.toml** — install manually:
  ```
  pip install opencv-python numpy pyrealsense2 pyorbbecsdk
  ```
- **Hardcoded paths** — `DATASET_ROOT` in each `path_config_*.py`, modify per environment
- **Orbbec C1 serial** `CL8K14100H4` hardcoded in every config module
- **Must have exactly 2 Orbbec cameras** — scripts exit with error if count ≠ 2
- **`venv/` tracked in git** — commit venv changes with dependency modifications
- **No tests, no lint, no typecheck, no CI**
- **RealSense green issue**: RGB vs BGR channel order — `solve_green.py` fixes per-view batch

## Generation Naming Cross-Reference

| File(s) | Container names | Anomaly types | Point names |
|---------|----------------|---------------|-------------|
| `capture.py`, `parallel_cap.py` | Chinese/mixed | Chinese/mixed | Chinese/mixed |
| `para_cap_standard.py`, `capture_base.py` | English | English | English |
| `path_config_beaker.py` | English (beaker only) | English | English |

When adding new anomaly types or containers, update all three scripts and the corresponding config modules. The `gui.py` has its own inline copies of all config dictionaries.
