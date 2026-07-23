#!/usr/bin/env python3
"""Live-preview capture GUI — streams all three cameras and captures frames
directly from the video feed without restarting pipelines.

Usage::

    python -m preview_mode.preview_gui          # from project root
    python preview_mode/preview_gui.py          # from project root
"""

from __future__ import annotations

import argparse
import importlib
import re
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import ttk, scrolledtext, messagebox

# Allow importing modules from the project root
_PARENT = Path(__file__).resolve().parent.parent
if str(_PARENT) not in sys.path:
    sys.path.insert(0, str(_PARENT))

import cv2
import numpy as np

from capture_base import _create_dry_run_placeholder
from preview_mode.camera_manager import (
    CAMERA_IDS,
    ORBBEC_C1,
    ORBBEC_C2,
    REALSENSE,
    CameraManager,
    list_connected_cameras,
)

# Try to import PIL (may not be installed on all lab machines)
try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


def _load_path_config(module_name: str):
    """Dynamically import a path_config module by name."""
    try:
        return importlib.import_module(module_name)
    except ImportError as e:
        print(f"无法加载配置模块 '{module_name}': {e}", file=sys.stderr)
        raise SystemExit(1) from e


# ── constants ─────────────────────────────────────────────────────────────

PREVIEW_WIDTH = 640
PREVIEW_HEIGHT = 480
FRAME_INTERVAL_MS = 33  # ~30 fps

CAMERA_LABELS: dict[str, str] = {
    REALSENSE: "RealSense",
    ORBBEC_C1: "Orbbec C1",
    ORBBEC_C2: "Orbbec C2",
}


# ────────────────────────────────────────────────────────────────────────────
# PreviewCaptureGUI
# ────────────────────────────────────────────────────────────────────────────


