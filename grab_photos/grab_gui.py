#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""grab_gui.py — 参数定位数据集目录，逐张预览挑选图片，一键打包。

Usage::

    python grab_photos/grab_gui.py          # from project root
    python -m grab_photos.grab_gui          # equivalent
"""

from __future__ import annotations

import csv
import json
import shutil
import sys
import threading
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk

# Allow importing from project root
_PARENT = Path(__file__).resolve().parent.parent
if str(_PARENT) not in sys.path:
    sys.path.insert(0, str(_PARENT))

import cv2
import numpy as np

# Conditional PIL (mirrors preview_gui.py)
try:
    from PIL import Image, ImageTk

    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# Reuse grab.py utilities (module-level functions, safe to import)
from grab_photos.grab import (  # noqa: E402
    IMAGE_EXTS,
    PathTranslator,
    collect_images,
    generate_module_json,
    load_config,
    resolve_dirs,
    split_multi,
    view_number_of,
)

# ── constants ─────────────────────────────────────────────────────────────

PREVIEW_WIDTH = 520
PREVIEW_HEIGHT = 390

CATEGORY_EMPTY = "empty_container"
CATEGORY_MATERIAL = "material"

# ── helpers ────────────────────────────────────────────────────────────────


def _extract_id(combo_text: str) -> int | None:
    """Extract numeric ID from a '123: label' combobox string."""
    try:
        return int(combo_text.split(":", 1)[0])
    except (ValueError, IndexError):
        return None


def _set_combo_options(
    combo: ttk.Combobox,
    var: tk.StringVar,
    options: dict[int, str],
    prefer_id: int | None = None,
) -> None:
    """Fill *combo* with ``id: name`` entries and select *prefer_id* if valid."""
    items = [f"{i}: {name}" for i, name in sorted(options.items())]
    combo["values"] = items
    if not items:
        var.set("")
        return
    selected = prefer_id if prefer_id in options else min(options)
    var.set(f"{selected}: {options[selected]}")


# ── GrabGui ────────────────────────────────────────────────────────────────


class GrabGui:
    """图片挑选打包 GUI — 参数定位目录，逐张预览，挑选后打包。"""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title("图片抓取打包工具")
        root.minsize(1050, 780)

        # ── parse --load <path> and --dataset-root <dir> from CLI ──
        self._init_load_path: Path | None = None
        self._init_dataset_root: Path | None = None
        argv = sys.argv[1:]
        for i, arg in enumerate(argv):
            if arg == "--load" and i + 1 < len(argv):
                candidate = Path(argv[i + 1])
                if candidate.is_file():
                    self._init_load_path = candidate
            elif arg == "--dataset-root" and i + 1 < len(argv):
                candidate = Path(argv[i + 1])
                if candidate.is_dir():
                    self._init_dataset_root = candidate

        # ── load both configs ──
        self._cfg_empty, self._root_empty = load_config(CATEGORY_EMPTY)
        self._cfg_material, self._root_material = load_config(CATEGORY_MATERIAL)

        if self._cfg_empty is None and self._cfg_material is None:
            messagebox.showerror(
                "配置加载失败",
                "无法加载 path_config_standard 和 path_config_material，请检查项目目录。",
            )
            root.destroy()
            return

        # Active config (switched via category radiobutton)
        self._cfg = self._cfg_empty or self._cfg_material
        self._material_mode = False
        # Use CLI override if provided, otherwise fall back to config defaults
        if self._init_dataset_root is not None:
            self._dataset_root: Path | None = self._init_dataset_root
        else:
            self._dataset_root = self._root_empty or self._root_material

        # ── state ──
        self._current_images: list[Path] = []
        self._current_index: int = 0
        self._image_list: list[dict] = []  # {path, dir_name, category}
        self._packing: bool = False
        self._imgtk: ImageTk.PhotoImage | None = None
        self._search_after_id: str | None = None
        self._search_gen: int = 0  # generation counter for stale-result detection
        self._dataset_root_user_set: bool = self._init_dataset_root is not None

        # ── param widgets (rebuilt on category switch) ──
        self._param_frame: ttk.Frame | None = None
        self._container_var: tk.StringVar | None = None
        self._anomaly_var: tk.StringVar | None = None
        self._sub_var: tk.StringVar | None = None
        self._point_var: tk.StringVar | None = None
        self._view_var: tk.StringVar | None = None
        self._state_var: tk.StringVar | None = None  # material only
        self._material_var: tk.StringVar | None = None  # material only
        self._container_cb: ttk.Combobox | None = None
        self._anomaly_cb: ttk.Combobox | None = None
        self._sub_cb: ttk.Combobox | None = None
        self._point_cb: ttk.Combobox | None = None
        self._state_cb: ttk.Combobox | None = None
        self._material_cb: ttk.Combobox | None = None
        self._config_path_var: tk.StringVar | None = None
        self._match_path_var: tk.StringVar | None = None
        self._process_id_var: tk.StringVar | None = None
        self._name_var: tk.StringVar | None = None
        self._stage_var: tk.StringVar | None = None
        self._stage_cb: ttk.Combobox | None = None

        # ── theme ──
        try:
            ttk.Style().theme_use("vista")
        except tk.TclError:
            pass

        self._build_ui()
        self._switch_category(CATEGORY_EMPTY)

        root.protocol("WM_DELETE_WINDOW", self._on_close)

        # ── auto-load sequence if --load was given ──
        if self._init_load_path is not None:
            self.root.after(100, lambda: self._load_sequence_from_file(self._init_load_path))  # type: ignore[arg-type]

    # ── UI construction ────────────────────────────────────────────────

    def _build_ui(self) -> None:
        main = ttk.Frame(self.root, padding=12)
        main.pack(fill=tk.BOTH, expand=True)

        self._build_category_section(main)
        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=2)

        # Parameter section container (rebuilt on category switch)
        self._param_container = ttk.LabelFrame(main, text="抓取参数", padding=6)
        self._param_container.pack(fill=tk.X)

        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=2)
        self._build_preview_section(main)
        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=2)
        self._build_list_section(main)
        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=2)
        self._build_output_section(main)
        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=2)
        self._build_action_section(main)
        self._build_log_section(main)

        # Keyboard bindings
        self._setup_keyboard()

    # ── category section ───────────────────────────────────────────────

    def _build_category_section(self, parent: ttk.Frame) -> None:
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X)

        ttk.Label(frame, text="数据集:").pack(side=tk.LEFT, padx=(0, 8))
        self._cat_var = tk.StringVar(value=CATEGORY_EMPTY)
        ttk.Radiobutton(
            frame,
            text="空容器 (path_config_standard)",
            variable=self._cat_var,
            value=CATEGORY_EMPTY,
            command=lambda: self._switch_category(CATEGORY_EMPTY),
        ).pack(side=tk.LEFT, padx=(0, 12))
        ttk.Radiobutton(
            frame,
            text="材料 (path_config_material)",
            variable=self._cat_var,
            value=CATEGORY_MATERIAL,
            command=lambda: self._switch_category(CATEGORY_MATERIAL),
        ).pack(side=tk.LEFT)

        # Dataset root row
        root_frame = ttk.Frame(frame)
        root_frame.pack(fill=tk.X, pady=(4, 0))
        ttk.Label(root_frame, text="数据集根目录:").pack(side=tk.LEFT, padx=(0, 4))
        self._dataset_root_var = tk.StringVar(value=str(self._dataset_root or ""))
        self._dataset_root_entry = ttk.Entry(
            root_frame, textvariable=self._dataset_root_var, font=("Consolas", 9)
        )
        self._dataset_root_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        ttk.Button(
            root_frame, text="浏览...", command=self._on_browse_dataset_root
        ).pack(side=tk.LEFT)
        self._dataset_root_var.trace_add("write", self._on_dataset_root_change)

    def _switch_category(self, category: str) -> None:
        """Rebuild parameter section for *category*."""
        if category == CATEGORY_MATERIAL and self._cfg_material is not None:
            self._cfg = self._cfg_material
            self._material_mode = True
            if not self._dataset_root_user_set:
                self._dataset_root = self._root_material
        else:
            self._cfg = self._cfg_empty or self._cfg_material
            self._material_mode = False
            if not self._dataset_root_user_set:
                self._dataset_root = self._root_empty or self._root_material

        self._cat_var.set(
            CATEGORY_MATERIAL if self._material_mode else CATEGORY_EMPTY
        )
        # Sync the text field (only if not user-set, keep user's value)
        if not self._dataset_root_user_set:
            self._programmatic_root_update = True
            try:
                self._dataset_root_var.set(str(self._dataset_root or ""))
            finally:
                self._programmatic_root_update = False

        # Destroy old param widgets
        for w in self._param_container.winfo_children():
            w.destroy()

        if self._material_mode:
            self._build_param_section_material()
        else:
            self._build_param_section_standard()

        # Clear preview and matched images
        self._clear_preview()
        self._current_images = []
        self._current_index = 0

    # ── dataset root ────────────────────────────────────────────────────

    def _on_browse_dataset_root(self) -> None:
        """Open a directory picker and set the dataset root."""
        d = filedialog.askdirectory(title="选择数据集根目录")
        if d:
            self._dataset_root_var.set(d)

    def _on_dataset_root_change(self, *_args) -> None:
        """Called when the dataset root text field is edited."""
        # Ignore programmatic updates from _switch_category — only
        # user-initiated edits (typing or browsing) should lock the root.
        if getattr(self, "_programmatic_root_update", False):
            return
        new_root_str = self._dataset_root_var.get().strip()
        if new_root_str:
            new_root = Path(new_root_str)
            if new_root.is_dir():
                self._dataset_root = new_root
                self._dataset_root_user_set = True
                # Re-trigger path resolution with the new root
                self._on_path_field_change()
                return
        # If empty or invalid, still allow but resolution will show error
        if new_root_str:
            self._dataset_root = Path(new_root_str)
        else:
            self._dataset_root = None
        self._dataset_root_user_set = True
        self._on_path_field_change()

    # ── parameter section (standard — empty_container) ─────────────────

    def _build_param_section_standard(self) -> None:
        cfg = self._cfg
        parent = self._param_container

        # Row 0: container + anomaly
        row0 = ttk.Frame(parent)
        row0.pack(fill=tk.X, pady=1)
        obj_label = getattr(cfg, "OBJECT_LABEL_CN", "容器:")
        ttk.Label(row0, text=obj_label, width=10).pack(side=tk.LEFT)
        self._container_var = tk.StringVar()
        self._container_cb = ttk.Combobox(
            row0, textvariable=self._container_var, state="readonly", width=30
        )
        self._container_cb.pack(side=tk.LEFT, padx=(0, 16))
        self._container_var.trace_add("write", self._on_container_change__std)

        ttk.Label(row0, text="异常类型:", width=10).pack(side=tk.LEFT)
        self._anomaly_var = tk.StringVar()
        self._anomaly_cb = ttk.Combobox(
            row0, textvariable=self._anomaly_var, state="readonly", width=30
        )
        self._anomaly_cb.pack(side=tk.LEFT)
        self._anomaly_var.trace_add("write", self._on_anomaly_change__std)

        # Row 1: subcategory + shooting point
        row1 = ttk.Frame(parent)
        row1.pack(fill=tk.X, pady=1)
        ttk.Label(row1, text="小类:", width=10).pack(side=tk.LEFT)
        self._sub_var = tk.StringVar()
        self._sub_cb = ttk.Combobox(
            row1, textvariable=self._sub_var, state="readonly", width=30
        )
        self._sub_cb.pack(side=tk.LEFT, padx=(0, 16))
        self._sub_var.trace_add("write", self._on_path_field_change)

        ttk.Label(row1, text="拍摄点位:", width=10).pack(side=tk.LEFT)
        self._point_var = tk.StringVar(
            value=cfg.SHOOTING_POINTS_CN_LIST[0]
            if getattr(cfg, "SHOOTING_POINTS_CN_LIST", None)
            else ""
        )
        self._point_cb = ttk.Combobox(
            row1,
            textvariable=self._point_var,
            values=getattr(cfg, "SHOOTING_POINTS_CN_LIST", []),
            width=28,
        )
        self._point_cb.pack(side=tk.LEFT)
        self._point_var.trace_add("write", self._on_path_field_change)

        # Row 2: view number
        row2 = ttk.Frame(parent)
        row2.pack(fill=tk.X, pady=1)
        ttk.Label(row2, text="视角编号:", width=10).pack(side=tk.LEFT)
        self._view_var = tk.StringVar(value="1")
        ttk.Entry(row2, textvariable=self._view_var, width=10).pack(side=tk.LEFT)
        self._view_var.trace_add("write", self._on_path_field_change)

        # Configured path preview (theoretical, regardless of existence)
        row_cfg = ttk.Frame(parent)
        row_cfg.pack(fill=tk.X, pady=(4, 0))
        ttk.Label(row_cfg, text="配置路径:", width=10).pack(side=tk.LEFT)
        self._config_path_var = tk.StringVar(value="(选择参数后显示)")
        ttk.Entry(
            row_cfg,
            textvariable=self._config_path_var,
            state="readonly",
            font=("Consolas", 9),
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Matched path preview (filesystem search result)
        row3 = ttk.Frame(parent)
        row3.pack(fill=tk.X, pady=(4, 0))
        ttk.Label(row3, text="匹配路径:", width=10).pack(side=tk.LEFT)
        self._match_path_var = tk.StringVar(value="(选择参数后自动匹配)")
        ttk.Entry(
            row3,
            textvariable=self._match_path_var,
            state="readonly",
            font=("Consolas", 9),
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Populate comboboxes
        self._populate_standard_params()

    # ── parameter section (material) ────────────────────────────────────

    def _build_param_section_material(self) -> None:
        cfg = self._cfg
        parent = self._param_container

        # Row 0: state + material
        row0 = ttk.Frame(parent)
        row0.pack(fill=tk.X, pady=1)
        ttk.Label(row0, text="材料状态:", width=10).pack(side=tk.LEFT)
        self._state_var = tk.StringVar()
        self._state_cb = ttk.Combobox(
            row0, textvariable=self._state_var, state="readonly", width=24
        )
        self._state_cb.pack(side=tk.LEFT, padx=(0, 16))
        self._state_var.trace_add("write", self._on_state_change__mat)

        ttk.Label(row0, text="具体材料:", width=10).pack(side=tk.LEFT)
        self._material_var = tk.StringVar()
        self._material_cb = ttk.Combobox(
            row0, textvariable=self._material_var, state="readonly", width=38
        )
        self._material_cb.pack(side=tk.LEFT)
        self._material_var.trace_add("write", self._on_path_field_change)

        # Row 1: anomaly + container
        row1 = ttk.Frame(parent)
        row1.pack(fill=tk.X, pady=1)
        ttk.Label(row1, text="异常类型:", width=10).pack(side=tk.LEFT)
        self._anomaly_var = tk.StringVar()
        self._anomaly_cb = ttk.Combobox(
            row1, textvariable=self._anomaly_var, state="readonly", width=30
        )
        self._anomaly_cb.pack(side=tk.LEFT, padx=(0, 16))
        self._anomaly_var.trace_add("write", self._on_path_field_change)

        ttk.Label(row1, text="容器种类:", width=10).pack(side=tk.LEFT)
        self._container_var = tk.StringVar()
        self._container_cb = ttk.Combobox(
            row1, textvariable=self._container_var, state="readonly", width=30
        )
        self._container_cb.pack(side=tk.LEFT)
        self._container_var.trace_add("write", self._on_container_change__mat)

        # Row 2: shooting point
        row2 = ttk.Frame(parent)
        row2.pack(fill=tk.X, pady=1)
        ttk.Label(row2, text="拍摄点位:", width=10).pack(side=tk.LEFT)
        self._point_var = tk.StringVar()
        self._point_cb = ttk.Combobox(
            row2, textvariable=self._point_var, state="readonly", width=30
        )
        self._point_cb.pack(side=tk.LEFT)
        self._point_var.trace_add("write", self._on_path_field_change)

        # Row 3: view number
        row3 = ttk.Frame(parent)
        row3.pack(fill=tk.X, pady=1)
        ttk.Label(row3, text="视角编号:", width=10).pack(side=tk.LEFT)
        self._view_var = tk.StringVar(value="1")
        ttk.Entry(row3, textvariable=self._view_var, width=10).pack(side=tk.LEFT)
        self._view_var.trace_add("write", self._on_path_field_change)

        # Configured path preview (theoretical, regardless of existence)
        row_cfg = ttk.Frame(parent)
        row_cfg.pack(fill=tk.X, pady=(4, 0))
        ttk.Label(row_cfg, text="配置路径:", width=10).pack(side=tk.LEFT)
        self._config_path_var = tk.StringVar(value="(选择参数后显示)")
        ttk.Entry(
            row_cfg,
            textvariable=self._config_path_var,
            state="readonly",
            font=("Consolas", 9),
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Matched path preview (filesystem search result)
        row4 = ttk.Frame(parent)
        row4.pack(fill=tk.X, pady=(4, 0))
        ttk.Label(row4, text="匹配路径:", width=10).pack(side=tk.LEFT)
        self._match_path_var = tk.StringVar(value="(选择参数后自动匹配)")
        ttk.Entry(
            row4,
            textvariable=self._match_path_var,
            state="readonly",
            font=("Consolas", 9),
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Populate comboboxes
        self._populate_material_params()

    # ── parameter population ────────────────────────────────────────────

    def _populate_standard_params(self) -> None:
        cfg = self._cfg
        items = [f"{k}: {v}" for k, v in sorted(cfg.CONTAINERS_CN.items())]
        self._container_cb["values"] = items  # type: ignore[index]
        if items:
            self._container_var.set(items[0])  # type: ignore[union-attr]
        self._update_anomalies__std()

    def _populate_material_params(self) -> None:
        cfg = self._cfg
        items = [
            f"{sid}: {cfg.MATERIAL_STATES_CN[sid]}"
            for sid in sorted(cfg.MATERIAL_STATES)
        ]
        self._state_cb["values"] = items  # type: ignore[index]
        if items:
            self._state_var.set(items[0])  # type: ignore[union-attr]
        self._update_material_dependent()

    # ── standard combobox callbacks ─────────────────────────────────────

    def _on_container_change__std(self, *_args) -> None:
        self._update_anomalies__std()

    def _on_anomaly_change__std(self, *_args) -> None:
        self._update_subcategories__std()

    def _update_anomalies__std(self) -> None:
        cfg = self._cfg
        text = (self._container_var or tk.StringVar()).get()
        if not text:
            return
        cid = _extract_id(text) or min(cfg.CONTAINERS)
        anomaly_ids = (
            cfg.get_anomaly_types(cid)
            if hasattr(cfg, "get_anomaly_types")
            else sorted(cfg.ANOMALY_TYPES)
        )
        cur = _extract_id((self._anomaly_var or tk.StringVar()).get())
        selected = cur if cur in anomaly_ids else anomaly_ids[0]
        items = [f"{a}: {cfg.ANOMALY_TYPES_CN[a]}" for a in anomaly_ids]
        self._anomaly_cb["values"] = items  # type: ignore[index]
        self._anomaly_var.set(f"{selected}: {cfg.ANOMALY_TYPES_CN[selected]}")  # type: ignore[union-attr]
        self._update_subcategories__std()

    def _update_subcategories__std(self) -> None:
        cfg = self._cfg
        aid_text = (self._anomaly_var or tk.StringVar()).get()
        cid_text = (self._container_var or tk.StringVar()).get()
        if not aid_text or not cid_text:
            return
        aid = _extract_id(aid_text) or 1
        cid = _extract_id(cid_text) or min(cfg.CONTAINERS)

        if hasattr(cfg, "get_anomaly_subcategories"):
            subs = cfg.get_anomaly_subcategories(cid, aid)
        else:
            subs = cfg.ANOMALY_SUBCATEGORIES.get(aid, [])

        no_sub = getattr(cfg, "NO_SUBCATEGORY", "-")
        if aid == 1 or not subs:
            self._sub_cb["state"] = tk.DISABLED  # type: ignore[index]
            self._sub_var.set(no_sub)  # type: ignore[union-attr]
            self._sub_cb["values"] = [no_sub]  # type: ignore[index]
        else:
            self._sub_cb["state"] = "readonly"  # type: ignore[index]
            subs_display = [cfg.ANOMALY_SUBCATEGORIES_CN.get(s, s) for s in subs]
            self._sub_cb["values"] = subs_display  # type: ignore[index]
            self._sub_var.set(subs_display[0])  # type: ignore[union-attr]

    # ── material combobox callbacks ─────────────────────────────────────

    def _on_state_change__mat(self, *_args) -> None:
        self._update_material_dependent()

    def _on_container_change__mat(self, *_args) -> None:
        self._update_material_points()

    def _update_material_dependent(self) -> None:
        cfg = self._cfg
        sid = _extract_id((self._state_var or tk.StringVar()).get())
        if sid is None:
            return

        _set_combo_options(
            self._material_cb,  # type: ignore[arg-type]
            self._material_var,  # type: ignore[arg-type]
            cfg.MATERIALS_CN[sid],
            _extract_id((self._material_var or tk.StringVar()).get()),
        )

        # gel (3) / solution (2) 状态下没有异常类型目录，禁用异常选择
        state_en = cfg.MATERIAL_STATES.get(sid, "")
        if state_en.lower() in ("gel", "solution"):
            self._anomaly_cb["state"] = tk.DISABLED  # type: ignore[index]
            self._anomaly_var.set("—")  # type: ignore[union-attr]
            self._anomaly_cb["values"] = ["—"]  # type: ignore[index]
        else:
            self._anomaly_cb["state"] = "readonly"  # type: ignore[index]
            anomaly_ids = (
                cfg.get_anomaly_types(sid)
                if hasattr(cfg, "get_anomaly_types")
                else sorted(cfg.ANOMALY_TYPES)
            )
            _set_combo_options(
                self._anomaly_cb,  # type: ignore[arg-type]
                self._anomaly_var,  # type: ignore[arg-type]
                {a: cfg.ANOMALY_TYPES_CN[a] for a in anomaly_ids},
                _extract_id((self._anomaly_var or tk.StringVar()).get()),
            )
        container_ids = (
            cfg.get_containers(sid)
            if hasattr(cfg, "get_containers")
            else sorted(cfg.CONTAINERS)
        )
        _set_combo_options(
            self._container_cb,  # type: ignore[arg-type]
            self._container_var,  # type: ignore[arg-type]
            {c: cfg.CONTAINERS_CN[c] for c in container_ids},
            _extract_id((self._container_var or tk.StringVar()).get()),
        )
        self._update_material_points()

    def _update_material_points(self) -> None:
        cfg = self._cfg
        sid = _extract_id((self._state_var or tk.StringVar()).get())
        cid = _extract_id((self._container_var or tk.StringVar()).get())
        if sid is None or cid is None:
            return
        points = cfg.get_shooting_points(sid, cid)
        items = [cfg.SHOOTING_POINTS[p] for p in points]
        self._point_cb["values"] = items  # type: ignore[index]
        cur = (self._point_var or tk.StringVar()).get()
        if cur not in items:
            self._point_var.set(items[0] if items else "")  # type: ignore[union-attr]

    # ── configured path display ──────────────────────────────────────────

    def _update_configured_path(self) -> None:
        """Build the theoretical dataset path from current selections and display it.

        This path is computed purely from the selected options — it does **not**
        check whether the directory actually exists on disk.

        The config modules define ``DATASET_ROOT = DATASET_BASE / "<category_dir>"``
        (e.g. ``…/material`` or ``…/empty_container``).  When the user overrides the
        root to the top-level ``DATASET_BASE``, we automatically prepend the
        category directory so the displayed path stays correct.
        """
        cfg = self._cfg
        root = self._dataset_root
        if root is None:
            self._config_path_var.set("(未设置数据集根目录)")  # type: ignore[union-attr]
            return

        point_view = self._get_point_view()
        if not point_view or point_view.endswith("-"):
            self._config_path_var.set("(请完善点位和视角参数)")  # type: ignore[union-attr]
            return

        # Ensure the category directory is part of the path.  The config's
        # DATASET_ROOT already includes it, but the user may have overridden
        # the root to the parent DATASET_BASE.
        if self._material_mode:
            expected_dir = "material"
        else:
            expected_dir = "empty_container"

        if root.name != expected_dir:
            root = root / expected_dir

        root_str = str(root)

        if self._material_mode:
            path = self._build_configured_path_material(root_str, point_view)
        else:
            path = self._build_configured_path_standard(root_str, point_view)

        if path is not None:
            self._config_path_var.set(path)  # type: ignore[union-attr]

    @staticmethod
    def _sanitize_name(name: str) -> str:
        """Replace Windows-forbidden characters in a single path segment."""
        return name.replace(":", "_")

    def _build_configured_path_standard(self, root_str: str, point_view: str) -> str | None:
        """Build path for empty_container (standard) mode."""
        cfg = self._cfg

        # Resolve container
        cont_text = (self._container_var or tk.StringVar()).get().strip()
        cont_id = _extract_id(cont_text)
        if cont_id is None:
            return "(请选择容器)"
        container_en = self._sanitize_name(cfg.CONTAINERS.get(cont_id, str(cont_id)))

        # Resolve anomaly type
        ano_text = (self._anomaly_var or tk.StringVar()).get().strip()
        ano_id = _extract_id(ano_text)
        if ano_id is None:
            return "(请选择异常类型)"
        anomaly_en = self._sanitize_name(cfg.ANOMALY_TYPES.get(ano_id, str(ano_id)))

        parts = [root_str, container_en, anomaly_en]

        # Subcategory (only for non-normal anomaly types)
        if ano_id != 1:
            sub_text = (self._sub_var or tk.StringVar()).get().strip()
            no_sub = getattr(cfg, "NO_SUBCATEGORY", "-")
            if sub_text and sub_text != no_sub:
                # sub_text could be Chinese display name — resolve to English
                subs_en_map = {v: k for k, v in cfg.ANOMALY_SUBCATEGORIES_CN.items()}
                sub_en = self._sanitize_name(subs_en_map.get(sub_text, sub_text))
                parts.append(sub_en)

        parts.append(point_view)
        return "/".join(parts)

    def _build_configured_path_material(self, root_str: str, point_view: str) -> str | None:
        """Build path for material mode.

        Directory structure::

            raw_material / original_solution:
                <root> / state / material / anomaly / container / point-view
            gel / solution (no anomaly level):
                <root> / state / material / container / point-view
        """
        cfg = self._cfg

        # Resolve state
        state_text = (self._state_var or tk.StringVar()).get().strip()
        state_id = _extract_id(state_text)
        if state_id is None:
            return "(请选择材料状态)"
        state_en = self._sanitize_name(cfg.MATERIAL_STATES.get(state_id, str(state_id)))

        # Resolve material
        mat_text = (self._material_var or tk.StringVar()).get().strip()
        mat_id = _extract_id(mat_text)
        if mat_id is None:
            return "(请选择具体材料)"
        materials_for_state = cfg.MATERIALS.get(state_id, {})
        material_en = self._sanitize_name(materials_for_state.get(mat_id, str(mat_id)))

        parts = [root_str, state_en, material_en]

        # gel / solution have no anomaly level, but still have container
        if state_en.lower() in ("gel", "solution"):
            # container only (no anomaly)
            cont_text = (self._container_var or tk.StringVar()).get().strip()
            cont_id = _extract_id(cont_text)
            if cont_id is not None:
                container_en = self._sanitize_name(cfg.CONTAINERS.get(cont_id, str(cont_id)))
                parts.append(container_en)
        else:
            # Resolve anomaly type
            ano_text = (self._anomaly_var or tk.StringVar()).get().strip()
            if ano_text != "—":
                ano_id = _extract_id(ano_text)
                if ano_id is not None:
                    anomaly_en = self._sanitize_name(cfg.ANOMALY_TYPES.get(ano_id, str(ano_id)))
                    parts.append(anomaly_en)

            # Resolve container
            cont_text = (self._container_var or tk.StringVar()).get().strip()
            cont_id = _extract_id(cont_text)
            if cont_id is not None:
                container_en = self._sanitize_name(cfg.CONTAINERS.get(cont_id, str(cont_id)))
                parts.append(container_en)

        parts.append(point_view)
        return "/".join(parts)

    # ── path field change → auto-resolve ────────────────────────────────

    def _on_path_field_change(self, *_args) -> None:
        """Any parameter changed → update configured path, resolve matching directories and show preview."""
        # Update the theoretical configured path immediately
        self._update_configured_path()
        # Cancel any pending resolution
        if self._search_after_id is not None:
            self.root.after_cancel(self._search_after_id)
        self._search_after_id = self.root.after(200, self._resolve_and_preview)

    # ── resolve directories & collect images ────────────────────────────

    def _get_point_view(self) -> str:
        """Build point_view string from current parameters."""
        cfg = self._cfg
        point_cn = (self._point_var or tk.StringVar()).get().strip()
        point_en = cfg.SHOOTING_POINTS_CN.get(point_cn, point_cn)
        view = (self._view_var or tk.StringVar()).get().strip()
        return f"{point_en}-{view}" if view else point_en

    def _get_required_tokens(self) -> list[str]:
        """Build the list of required ancestor tokens for directory matching."""
        cfg = self._cfg

        if self._material_mode:
            mat = (self._material_var or tk.StringVar()).get().strip()
            mat_en = _extract_id(mat)  # fallback: try numeric
            if mat_en is not None:
                sid = _extract_id((self._state_var or tk.StringVar()).get())
                mat_en_str = cfg.MATERIALS.get(sid or 0, {}).get(mat_en, str(mat_en))
            else:
                mat_en_str = mat
            # Normalise colons → underscores (config uses "01:polyvinyl_alcohol"
            # but Windows directories use "01_polyvinyl_alcohol").
            mat_en_str = mat_en_str.replace(":", "_")
            ano_text = (self._anomaly_var or tk.StringVar()).get().strip()
            ano_id = _extract_id(ano_text)
            ano_en = cfg.ANOMALY_TYPES.get(ano_id or 0, ano_text) if ano_id else ano_text
            cont_text = (self._container_var or tk.StringVar()).get().strip()
            cont_id = _extract_id(cont_text)
            cont_en = cfg.CONTAINERS.get(cont_id or 0, cont_text) if cont_id else cont_text
            state_text = (self._state_var or tk.StringVar()).get().strip()
            state_id = _extract_id(state_text)
            state_en = cfg.MATERIAL_STATES.get(state_id or 0, state_text) if state_id else state_text
            # gel / solution 没有异常类型目录层级，不按 anomaly 过滤
            if state_en.lower() in ("gel", "solution"):
                return [mat_en_str, state_en]
            else:
                return split_multi(ano_en) + [mat_en_str, cont_en, state_en]
        else:
            ano_text = (self._anomaly_var or tk.StringVar()).get().strip()
            ano_id = _extract_id(ano_text)
            ano_en = cfg.ANOMALY_TYPES.get(ano_id or 0, ano_text) if ano_id else ano_text
            cont_text = (self._container_var or tk.StringVar()).get().strip()
            cont_id = _extract_id(cont_text)
            cont_en = cfg.CONTAINERS.get(cont_id or 0, cont_text) if cont_id else cont_text
            tokens = split_multi(ano_en) + [cont_en]

            sub = (self._sub_var or tk.StringVar()).get().strip()
            no_sub = getattr(cfg, "NO_SUBCATEGORY", "-")
            if sub and sub != no_sub:
                subs_en = {v: k for k, v in cfg.ANOMALY_SUBCATEGORIES_CN.items()}
                tokens += split_multi(subs_en.get(sub, sub))
            return tokens

    def _resolve_and_preview(self) -> None:
        """Match dataset directories in a background thread, then show first image."""
        self._search_after_id = None
        root = self._dataset_root
        point_view = self._get_point_view()
        required = self._get_required_tokens()

        if not root or not root.is_dir():
            self._match_path_var.set("(数据集根目录不存在)")
            self._clear_preview()
            return
        if not point_view or point_view.endswith("-"):
            self._match_path_var.set("(请完善点位和视角参数)")
            return

        self._match_path_var.set("正在搜索...")
        gen = self._search_gen = self._search_gen + 1

        # When in empty_container mode, exclude directories whose ancestor path
        # contains material state names (raw_material, solution, gel, …).
        # This prevents matching material-structured directories when both
        # datasets happen to share a common root.
        _material_state_names: set[str] = set()
        if not self._material_mode and self._cfg_material is not None:
            _material_state_names = set(
                getattr(self._cfg_material, "MATERIAL_STATES", {}).values()
            )

        def _search() -> None:
            try:
                dirs = resolve_dirs(
                    root,
                    point_view,
                    required,
                    exclude_ancestor_tokens=_material_state_names or None,
                )
            except SystemExit:
                dirs = []

            if gen != self._search_gen:
                return  # stale result

            if not dirs:
                self.root.after(0, self._on_search_done, [], "(未找到匹配目录)")
                return

            all_images: list[Path] = []
            for d in dirs:
                all_images.extend(collect_images(d))

            if not all_images:
                rel = dirs[0].relative_to(root) if dirs else "?"
                self.root.after(0, self._on_search_done, [], f"{rel} (无图片)")
                return

            rel = (
                str(dirs[0].relative_to(root))
                if len(dirs) == 1
                else f"{len(dirs)} 个目录"
            )
            self.root.after(
                0, self._on_search_done, all_images, f"{rel}，{len(all_images)} 张图片"
            )

        t = threading.Thread(target=_search, daemon=True)
        t.start()

    def _on_search_done(
        self, images: list[Path], info: str
    ) -> None:
        """Update UI after background search completes."""
        self._match_path_var.set(info)
        self._current_images = images
        self._current_index = 0
        if images:
            self._show_image(0)
        else:
            self._clear_preview()

    # ── image preview ───────────────────────────────────────────────────

    def _build_preview_section(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="图片预览", padding=4)
        frame.pack(fill=tk.BOTH, expand=True)

        # Info bar
        info = ttk.Frame(frame)
        info.pack(fill=tk.X, pady=(0, 2))
        self._img_count_var = tk.StringVar(value="0 / 0")
        ttk.Label(info, textvariable=self._img_count_var, font=("Consolas", 10)).pack(
            side=tk.LEFT
        )
        self._img_info_var = tk.StringVar()
        ttk.Label(
            info, textvariable=self._img_info_var, font=("Consolas", 9), foreground="gray"
        ).pack(side=tk.RIGHT)

        if HAS_PIL:
            self._preview_label = ttk.Label(
                frame,
                text="请选择抓取参数",
                anchor=tk.CENTER,
                background="#1e1e1e",
                foreground="#999999",
                font=("微软雅黑", 12),
            )
            self._preview_label.pack(fill=tk.BOTH, expand=True)
        else:
            self._preview_label = ttk.Label(
                frame,
                text="⚠ Pillow 未安装\n请执行: pip install Pillow\n\n仍可添加和打包，但无法预览图片",
                anchor=tk.CENTER,
            )
            self._preview_label.pack(fill=tk.BOTH, expand=True)

        # Stage selector
        stage_row = ttk.Frame(frame)
        stage_row.pack(fill=tk.X, pady=(4, 0))
        ttk.Label(stage_row, text="Stage:").pack(side=tk.LEFT, padx=(0, 8))
        self._stage_var = tk.StringVar(value="raw")
        self._stage_cb = ttk.Combobox(
            stage_row,
            textvariable=self._stage_var,
            state="readonly",
            values=["raw", "process", "finished"],
            width=12,
        )
        self._stage_cb.pack(side=tk.LEFT)

        # Navigation buttons
        nav = ttk.Frame(frame)
        nav.pack(fill=tk.X, pady=(4, 0))
        self._prev_btn = ttk.Button(nav, text="◀ 上一张", command=self._prev_image)
        self._prev_btn.pack(side=tk.LEFT, padx=(0, 4))
        self._add_btn = ttk.Button(
            nav, text="➕ 添加当前图片", command=self._add_current_image
        )
        self._add_btn.pack(side=tk.LEFT, padx=(0, 4))
        self._next_btn = ttk.Button(nav, text="▶ 下一张", command=self._next_image)
        self._next_btn.pack(side=tk.LEFT)

    def _show_image(self, index: int) -> None:
        """Display the image at *index* in the preview area."""
        if not self._current_images:
            self._clear_preview()
            return

        total = len(self._current_images)
        if index < 0:
            index = total - 1
        elif index >= total:
            index = 0
        self._current_index = index

        path = self._current_images[index]
        self._img_count_var.set(f"{index + 1} / {total}")
        self._img_info_var.set(f"{path.name}")

        if not HAS_PIL:
            self._preview_label.configure(
                image="",
                text=f"[{index + 1}/{total}]\n{path.name}\n{path}",
            )
            return

        try:
            img = cv2.imread(str(path))
            if img is None:
                self._preview_label.configure(
                    image="", text=f"无法读取:\n{path.name}"
                )
                return

            h, w = img.shape[:2]
            scale = min(PREVIEW_WIDTH / w, PREVIEW_HEIGHT / h, 1.0)
            new_w, new_h = max(1, int(w * scale)), max(1, int(h * scale))
            resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
            rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(rgb)
            self._imgtk = ImageTk.PhotoImage(image=pil_img)
            self._preview_label.configure(image=self._imgtk, text="")
        except Exception as exc:
            self._preview_label.configure(image="", text=f"预览失败:\n{exc}")

    def _clear_preview(self) -> None:
        self._imgtk = None
        self._img_count_var.set("0 / 0")
        self._img_info_var.set("")
        if HAS_PIL:
            self._preview_label.configure(
                image="",
                text="请选择抓取参数",
                background="#1e1e1e",
                foreground="#999999",
            )

    def _prev_image(self) -> None:
        if self._current_images:
            self._show_image(self._current_index - 1)

    def _next_image(self) -> None:
        if self._current_images:
            self._show_image(self._current_index + 1)

    def _build_image_item(self) -> dict | None:
        """构建当前预览图片的条目字典，无预览时返回 None。"""
        if not self._current_images:
            return None
        path = self._current_images[self._current_index]
        dir_name = path.parent.name
        category = CATEGORY_MATERIAL if self._material_mode else CATEGORY_EMPTY

        ano_display = ""
        type_display = ""
        if self._anomaly_var:
            ano_text = self._anomaly_var.get()
            ano_display = ano_text.split(":", 1)[-1].strip() if ":" in ano_text else ano_text
        if self._material_mode:
            if self._material_var:
                mat_text = self._material_var.get()
                type_display = mat_text.split(":", 1)[-1].strip() if ":" in mat_text else mat_text
        else:
            if self._container_var:
                cont_text = self._container_var.get()
                type_display = cont_text.split(":", 1)[-1].strip() if ":" in cont_text else cont_text

        return {
            "path": path,
            "dir_name": dir_name,
            "category": category,
            "anomaly": ano_display,
            "type_info": type_display,
            "stage": self._stage_var.get().strip() if self._stage_var else "raw",
        }

    def _add_current_image(self) -> None:
        """Add the currently displayed image to the end of the grab list."""
        item = self._build_image_item()
        if item is None:
            messagebox.showwarning("无图片", "请先选择参数匹配到图片后再添加。")
            return

        self._image_list.append(item)
        self._refresh_treeview()
        self._pack_btn["state"] = tk.NORMAL
        self._log(
            f"已添加: {item['path'].name}  "
            f"异常={item['anomaly']}  "
            f"类型={item['type_info']}"
        )

    def _on_insert_after(self) -> None:
        """在当前选中的条目下方插入一张图片；未选中则追加到末尾。"""
        item = self._build_image_item()
        if item is None:
            messagebox.showwarning("无图片", "请先选择参数匹配到图片后再添加。")
            return

        selected = self._tree.selection()
        if selected:
            insert_idx = self._tree.index(selected[0]) + 1
        else:
            insert_idx = len(self._image_list)

        self._image_list.insert(insert_idx, item)
        self._refresh_treeview()
        self._pack_btn["state"] = tk.NORMAL
        # 选中新插入的行
        children = self._tree.get_children()
        if insert_idx < len(children):
            self._tree.selection_set(children[insert_idx])
        self._log(
            f"已插入 (#{insert_idx + 1}): {item['path'].name}  "
            f"异常={item['anomaly']}  "
            f"类型={item['type_info']}"
        )

    # ── image list ──────────────────────────────────────────────────────

    def _build_list_section(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="已选图片列表", padding=4)
        frame.pack(fill=tk.BOTH, expand=False)

        columns = ("idx", "anomaly", "dir", "type_info", "stage")
        self._tree = ttk.Treeview(frame, columns=columns, show="headings", height=6)
        self._tree.heading("idx", text="#")
        self._tree.heading("anomaly", text="异常类型")
        self._tree.heading("dir", text="目录 (点位-视角)")
        self._tree.heading("type_info", text="材料类型/容器类型")
        self._tree.heading("stage", text="Stage")
        self._tree.column("idx", width=36, anchor=tk.CENTER)
        self._tree.column("anomaly", width=120)
        self._tree.column("dir", width=160)
        self._tree.column("type_info", width=130)
        self._tree.column("stage", width=70, anchor=tk.CENTER)

        vsb = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        self._tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        btn_row = ttk.Frame(frame)
        btn_row.pack(fill=tk.X, pady=(4, 0))
        ttk.Button(btn_row, text="移除选中", command=self._on_remove).pack(
            side=tk.LEFT, padx=(0, 4)
        )
        ttk.Button(btn_row, text="清空列表", command=self._on_clear).pack(
            side=tk.LEFT, padx=(0, 4)
        )
        ttk.Button(btn_row, text="↑ 上移", command=self._on_move_up).pack(
            side=tk.LEFT, padx=(0, 4)
        )
        ttk.Button(btn_row, text="↓ 下移", command=self._on_move_down).pack(
            side=tk.LEFT, padx=(0, 4)
        )
        ttk.Button(btn_row, text="▼ 插入到选中下方", command=self._on_insert_after).pack(
            side=tk.LEFT, padx=(0, 4)
        )
        self._list_count_var = tk.StringVar(value="共 0 张")
        ttk.Label(btn_row, textvariable=self._list_count_var).pack(
            side=tk.RIGHT, padx=(8, 0)
        )

    def _refresh_treeview(self) -> None:
        for row in self._tree.get_children():
            self._tree.delete(row)
        for i, item in enumerate(self._image_list, 1):
            self._tree.insert(
                "",
                tk.END,
                values=(
                    i,
                    item.get("anomaly", ""),
                    item["dir_name"],
                    item.get("type_info", ""),
                    item.get("stage", "raw"),
                ),
            )
        self._list_count_var.set(f"共 {len(self._image_list)} 张")

    def _on_remove(self) -> None:
        selected = self._tree.selection()
        if not selected:
            return
        indices = sorted(
            (self._tree.index(s) for s in selected), reverse=True
        )
        for idx in indices:
            if 0 <= idx < len(self._image_list):
                removed = self._image_list.pop(idx)
                self._log(f"已移除: {removed['path'].name}")
        self._refresh_treeview()
        if not self._image_list:
            self._pack_btn["state"] = tk.DISABLED

    def _on_clear(self) -> None:
        if not self._image_list:
            return
        if messagebox.askyesno("确认清空", "确定要清空所有已选图片吗？"):
            self._image_list.clear()
            self._refresh_treeview()
            self._pack_btn["state"] = tk.DISABLED
            self._log("已清空图片列表")

    def _on_move_up(self) -> None:
        selected = self._tree.selection()
        if not selected:
            return
        idx = self._tree.index(selected[0])
        if idx <= 0:
            return
        self._image_list[idx], self._image_list[idx - 1] = (
            self._image_list[idx - 1],
            self._image_list[idx],
        )
        self._refresh_treeview()
        # Re-select moved item
        children = self._tree.get_children()
        if idx - 1 < len(children):
            self._tree.selection_set(children[idx - 1])

    def _on_move_down(self) -> None:
        selected = self._tree.selection()
        if not selected:
            return
        idx = self._tree.index(selected[0])
        if idx >= len(self._image_list) - 1:
            return
        self._image_list[idx], self._image_list[idx + 1] = (
            self._image_list[idx + 1],
            self._image_list[idx],
        )
        self._refresh_treeview()
        children = self._tree.get_children()
        if idx + 1 < len(children):
            self._tree.selection_set(children[idx + 1])

    # ── output section ──────────────────────────────────────────────────

    def _build_output_section(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="输出设置", padding=6)
        frame.pack(fill=tk.X)

        ttk.Label(frame, text="描述说明:").pack(anchor=tk.W)
        self._desc_text = scrolledtext.ScrolledText(
            frame, height=3, font=("微软雅黑", 9), wrap=tk.WORD
        )
        self._desc_text.insert(
            tk.END, "在此输入描述文本…（可选，会写入 description.txt）"
        )
        self._desc_text.pack(fill=tk.X, pady=(2, 4))

        # module.json metadata fields
        mod_row = ttk.Frame(frame)
        mod_row.pack(fill=tk.X, pady=(0, 2))
        ttk.Label(mod_row, text="Process ID:", width=14).pack(side=tk.LEFT)
        self._process_id_var = tk.StringVar()
        ttk.Entry(
            mod_row, textvariable=self._process_id_var, font=("Consolas", 9), width=28
        ).pack(side=tk.LEFT, padx=(0, 12))
        ttk.Label(mod_row, text="流程名称:", width=10).pack(side=tk.LEFT)
        self._name_var = tk.StringVar()
        ttk.Entry(
            mod_row, textvariable=self._name_var, font=("微软雅黑", 9), width=28
        ).pack(side=tk.LEFT)

        row = ttk.Frame(frame)
        row.pack(fill=tk.X)
        ttk.Label(row, text="输出目录:").pack(side=tk.LEFT)
        default_out = (
            Path(__file__).resolve().parent
            / "grabbed"
            / datetime.now().strftime("%Y%m%d_%H%M%S")
        )
        self._out_dir_var = tk.StringVar(value=str(default_out))
        ttk.Entry(
            row, textvariable=self._out_dir_var, font=("Consolas", 9)
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 4))
        ttk.Button(row, text="浏览...", command=self._on_browse_out_dir).pack(
            side=tk.LEFT
        )

    def _on_browse_out_dir(self) -> None:
        d = filedialog.askdirectory(title="选择输出目录")
        if d:
            self._out_dir_var.set(d)

    # ── sequence load / save ────────────────────────────────────────────

    def _on_load_sequence(self) -> None:
        """弹出文件对话框，加载 JSON 或 CSV 序列文件。"""
        path_str = filedialog.askopenfilename(
            title="加载序列文件",
            filetypes=[
                ("序列文件", "*.json *.csv"),
                ("JSON 文件", "*.json"),
                ("CSV 文件", "*.csv"),
                ("所有文件", "*.*"),
            ],
        )
        if not path_str:
            return
        self._load_sequence_from_file(Path(path_str))

    def _load_sequence_from_file(self, file_path: Path) -> None:
        """从 JSON 或 CSV 文件加载图片序列到列表中。"""
        if not file_path.is_file():
            messagebox.showwarning("文件不存在", f"序列文件不存在:\n{file_path}")
            return

        items_data: list[dict] = []
        desc = ""
        try:
            raw = file_path.read_text(encoding="utf-8")
            if file_path.suffix.lower() == ".json":
                data = json.loads(raw)
                desc = data.get("description", "")
                items_data = data.get("items", [])
            elif file_path.suffix.lower() == ".csv":
                import io
                reader = csv.DictReader(io.StringIO(raw))
                for row in reader:
                    items_data.append({
                        "source": row.get("source", ""),
                        "dir_name": row.get("dir_name", ""),
                        "category": row.get("category", ""),
                        "anomaly": row.get("anomaly", ""),
                        "type_info": row.get("type_info", ""),
                        "stage": row.get("stage", "raw"),
                    })
            else:
                messagebox.showwarning("不支持的格式", f"请选择 .json 或 .csv 文件。")
                return
        except Exception as exc:
            messagebox.showerror("加载失败", f"无法解析序列文件:\n{exc}")
            return

        if not items_data:
            messagebox.showwarning("空序列", "序列文件中没有条目。")
            return

        loaded = 0
        skipped = 0
        for item_data in items_data:
            src_str = item_data.get("source", "")
            src = Path(src_str) if src_str else None
            if src is None or not src.is_file():
                skipped += 1
                self._log(f"  ⚠ 文件不存在，跳过: {src}")
                continue
            self._image_list.append({
                "path": src,
                "dir_name": item_data.get("dir_name", src.parent.name),
                "category": item_data.get("category", ""),
                "anomaly": item_data.get("anomaly", ""),
                "type_info": item_data.get("type_info", ""),
                "stage": item_data.get("stage", "raw"),
            })
            loaded += 1

        if desc:
            self._desc_text.delete("1.0", tk.END)
            self._desc_text.insert(tk.END, desc)

        self._refresh_treeview()
        if self._image_list:
            self._pack_btn["state"] = tk.NORMAL
        self._log(
            f"已加载序列: {file_path.name} "
            f"(成功 {loaded} 张, 跳过 {skipped} 张)"
        )

    # ── action section ──────────────────────────────────────────────────

    def _build_action_section(self, parent: ttk.Frame) -> None:
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=4)
        self._pack_btn = ttk.Button(
            frame,
            text="📦 打包 (Zip)",
            command=self._on_pack,
            state=tk.DISABLED,
        )
        self._pack_btn.pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(
            frame,
            text="📂 加载序列",
            command=self._on_load_sequence,
        ).pack(side=tk.LEFT, padx=(0, 8))

    # ── log section ─────────────────────────────────────────────────────

    def _build_log_section(self, parent: ttk.Frame) -> None:
        ttk.Label(parent, text="日志:").pack(anchor=tk.W, pady=(4, 0))
        self._log_area = scrolledtext.ScrolledText(
            parent,
            height=6,
            font=("Consolas", 9),
            wrap=tk.WORD,
            state=tk.DISABLED,
        )
        self._log_area.pack(fill=tk.BOTH, expand=True)

    def _log(self, msg: str) -> None:
        self._log_area["state"] = tk.NORMAL
        self._log_area.insert(tk.END, msg + "\n")
        self._log_area.see(tk.END)
        self._log_area["state"] = tk.DISABLED

    # ── keyboard shortcuts ──────────────────────────────────────────────

    def _setup_keyboard(self) -> None:
        self.root.bind("<Left>", self._on_key_left)
        self.root.bind("<Right>", self._on_key_right)
        self.root.bind("<space>", self._on_key_space)

    def _is_editable_focused(self) -> bool:
        """Return True if focus is on a text-entry widget."""
        focus = self.root.focus_get()
        if focus is None:
            return False
        if isinstance(focus, tk.Text):
            try:
                return str(focus.cget("state")) == "normal"
            except tk.TclError:
                return False
        if isinstance(focus, (tk.Entry, ttk.Entry)):
            try:
                return str(focus.cget("state")) != "disabled"
            except tk.TclError:
                return True
        if isinstance(focus, ttk.Combobox):
            try:
                return str(focus.cget("state")) != "readonly"
            except tk.TclError:
                return False
        return False

    def _on_key_left(self, _event: tk.Event) -> None:
        if not self._is_editable_focused():
            self._prev_image()

    def _on_key_right(self, _event: tk.Event) -> None:
        if not self._is_editable_focused():
            self._next_image()

    def _on_key_space(self, _event: tk.Event) -> None:
        if not self._is_editable_focused():
            self._add_current_image()

    # ── pack ────────────────────────────────────────────────────────────

    def _on_pack(self) -> None:
        if self._packing:
            return
        if not self._image_list:
            messagebox.showwarning("列表为空", "请先添加至少一张图片。")
            return

        out_dir_str = self._out_dir_var.get().strip()
        if not out_dir_str:
            messagebox.showwarning("未指定输出目录", "请先设置输出目录。")
            return
        out_dir = Path(out_dir_str)
        if not out_dir.is_absolute():
            out_dir = (Path(__file__).resolve().parent / out_dir).resolve()

        if out_dir.exists() and any(out_dir.iterdir()):
            if not messagebox.askyesno(
                "目录已存在", f"输出目录已有文件:\n{out_dir}\n\n是否继续？"
            ):
                return

        self._packing = True
        self._pack_btn["state"] = tk.DISABLED
        desc = self._desc_text.get("1.0", tk.END).strip()
        if desc == "在此输入描述文本…（可选，会写入 description.txt）":
            desc = ""
        items = list(self._image_list)

        self._log(f"开始打包 {len(items)} 张图片 → {out_dir} ...")
        t = threading.Thread(
            target=self._do_pack_in_thread, args=(out_dir, items, desc), daemon=True
        )
        t.start()

    def _do_pack_in_thread(
        self, out_dir: Path, items: list[dict], desc: str
    ) -> None:
        try:
            out_dir.mkdir(parents=True, exist_ok=True)
            self.root.after(0, self._log, f"输出目录: {out_dir}")

            # ═════════════════════════════════════════════════════════════
            # Phase 1 — 编号命名：为每张图片确定唯一的扁平文件名
            #            （与子文件夹无关，仅按步骤+视角编号）
            # ═════════════════════════════════════════════════════════════
            named_photos: list[tuple[dict, str]] = []  # (item, base_name)
            used_flat_names: set[str] = set()
            prev_step_key: str | None = None
            step_num = 0

            for idx, item in enumerate(items, 1):
                src = item["path"]
                if not src.is_file():
                    self.root.after(0, self._log, f"  ⚠ 文件不存在，跳过: {src}")
                    continue

                dn = item.get("dir_name", "")
                vn = view_number_of(dn)
                # 步骤键：完整父目录 + 点位名（不含视角编号后缀）
                # 用于判断是否与上一张图片属于同一点位
                if vn is not None:
                    step_key = str(src.parent.parent / dn.rsplit("-", 1)[0])
                else:
                    step_key = str(src.parent)

                if prev_step_key is None or step_key != prev_step_key:
                    step_num += 1
                    prev_step_key = step_key

                ext = src.suffix.lower()
                if ext not in IMAGE_EXTS:
                    ext = src.suffix or ".png"

                if vn is not None:
                    base_name = f"{step_num:02d}-{vn:03d}{ext}"
                else:
                    base_name = f"{step_num:02d}{ext}"

                # 碰撞安全：扁平命名空间内保证唯一
                while base_name in used_flat_names:
                    step_num += 1
                    if vn is not None:
                        base_name = f"{step_num:02d}-{vn:03d}{ext}"
                    else:
                        base_name = f"{step_num:02d}{ext}"
                used_flat_names.add(base_name)

                named_photos.append((item, base_name))

                if idx % 10 == 0 or idx == len(items):
                    self.root.after(
                        0, self._log,
                        f"  已编号 {len(named_photos)}/{len(items)} ...",
                    )

            total = len(named_photos)
            self.root.after(0, self._log, f"编号完成，共 {total} 张图片")

            if total == 0:
                self.root.after(0, self._on_pack_error, "没有成功复制任何图片")
                return

            # ═════════════════════════════════════════════════════════════
            # Phase 2 — 归档：按 stage 分配到子文件夹，复制文件
            #          （命名已确定，此处只负责文件夹分配与文件复制）
            # ═════════════════════════════════════════════════════════════
            manifest_rows: list[dict] = []
            used_destrels: set[str] = set()

            for i, (item, base_name) in enumerate(named_photos, 1):
                src = item["path"]
                stage = item.get("stage", "raw")
                dest_rel = f"{stage}/{base_name}"

                # 处理极端情况下的跨 stage 冲突
                while dest_rel in used_destrels:
                    stem, dot, ext = base_name.rpartition(".")
                    ext = ("." + ext) if dot else ""
                    base_name = f"{stem}_2{ext}"
                    dest_rel = f"{stage}/{base_name}"
                used_destrels.add(dest_rel)

                dest = out_dir / dest_rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(str(src), str(dest))

                manifest_rows.append(
                    {
                        "output": dest_rel,
                        "source": str(src),
                        "dir_name": item.get("dir_name", ""),
                        "category": item.get("category", ""),
                        "anomaly": item.get("anomaly", ""),
                        "type_info": item.get("type_info", ""),
                        "stage": stage,
                    }
                )
                if i % 10 == 0 or i == total:
                    self.root.after(
                        0, self._log, f"  已归档 {i}/{total} ..."
                    )

            self.root.after(0, self._log, f"归档完成，共 {total} 张图片")

            # description.txt
            desc_path = out_dir / "description.txt"
            with desc_path.open("w", encoding="utf-8") as fh:
                if desc:
                    fh.write(desc)
                    if not desc.endswith("\n"):
                        fh.write("\n")
                    fh.write("\n")
                fh.write("# ---- 打包清单 (自动生成) ----\n")
                for r in manifest_rows:
                    fh.write(f"# {r['output']}  <-  {r['source']}\n")
            self.root.after(0, self._log, f"已写入描述: {desc_path.name}")

            # manifest.csv
            csv_path = out_dir / "manifest.csv"
            with csv_path.open("w", encoding="utf-8", newline="") as fh:
                writer = csv.DictWriter(
                    fh, fieldnames=["output", "source", "dir_name", "category", "anomaly", "type_info", "stage"]
                )
                writer.writeheader()
                writer.writerows(manifest_rows)
            self.root.after(0, self._log, f"已写入清单: {csv_path.name}")

            # sequence.json
            seq_path = out_dir / "sequence.json"
            seq_data = {
                "description": desc,
                "created": datetime.now().isoformat(),
                "items": [
                    {
                        "source": r["source"],
                        "dir_name": r.get("dir_name", ""),
                        "category": r.get("category", ""),
                        "anomaly": r.get("anomaly", ""),
                        "type_info": r.get("type_info", ""),
                        "stage": r.get("stage", "raw"),
                    }
                    for r in manifest_rows
                ],
            }
            with seq_path.open("w", encoding="utf-8") as fh:
                json.dump(seq_data, fh, ensure_ascii=False, indent=2)
            self.root.after(0, self._log, f"已写入序列: {seq_path.name}")

            # module.json
            process_id = (self._process_id_var.get().strip() if self._process_id_var else "")
            mod_name = (self._name_var.get().strip() if self._name_var else "")
            module_json = generate_module_json(
                manifest_rows, desc, process_id=process_id, name=mod_name
            )
            module_path = out_dir / "module.json"
            with module_path.open("w", encoding="utf-8") as fh:
                json.dump(module_json, fh, ensure_ascii=False, indent=2)
            self.root.after(0, self._log, f"已写入模块: {module_path.name}")

            # ── 按 stage 拆分 manifest.json 到各子文件夹 ──
            stages_seen: set[str] = {r["stage"] for r in manifest_rows}
            for stage_name in sorted(stages_seen):
                stage_images = [
                    img for img in module_json["images"]
                    if img["file"].startswith(f"{stage_name}/")
                ]
                stage_manifest = {
                    "schema_version": module_json["schema_version"],
                    "process_id": module_json["process_id"],
                    "name": module_json["name"],
                    "version": module_json["version"],
                    "images": stage_images,
                }
                stage_manifest_path = out_dir / stage_name / "manifest.json"
                with stage_manifest_path.open("w", encoding="utf-8") as fh:
                    json.dump(stage_manifest, fh, ensure_ascii=False, indent=2)
                self.root.after(
                    0, self._log,
                    f"  已写入阶段清单: {stage_name}/manifest.json ({len(stage_images)} 张)",
                )

            # Zip
            self.root.after(0, self._log, "正在打包压缩包...")
            zip_path = shutil.make_archive(str(out_dir), "zip", out_dir)
            self.root.after(0, self._on_pack_done, zip_path, total)

        except Exception as exc:
            self.root.after(0, self._on_pack_error, f"打包失败: {exc}")

    def _on_pack_done(self, zip_path: str, total: int) -> None:
        self._log(f"✓ 打包完成: {zip_path}")
        self._log(f"  共 {total} 张图片")
        self._packing = False
        self._pack_btn["state"] = tk.NORMAL
        if messagebox.askyesno(
            "打包完成",
            f"打包完成!\n共 {total} 张图片\n\n压缩包:\n{zip_path}\n\n是否打开输出目录？",
        ):
            try:
                import os
                os.startfile(str(Path(zip_path).parent))
            except Exception:
                pass

    def _on_pack_error(self, error_msg: str) -> None:
        self._log(f"✗ {error_msg}")
        messagebox.showerror("打包失败", error_msg)
        self._packing = False
        self._pack_btn["state"] = tk.NORMAL

    # ── shutdown ────────────────────────────────────────────────────────

    def _on_close(self) -> None:
        self.root.destroy()


# ── entry point ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    GrabGui(root)
    root.mainloop()