class PreviewCaptureGUI:
    """Standalone tkinter application that combines live camera preview
    with parameter-driven capture directly from the video stream."""

    def __init__(self, root: tk.Tk, cfg=None) -> None:
        self.root = root

        # Load path config (pluggable)
        if cfg is None:
            cfg = _load_path_config("path_config_material")
        self._cfg = cfg
        self._material_mode = bool(getattr(cfg, "USES_MATERIAL_HIERARCHY", False))

        root.title("拍照控制 — 实时预览")
        root.minsize(1000, 800)

        # Internal state
        self._camera_manager: CameraManager | None = None
        self._preview_active = False
        self._capturing = False
        # Keyboard shortcut state
        self._kb_mode: str | None = None  # 'material' | 'anomaly' | None
        self._kb_buffer: str = ""
        self._kb_after_id: str | None = None
        self._current_camera = REALSENSE
        self._imgtk: ImageTk.PhotoImage | None = None
        self._kb_status_var = tk.StringVar()
        self._after_id: str | None = None

        # Theme
        try:
            ttk.Style().theme_use("vista")
        except tk.TclError:
            pass

        self._build_ui()
        self._update_path_preview()

        # Clean shutdown
        root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── UI construction ───────────────────────────────────────────────

    def _build_ui(self) -> None:
        main = ttk.Frame(self.root, padding=12)
        main.pack(fill=tk.BOTH, expand=True)

        self._build_preview_section(main)
        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=6)
        self._build_param_section(main)
        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=6)
        self._build_button_section(main)
        self._build_log_section(main)
        self._setup_keyboard_shortcuts()

    # ── preview section ───────────────────────────────────────────────

    def _build_preview_section(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="相机预览", padding=6)
        frame.pack(fill=tk.BOTH, expand=True)

        # Top bar: camera selector + status
        top = ttk.Frame(frame)
        top.pack(fill=tk.X, pady=(0, 4))

        ttk.Label(top, text="相机:").pack(side=tk.LEFT)
        self._cam_var = tk.StringVar(value=REALSENSE)
        for cid in CAMERA_IDS:
            ttk.Radiobutton(
                top,
                text=CAMERA_LABELS[cid],
                variable=self._cam_var,
                value=cid,
                command=self._on_camera_switch,
            ).pack(side=tk.LEFT, padx=4)

        self._status_var = tk.StringVar(value="未启动预览")
        ttk.Label(top, textvariable=self._status_var, foreground="gray").pack(
            side=tk.RIGHT
        )

        # Preview display
        if HAS_PIL:
            self._preview_label = ttk.Label(
                frame, anchor=tk.CENTER, background="black"
            )
            self._preview_label.pack(fill=tk.BOTH, expand=True)
        else:
            self._preview_label = ttk.Label(
                frame,
                text="⚠ Pillow not installed.\nInstall with: pip install Pillow",
                anchor=tk.CENTER,
            )
            self._preview_label.pack(fill=tk.BOTH, expand=True)

    # ── parameter section ─────────────────────────────────────────────

    def _build_param_section(self, parent: ttk.Frame) -> None:
        section = ttk.LabelFrame(parent, text="拍摄参数", padding=6)
        section.pack(fill=tk.X)

        if self._material_mode:
            self._build_material_param_fields(section)
            return

        # Row 0: container + anomaly type
        row0 = ttk.Frame(section)
        row0.pack(fill=tk.X, pady=1)
        object_label = getattr(self._cfg, "OBJECT_LABEL_CN", "容器:")
        ttk.Label(row0, text=object_label, width=10).pack(side=tk.LEFT)
        self._container_var = tk.StringVar()
        self._container_cb = ttk.Combobox(
            row0, textvariable=self._container_var, state="readonly", width=30
        )
        self._container_cb.pack(side=tk.LEFT, padx=(0, 16))
        self._container_var.trace_add("write", self._on_container_change)

        ttk.Label(row0, text="异常类型:", width=10).pack(side=tk.LEFT)
        self._anomaly_var = tk.StringVar()
        self._anomaly_cb = ttk.Combobox(
            row0, textvariable=self._anomaly_var, state="readonly", width=30
        )
        self._anomaly_cb.pack(side=tk.LEFT)
        self._anomaly_var.trace_add("write", self._on_anomaly_change)

        # Row 1: subcategory + shooting point
        row1 = ttk.Frame(section)
        row1.pack(fill=tk.X, pady=1)
        ttk.Label(row1, text="小类:", width=10).pack(side=tk.LEFT)
        self._sub_var = tk.StringVar()
        self._sub_cb = ttk.Combobox(
            row1, textvariable=self._sub_var, state="readonly", width=30
        )
        self._sub_cb.pack(side=tk.LEFT, padx=(0, 16))
        self._sub_var.trace_add("write", self._on_path_field_change)

        ttk.Label(row1, text="拍摄点位:", width=10).pack(side=tk.LEFT)
        self._point_var = tk.StringVar(value=self._cfg.SHOOTING_POINTS_CN_LIST[0])
        self._point_cb = ttk.Combobox(
            row1, textvariable=self._point_var, values=self._cfg.SHOOTING_POINTS_CN_LIST, width=28
        )
        self._point_cb.pack(side=tk.LEFT)
        self._point_var.trace_add("write", self._on_path_field_change)

        # Row 2: view number + photo number
        # 视角编号支持数字（补零）或字符串如 A1（不补零）
        row2 = ttk.Frame(section)
        row2.pack(fill=tk.X, pady=1)
        ttk.Label(row2, text="视角编号:", width=10).pack(side=tk.LEFT)
        self._view_var = tk.StringVar(value="1")
        ttk.Entry(row2, textvariable=self._view_var, width=10).pack(side=tk.LEFT)
        self._view_var.trace_add("write", self._on_path_field_change)

        ttk.Label(row2, text="照片编号:", width=10).pack(
            side=tk.LEFT, padx=(28, 0)
        )
        self._photo_var = tk.IntVar(value=1)
        ttk.Spinbox(
            row2, from_=1, to=999, textvariable=self._photo_var, width=8
        ).pack(side=tk.LEFT)
        ttk.Button(
            row2, text="Next", width=6, command=self._next_photo_number
        ).pack(side=tk.LEFT, padx=(6, 0))

        # Path preview
        row3 = ttk.Frame(section)
        row3.pack(fill=tk.X, pady=(4, 0))
        ttk.Label(row3, text="保存路径:", width=10).pack(side=tk.LEFT)
        self._path_var = tk.StringVar()
        ttk.Entry(
            row3,
            textvariable=self._path_var,
            state="readonly",
            font=("Consolas", 9),
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Populate combobox values
        self._populate_params()

    def _build_material_param_fields(self, section: ttk.Frame) -> None:
        row0 = ttk.Frame(section)
        row0.pack(fill=tk.X, pady=1)
        ttk.Label(row0, text="材料状态:", width=10).pack(side=tk.LEFT)
        self._state_var = tk.StringVar()
        self._state_cb = ttk.Combobox(
            row0, textvariable=self._state_var, state="readonly", width=24
        )
        self._state_cb.pack(side=tk.LEFT, padx=(0, 16))
        self._state_var.trace_add("write", self._on_material_state_change)

        ttk.Label(row0, text="具体材料:", width=10).pack(side=tk.LEFT)
        self._material_var = tk.StringVar()
        self._material_cb = ttk.Combobox(
            row0, textvariable=self._material_var, state="readonly", width=38
        )
        self._material_cb.pack(side=tk.LEFT)
        self._material_var.trace_add("write", self._on_material_change)

        row1 = ttk.Frame(section)
        row1.pack(fill=tk.X, pady=1)
        ttk.Label(row1, text="异常类型:", width=10).pack(side=tk.LEFT)
        self._anomaly_var = tk.StringVar()
        self._anomaly_cb = ttk.Combobox(
            row1, textvariable=self._anomaly_var, state="readonly", width=30
        )
        self._anomaly_cb.pack(side=tk.LEFT, padx=(0, 16))
        self._anomaly_var.trace_add("write", self._on_anomaly_change)

        ttk.Label(row1, text="容器种类:", width=10).pack(side=tk.LEFT)
        self._container_var = tk.StringVar()
        self._container_cb = ttk.Combobox(
            row1, textvariable=self._container_var, state="readonly", width=30
        )
        self._container_cb.pack(side=tk.LEFT)
        self._container_var.trace_add("write", self._on_container_change)

        row2 = ttk.Frame(section)
        row2.pack(fill=tk.X, pady=1)
        ttk.Label(row2, text="拍摄点位:", width=10).pack(side=tk.LEFT)
        self._point_var = tk.StringVar()
        self._point_cb = ttk.Combobox(
            row2, textvariable=self._point_var, state="readonly", width=30
        )
        self._point_cb.pack(side=tk.LEFT)
        self._point_var.trace_add("write", self._on_path_field_change)

        row3 = ttk.Frame(section)
        row3.pack(fill=tk.X, pady=1)
        ttk.Label(row3, text="视角编号:", width=10).pack(side=tk.LEFT)
        self._view_var = tk.StringVar(value="1")
        ttk.Entry(row3, textvariable=self._view_var, width=10).pack(side=tk.LEFT)
        self._view_var.trace_add("write", self._on_path_field_change)

        ttk.Label(row3, text="照片编号:", width=10).pack(
            side=tk.LEFT, padx=(28, 0)
        )
        self._photo_var = tk.IntVar(value=1)
        ttk.Spinbox(
            row3, from_=1, to=999, textvariable=self._photo_var, width=8
        ).pack(side=tk.LEFT)
        ttk.Button(
            row3, text="Next", width=6, command=self._next_photo_number
        ).pack(side=tk.LEFT, padx=(6, 0))

        row4 = ttk.Frame(section)
        row4.pack(fill=tk.X, pady=(4, 0))
        ttk.Label(row4, text="保存路径:", width=10).pack(side=tk.LEFT)
        self._path_var = tk.StringVar()
        ttk.Entry(
            row4,
            textvariable=self._path_var,
            state="readonly",
            font=("Consolas", 9),
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)

        self._populate_params()

    def _populate_params(self) -> None:
        """Fill comboboxes with values from the loaded path config."""
        if self._material_mode:
            self._populate_material_params()
            return

        c_items = [f"{k}: {v}" for k, v in sorted(self._cfg.CONTAINERS_CN.items())]
        self._container_cb["values"] = c_items
        if c_items:
            self._container_var.set(c_items[0])

        self._update_anomalies()

    def _populate_material_params(self) -> None:
        items = [
            f"{sid}: {self._cfg.MATERIAL_STATES_CN[sid]}"
            for sid in sorted(self._cfg.MATERIAL_STATES)
        ]
        self._state_cb["values"] = items
        if items:
            self._state_var.set(items[0])
        self._update_material_dependent_fields()

    # ── button section ────────────────────────────────────────────────

    def _build_button_section(self, parent: ttk.Frame) -> None:
        row = ttk.Frame(parent)
        row.pack(fill=tk.X, pady=6)

        self._preview_btn = ttk.Button(
            row, text="▶ 开始预览", command=self._start_preview
        )
        self._preview_btn.pack(side=tk.LEFT, padx=(0, 4))

        self._stop_preview_btn = ttk.Button(
            row, text="⏹ 停止预览", command=self._stop_preview, state=tk.DISABLED
        )
        self._stop_preview_btn.pack(side=tk.LEFT, padx=(0, 12))

        self._capture_btn = ttk.Button(
            row, text="📷 拍照", command=self._do_capture, state=tk.DISABLED
        )
        self._capture_btn.pack(side=tk.LEFT, padx=(0, 4))

        self._dryrun_btn = ttk.Button(
            row, text="预览 (dry-run)", command=self._do_dry_run
        )
        self._dryrun_btn.pack(side=tk.LEFT, padx=(0, 4))

        self._list_btn = ttk.Button(
            row, text="列出相机", command=self._do_list_cameras
        )
        self._list_btn.pack(side=tk.LEFT)

        # Keyboard shortcut status label (fixed-width, no layout shift)
        self._kb_status_label = ttk.Label(
            row,
            textvariable=self._kb_status_var,
            foreground="#555",
            width=36,
            anchor=tk.W,
        )
        self._kb_status_label.pack(side=tk.LEFT, padx=(16, 0))

    # ── log section ───────────────────────────────────────────────────

    def _build_log_section(self, parent: ttk.Frame) -> None:
        ttk.Label(parent, text="日志:").pack(anchor=tk.W, pady=(4, 0))
        self._log_area = scrolledtext.ScrolledText(
            parent,
            height=8,
            font=("Consolas", 9),
            wrap=tk.WORD,
            state=tk.DISABLED,
        )
        self._log_area.pack(fill=tk.BOTH, expand=True)

    # ── parameter callbacks ───────────────────────────────────────────

    def _current_combo_id(self, variable: tk.StringVar) -> int | None:
        try:
            return int(variable.get().split(":", 1)[0])
        except (ValueError, IndexError):
            return None

    def _require_combo_id(self, variable: tk.StringVar, label: str) -> int:
        value_id = self._current_combo_id(variable)
        if value_id is None:
            raise ValueError(f"请选择{label}")
        return value_id

    def _set_id_options(
        self,
        combobox: ttk.Combobox,
        variable: tk.StringVar,
        options: dict[int, str],
        current_id: int | None = None,
    ) -> None:
        items = [f"{item_id}: {name}" for item_id, name in sorted(options.items())]
        combobox["values"] = items
        if not items:
            variable.set("")
            return
        selected_id = current_id if current_id in options else min(options)
        selected = f"{selected_id}: {options[selected_id]}"
        if variable.get() != selected:
            variable.set(selected)

    def _on_material_state_change(self, *_args) -> None:
        if not self._material_mode:
            return
        self._photo_var.set(1)
        self._update_material_dependent_fields()
        self._update_path_preview()

    def _on_material_change(self, *_args) -> None:
        if not self._material_mode:
            return
        self._photo_var.set(1)
        self._update_path_preview()

    def _update_material_dependent_fields(self) -> None:
        state_id = self._current_combo_id(self._state_var)
        if state_id is None:
            return

        self._set_id_options(
            self._material_cb,
            self._material_var,
            self._cfg.MATERIALS_CN[state_id],
            self._current_combo_id(self._material_var),
        )
        self._set_id_options(
            self._anomaly_cb,
            self._anomaly_var,
            {
                aid: self._cfg.ANOMALY_TYPES_CN[aid]
                for aid in self._cfg.get_anomaly_types(state_id)
            },
            self._current_combo_id(self._anomaly_var),
        )
        self._set_id_options(
            self._container_cb,
            self._container_var,
            {
                cid: self._cfg.CONTAINERS_CN[cid]
                for cid in self._cfg.get_containers(state_id)
            },
            self._current_combo_id(self._container_var),
        )
        self._update_material_points()

    def _update_material_points(self) -> None:
        state_id = self._current_combo_id(self._state_var)
        container_id = self._current_combo_id(self._container_var)
        if state_id is None or container_id is None:
            return

        points = self._cfg.get_shooting_points(state_id, container_id)
        items = [self._cfg.SHOOTING_POINTS[point] for point in points]
        self._point_cb["values"] = items
        if self._point_var.get() not in items:
            self._point_var.set(items[0] if items else "")

    def _on_container_change(self, *_args) -> None:
        self._photo_var.set(1)
        if self._material_mode:
            self._update_material_points()
            self._update_path_preview()
            return
        self._update_anomalies()
        self._update_path_preview()

    def _on_anomaly_change(self, *_args) -> None:
        self._photo_var.set(1)
        if self._material_mode:
            self._update_path_preview()
            return
        self._update_subcategories()
        self._update_path_preview()

    def _on_path_field_change(self, *_args) -> None:
        self._photo_var.set(1)
        self._update_path_preview()

    def _get_shooting_point(self) -> str:
        cn = self._point_var.get().strip()
        return self._cfg.SHOOTING_POINTS_CN.get(cn, cn)

    def _get_subcategory_value(self) -> str:
        sub = self._sub_var.get().strip()
        if sub == self._cfg.NO_SUBCATEGORY:
            return self._cfg.NO_SUBCATEGORY
        subs_en = {v: k for k, v in self._cfg.ANOMALY_SUBCATEGORIES_CN.items()}
        return subs_en.get(sub, sub)

    def _update_anomalies(self) -> None:
        container_text = self._container_var.get()
        if not container_text:
            return
        try:
            container_id = int(container_text.split(":")[0])
        except (ValueError, IndexError):
            container_id = min(self._cfg.CONTAINERS)

        if hasattr(self._cfg, "get_anomaly_types"):
            anomaly_ids = self._cfg.get_anomaly_types(container_id)
        else:
            anomaly_ids = sorted(self._cfg.ANOMALY_TYPES)

        current_id = None
        try:
            current_id = int(self._anomaly_var.get().split(":")[0])
        except (ValueError, IndexError):
            pass

        items = [f"{aid}: {self._cfg.ANOMALY_TYPES_CN[aid]}" for aid in anomaly_ids]
        self._anomaly_cb["values"] = items
        if not items:
            self._anomaly_var.set("")
            return

        selected_id = current_id if current_id in anomaly_ids else anomaly_ids[0]
        self._anomaly_var.set(
            f"{selected_id}: {self._cfg.ANOMALY_TYPES_CN[selected_id]}"
        )
        self._update_subcategories()

    def _update_subcategories(self) -> None:
        text = self._anomaly_var.get()
        if not text:
            return
        try:
            aid = int(text.split(":")[0])
        except (ValueError, IndexError):
            aid = 1

        try:
            cid = int(self._container_var.get().split(":")[0])
        except (ValueError, IndexError):
            cid = min(self._cfg.CONTAINERS)

        if hasattr(self._cfg, "get_anomaly_subcategories"):
            subs = self._cfg.get_anomaly_subcategories(cid, aid)
        else:
            subs = self._cfg.ANOMALY_SUBCATEGORIES.get(aid, [])
        subs_display = [self._cfg.ANOMALY_SUBCATEGORIES_CN.get(s, s) for s in subs]
        if aid == 1 or not subs:
            self._sub_cb["state"] = tk.DISABLED
            self._sub_var.set(self._cfg.NO_SUBCATEGORY)
            self._sub_cb["values"] = [self._cfg.NO_SUBCATEGORY]
        else:
            self._sub_cb["state"] = "readonly"
            self._sub_cb["values"] = subs_display
            self._sub_var.set(subs_display[0])

    def _update_path_preview(self, *_args) -> None:
        try:
            path = self._build_output_dir()
            self._path_var.set(str(path))
        except Exception:
            self._path_var.set("(参数不完整)")

    def _on_camera_switch(self) -> None:
        self._current_camera = self._cam_var.get()

    # ── path building ─────────────────────────────────────────────────

    def _parse_material_params(self) -> tuple[int, int, int, int, str, str, int]:
        state_id = self._require_combo_id(self._state_var, "材料状态")
        material_id = self._require_combo_id(self._material_var, "具体材料")
        anomaly_id = self._require_combo_id(self._anomaly_var, "异常类型")
        container_id = self._require_combo_id(self._container_var, "容器类型")
        point = self._get_shooting_point()
        view = self._view_var.get().strip()
        photo = self._photo_var.get()

        if not point:
            raise ValueError("请选择拍摄点位")
        if not view:
            raise ValueError("请填写视角编号")

        return state_id, material_id, anomaly_id, container_id, point, view, photo

    def _parse_params(self) -> tuple[int, int, str, str, str, int]:
        """Extract (container_id, anomaly_id, sub, point, view, photo)
        from GUI state.  Raises ``ValueError`` on bad input.

        view 可为纯数字（路径中补零）或字符串如 A1（路径中原样使用）。
        """
        cid = int(self._container_var.get().split(":")[0])
        aid = int(self._anomaly_var.get().split(":")[0])
        sub = self._get_subcategory_value()
        point = self._get_shooting_point()
        view = self._view_var.get().strip()
        photo = self._photo_var.get()

        if not point:
            raise ValueError("请选择拍摄点位")
        if not view:
            raise ValueError("请填写视角编号")

        return cid, aid, sub, point, view, photo

    def _confirm_overwrite(self, paths: dict[str, Path]) -> bool:
        existing = [p for p in paths.values() if p.exists()]
        if not existing:
            return True
        msg = "以下文件已存在:\n" + "\n".join(str(p) for p in existing)
        msg += "\n\n是否覆盖？"
        return messagebox.askyesno("文件已存在", msg)

    def _build_output_dir(self) -> Path:
        if self._material_mode:
            state, material, anomaly, container, point, view, _photo = (
                self._parse_material_params()
            )
            return self._cfg.build_shot_dir(
                state, material, anomaly, container, point, view
            )

        cid, aid, sub, point, view, _photo = self._parse_params()
        return self._cfg.build_shot_dir(cid, aid, sub, point, view)

    def _build_output_paths(self) -> dict[str, Path]:
        """Return ``{camera_id: output_file_path}`` for the current
        parameter selection."""
        if self._material_mode:
            state, material, anomaly, container, point, view, photo = (
                self._parse_material_params()
            )
            shot_dir = self._cfg.build_shot_dir(
                state, material, anomaly, container, point, view
            )
        else:
            cid, aid, sub, point, view, photo = self._parse_params()
            shot_dir = self._cfg.build_shot_dir(cid, aid, sub, point, view)

        photo_id = f"{photo:03d}"
        orbbec_dir = shot_dir / f"view_top_{photo}"

        return {
            REALSENSE: shot_dir / f"{photo_id}_Color.png",
            ORBBEC_C1: orbbec_dir / "camera1_Color.png",
            ORBBEC_C2: orbbec_dir / "camera2_Color.png",
        }

    def _scan_max_photo_number(self, shot_dir: Path) -> int:
        """Return the highest photo number already present in *shot_dir*.

        Recognises script naming rules:
        - RealSense: ``001_Color.png``, ``002_Color.png``, …
        - Orbbec:    ``view_top_1/``, ``view_top_2/``, …
        """
        if not shot_dir.is_dir():
            return 0

        max_n = 0
        color_re = re.compile(r"^(\d+)_Color\.png$", re.IGNORECASE)
        top_re = re.compile(r"^view_top_(\d+)$", re.IGNORECASE)

        for entry in shot_dir.iterdir():
            if entry.is_file():
                m = color_re.match(entry.name)
                if m:
                    max_n = max(max_n, int(m.group(1)))
            elif entry.is_dir():
                m = top_re.match(entry.name)
                if m:
                    max_n = max(max_n, int(m.group(1)))

        return max_n

    def _next_photo_number(self) -> None:
        """Set photo number to max existing + 1 in the current shot folder."""
        try:
            shot_dir = self._build_output_dir()
        except ValueError as exc:
            messagebox.showwarning("参数不完整", str(exc))
            return
        except Exception:
            messagebox.showwarning("参数不完整", "无法解析当前保存路径")
            return

        next_n = self._scan_max_photo_number(shot_dir) + 1
        if next_n > 999:
            messagebox.showwarning("编号超限", "下一编号已超过 999")
            return

        self._photo_var.set(next_n)
        self._update_path_preview()
        self._log(f"Next → 照片编号 {next_n}  ({shot_dir})")

    # ── preview control ───────────────────────────────────────────────

    def _start_preview(self) -> None:
        if not HAS_PIL:
            messagebox.showerror(
                "缺少依赖",
                "实时预览需要 Pillow 库。\n请在终端运行: pip install Pillow",
            )
            return

        if self._preview_active:
            return

        self._log("正在启动相机流…")
        self._set_buttons_preview_starting()

        try:
            self._camera_manager = CameraManager(warmup_frames=self._cfg.WARMUP_FRAMES)
        except Exception as exc:
            self._log(f"初始化 CameraManager 失败: {exc}")
            messagebox.showerror("相机初始化失败", str(exc))
            self._set_buttons_preview_stopped()
            return

        # Start cameras in a background thread so the UI stays responsive
        def _start_and_begin() -> None:
            try:
                results = self._camera_manager.start_all(self._cfg.ORBBEC_C1_SERIAL)
                self.root.after(0, self._on_preview_started, results)
            except Exception as exc:
                self.root.after(0, self._on_preview_failed, str(exc))

        t = threading.Thread(target=_start_and_begin, daemon=True)
        t.start()

    def _on_preview_started(self, results: dict[str, bool]) -> None:
        success_count = sum(1 for v in results.values() if v)
        self._log(
            f"相机流已启动 ({success_count}/{len(results)} 路就绪): {results}"
        )

        self._preview_active = True
        self._set_buttons_preview_running()
        self._status_var.set("预热中…")
        self._update_frame()

    def _on_preview_failed(self, error_msg: str) -> None:
        self._log(f"启动相机流失败: {error_msg}")
        messagebox.showerror("启动失败", error_msg)
        self._set_buttons_preview_stopped()
        if self._camera_manager:
            self._camera_manager.stop_all()
            self._camera_manager = None

    def _stop_preview(self) -> None:
        self._preview_active = False

        # Cancel scheduled frame update
        if self._after_id is not None:
            self.root.after_cancel(self._after_id)
            self._after_id = None

        if self._camera_manager is not None:
            self._log("正在停止相机流…")
            self._camera_manager.stop_all()
            self._camera_manager = None

        self._set_buttons_preview_stopped()
        self._status_var.set("未启动预览")

        # Clear preview
        if HAS_PIL:
            self._preview_label.configure(image="", text="")
            self._imgtk = None

        self._log("相机流已停止")

    def _update_frame(self) -> None:
        """Called periodically by ``root.after`` to refresh the preview
        image from the current camera's latest frame."""
        if not self._preview_active:
            return

        mgr = self._camera_manager
        if mgr is None or not mgr.is_running():
            self._after_id = self.root.after(FRAME_INTERVAL_MS, self._update_frame)
            return

        cam_id = self._current_camera
        frame = mgr.get_latest_frame(cam_id)

        if frame is not None and HAS_PIL:
            # Update health status
            healthy = mgr.is_healthy(cam_id)
            h, w = frame.shape[:2]
            self._status_var.set(
                f"{'● Live' if healthy else '⚠ Unstable'}  {w}x{h}"
            )

            # Resize to fit preview area while preserving aspect ratio
            scale = min(PREVIEW_WIDTH / w, PREVIEW_HEIGHT / h)
            new_w, new_h = int(w * scale), int(h * scale)
            resized = cv2.resize(
                frame, (new_w, new_h), interpolation=cv2.INTER_AREA
            )

            # BGR → RGB → PIL → ImageTk
            rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb)
            self._imgtk = ImageTk.PhotoImage(image=img)
            self._preview_label.configure(image=self._imgtk)
        elif frame is None and HAS_PIL:
            healthy = mgr.is_healthy(cam_id)
            if not healthy:
                self._status_var.set("⚠ 相机断连")
            else:
                self._status_var.set("等待画面…")

        self._after_id = self.root.after(FRAME_INTERVAL_MS, self._update_frame)

    # ── capture ───────────────────────────────────────────────────────

    def _do_capture(self) -> None:
        if self._capturing:
            return

        mgr = self._camera_manager
        if mgr is None or not mgr.is_running():
            # No active preview — can't capture from stream
            messagebox.showwarning(
                "未启动预览",
                "请先点击「开始预览」启动相机流，\n然后再拍照。",
            )
            return

        try:
            paths = self._build_output_paths()
        except ValueError as exc:
            messagebox.showwarning("参数不完整", str(exc))
            return

        if not self._confirm_overwrite(paths):
            return

        shot_dir = paths[REALSENSE].parent
        self._log(f"拍照 → {shot_dir}")
        self._capturing = True
        self._capture_btn["state"] = tk.DISABLED

        # Run capture in a background thread so preview keeps updating
        def _capture() -> None:
            try:
                results = mgr.capture_all(paths)
                self.root.after(0, self._on_capture_done, results, paths)
            except Exception as exc:
                self.root.after(0, self._on_capture_error, str(exc))

        t = threading.Thread(target=_capture, daemon=True)
        t.start()

    def _on_capture_done(
        self, results: dict[str, bool], paths: dict[str, Path]
    ) -> None:
        for cam_id, ok in results.items():
            label = CAMERA_LABELS.get(cam_id, cam_id)
            if ok:
                self._log(f"  ✓ {label} → {paths[cam_id]}")
            else:
                self._log(f"  ✗ {label} 失败 (无可用帧)")

        self._log("拍照完成")
        self._capturing = False
        self._capture_btn["state"] = tk.NORMAL

        # Auto-increment photo number
        current = self._photo_var.get()
        self._photo_var.set(current + 1)
        self._update_path_preview()

    def _on_capture_error(self, error_msg: str) -> None:
        self._log(f"拍照出错: {error_msg}")
        messagebox.showerror("拍照失败", error_msg)
        self._capturing = False
        self._capture_btn["state"] = tk.NORMAL

    # ── dry-run ───────────────────────────────────────────────────────

    def _do_dry_run(self) -> None:
        try:
            paths = self._build_output_paths()
        except ValueError as exc:
            messagebox.showwarning("参数不完整", str(exc))
            return

        if not self._confirm_overwrite(paths):
            return

        self._log(f"dry-run → {paths[REALSENSE].parent}")
        for f in (paths[REALSENSE], paths[ORBBEC_C1], paths[ORBBEC_C2]):
            _create_dry_run_placeholder(f)
        self._log("dry-run 完成 — 未连接任何相机")

        # Auto-increment photo number
        current = self._photo_var.get()
        self._photo_var.set(current + 1)
        self._update_path_preview()

    # ── list cameras ──────────────────────────────────────────────────

    def _do_list_cameras(self) -> None:
        self._log("> 列出相机")
        # Run in thread to avoid blocking UI
        def _list() -> None:
            try:
                text = list_connected_cameras(self._cfg.ORBBEC_C1_SERIAL)
                self.root.after(0, self._log, text)
            except Exception as exc:
                self.root.after(0, self._log, f"列出相机失败: {exc}")

        t = threading.Thread(target=_list, daemon=True)
        t.start()

    # ── button state helpers ──────────────────────────────────────────

    def _set_buttons_preview_starting(self) -> None:
        self._preview_btn["state"] = tk.DISABLED
        self._stop_preview_btn["state"] = tk.DISABLED
        self._capture_btn["state"] = tk.DISABLED

    def _set_buttons_preview_running(self) -> None:
        self._preview_btn["state"] = tk.DISABLED
        self._stop_preview_btn["state"] = tk.NORMAL
        self._capture_btn["state"] = tk.NORMAL

    def _set_buttons_preview_stopped(self) -> None:
        self._preview_btn["state"] = tk.NORMAL
        self._stop_preview_btn["state"] = tk.DISABLED
        self._capture_btn["state"] = tk.DISABLED

    # ── logging ───────────────────────────────────────────────────────

    def _log(self, msg: str) -> None:
        self._log_area["state"] = tk.NORMAL
        self._log_area.insert(tk.END, msg + "\n")
        self._log_area.see(tk.END)
        self._log_area["state"] = tk.DISABLED

    # ── keyboard shortcuts ────────────────────────────────────────────

    def _setup_keyboard_shortcuts(self) -> None:
        """Register global keyboard and mouse bindings for quick operation."""
        self.root.bind("<Key>", self._on_key_press, add=True)
        # Cancel pending input on any mouse click
        self.root.bind("<Button-1>", self._on_mouse_cancel, add=True)

    def _is_editable_widget(self, widget) -> bool:
        """Return True if *widget* is a writable text-entry control."""
        if widget is None:
            return False
        # ttk.Entry covers both plain Entry and Spinbox
        if isinstance(widget, (tk.Entry, tk.Text, ttk.Entry)):
            return True
        # ttk.Combobox is editable unless state="readonly"
        if isinstance(widget, ttk.Combobox):
            try:
                return widget.cget("state") != "readonly"
            except tk.TclError:
                return False
        return False

    def _on_key_press(self, event: tk.Event) -> str | None:
        """Global key handler for shortcut sequences.

        Implemented per ``.plan/preview-gui-keyboard-control.md``.
        Returns ``"break"`` for consumed events; ``None`` otherwise.
        """
        # During capture — ignore all shortcuts
        if self._capturing:
            return "break"

        focus = self.root.focus_get()
        editable = self._is_editable_widget(focus)

        # ── Space: trigger capture (only when not in kb input mode) ──
        if event.keysym == "space" and not editable:
            if self._kb_mode is None:
                self._do_capture()
            return "break"

        # ── Escape: cancel input mode ──
        if event.keysym == "Escape" and self._kb_mode is not None:
            self._kb_cancel()
            return "break"

        # ── M / m: material selection mode ──
        if event.char in ("m", "M") and not editable:
            if self._material_mode:
                self._enter_kb_mode("material")
            return "break"

        # ── E / e: anomaly selection mode ──
        if event.char in ("e", "E") and not editable:
            self._enter_kb_mode("anomaly")
            return "break"

        # ── Digit input (only in kb mode) ──
        if event.char in "0123456789" and self._kb_mode is not None and not editable:
            self._kb_append_digit(event.char)
            return "break"

        # ── Backspace (only in kb mode) ──
        if event.keysym == "BackSpace" and self._kb_mode is not None and not editable:
            self._kb_backspace()
            return "break"

        # ── Enter / Return: submit buffer (in kb mode) ──
        if event.keysym == "Return" and self._kb_mode is not None:
            self._kb_submit()
            return "break"

        return None

    def _on_mouse_cancel(self, _event: tk.Event) -> None:
        """Cancel pending keyboard input on any mouse click."""
        if self._kb_mode is not None:
            self._kb_cancel()

    def _enter_kb_mode(self, mode: str) -> None:
        """Enter *mode* ('material' | 'anomaly') keyboard-input mode."""
        if self._kb_after_id is not None:
            self.root.after_cancel(self._kb_after_id)
            self._kb_after_id = None
        if self._kb_mode == mode:
            # Same mode again: clear buffer but stay in mode
            self._kb_buffer = ""
        else:
            self._kb_mode = mode
            self._kb_buffer = ""
        self._update_kb_status()

    def _kb_append_digit(self, digit: str) -> None:
        """Append *digit* to the keyboard input buffer."""
        self._kb_buffer += digit
        self._update_kb_status()

    def _kb_backspace(self) -> None:
        """Remove the last digit from the keyboard buffer."""
        if self._kb_buffer:
            self._kb_buffer = self._kb_buffer[:-1]
        self._update_kb_status()

    def _kb_cancel(self) -> None:
        """Cancel keyboard input mode and clear all state."""
        if self._kb_after_id is not None:
            self.root.after_cancel(self._kb_after_id)
            self._kb_after_id = None
        self._kb_mode = None
        self._kb_buffer = ""
        self._kb_status_var.set("")

    def _kb_submit(self) -> None:
        """Submit the current digit buffer as a numeric ID selection.

        On success, updates the dropdown briefly shows the chosen label and
        exits input mode.  On failure, shows valid IDs, rings the bell, and
        stays in input mode so the user can correct.
        """
        if not self._kb_buffer:
            return  # stay in mode, wait for digits

        item_id = int(self._kb_buffer)  # strips leading zeros
        mode = self._kb_mode

        if mode == "material":
            if not self._material_mode:
                self._kb_cancel()
                return
            ok = self._select_kb_item(self._material_cb, self._material_var, item_id)
            if ok:
                label = self._material_var.get()
                self._kb_status_var.set(f"✓ {label}")
                self._schedule_kb_clear()
            else:
                valid = self._get_kb_valid_ids(self._material_cb)
                self._kb_status_var.set(f"无效编号，可选: {', '.join(valid)}")
                self.root.bell()
                return  # stay in mode

        elif mode == "anomaly":
            ok = self._select_kb_item(self._anomaly_cb, self._anomaly_var, item_id)
            if ok:
                label = self._anomaly_var.get()
                self._kb_status_var.set(f"✓ {label}")
                self._schedule_kb_clear()
            else:
                valid = self._get_kb_valid_ids(self._anomaly_cb)
                self._kb_status_var.set(f"无效编号，可选: {', '.join(valid)}")
                self.root.bell()
                return  # stay in mode

        # Success: exit input mode
        self._kb_mode = None
        self._kb_buffer = ""

    def _select_kb_item(
        self,
        combobox: ttk.Combobox,
        variable: tk.StringVar,
        item_id: int,
    ) -> bool:
        """Select the combobox entry whose numeric prefix matches *item_id*.

        Returns ``True`` on success, ``False`` if no such entry exists.
        """
        prefix = f"{item_id}:"
        for item in combobox["values"]:
            if item.startswith(prefix):
                variable.set(item)
                return True
        return False

    def _get_kb_valid_ids(self, combobox: ttk.Combobox) -> list[str]:
        """Return sorted string IDs extracted from combobox values."""
        ids = []
        for item in combobox["values"]:
            try:
                iid = int(item.split(":", 1)[0])
                ids.append(str(iid))
            except (ValueError, IndexError):
                pass
        return ids

    def _update_kb_status(self) -> None:
        """Refresh the status label with current keyboard input state."""
        if self._kb_mode is None:
            self._kb_status_var.set("")
            return
        label = "材料编号" if self._kb_mode == "material" else "异常编号"
        self._kb_status_var.set(f"{label}: {self._kb_buffer}")

    def _schedule_kb_clear(self) -> None:
        """Schedule the status label to clear after a brief pause."""
        if self._kb_after_id is not None:
            self.root.after_cancel(self._kb_after_id)
        self._kb_after_id = self.root.after(2500, self._clear_kb_status)

    def _clear_kb_status(self) -> None:
        """Clear the keyboard status label (called via ``after``)."""
        self._kb_after_id = None
        self._kb_status_var.set("")

    # ── shutdown ──────────────────────────────────────────────────────

    def _on_close(self) -> None:
        """Clean up cameras and destroy the window."""
        if self._preview_active:
            self._stop_preview()
        self.root.destroy()


# ────────────────────────────────────────────────────────────────────────────
# entry point
# ────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="拍照控制 GUI — 实时预览并采集三路相机图像"
    )
    parser.add_argument(
        "--config",
        default="path_config_material",
        help=(
            "路径配置模块名，默认 %(default)s（可选 path_config_standard / "
            "path_config_beaker / path_config_cleaner）"
        ),
    )
    args = parser.parse_args()

    cfg = _load_path_config(args.config)
    print(f"[配置] 使用 {args.config}")

    root = tk.Tk()
    PreviewCaptureGUI(root, cfg=cfg)
    root.mainloop()
