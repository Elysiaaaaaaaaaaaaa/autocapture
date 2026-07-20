#!/usr/bin/env python3
"""Live-preview capture GUI — streams all three cameras and captures frames
directly from the video feed without restarting pipelines.

Usage::

    python -m preview_mode.preview_gui          # from project root
    python preview_mode/preview_gui.py          # from project root
"""

from __future__ import annotations

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

from path_config_standard import (
    ANOMALY_SUBCATEGORIES,
    ANOMALY_TYPES,
    CONTAINERS,
    DATASET_ROOT,
    NO_SUBCATEGORY,
    ORBBEC_C1_SERIAL,
    build_shot_dir,
)
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

# ── constants ─────────────────────────────────────────────────────────────

PREVIEW_WIDTH = 640
PREVIEW_HEIGHT = 480
FRAME_INTERVAL_MS = 33  # ~30 fps

CAMERA_LABELS: dict[str, str] = {
    REALSENSE: "RealSense",
    ORBBEC_C1: "Orbbec C1",
    ORBBEC_C2: "Orbbec C2",
}

SHOOTING_POINTS = [
    "magnetic_stirrer_01", "magnetic_stirrer_02",
    "beaker_sample_carousel", "plate_reservoir_sample_carousel",
    "mixed_sample_carousel", "analytical_balance", "transfer_stage",
    "ultrasonic_cleaner_slot_01", "ultrasonic_cleaner_slot_02",
    "ultrasonic_cleaner_slot_03", "pipetting_station",
    "mixer1", "mixer2", "stack1", "stack3",
    "tianping", "zhuanyi",
]

SHOOTING_POINTS_CN = {
    "磁力搅拌器1": "magnetic_stirrer_01",
    "磁力搅拌器2": "magnetic_stirrer_02",
    "烧杯样品盘": "beaker_sample_carousel",
    "孔板/储液槽样品盘": "plate_reservoir_sample_carousel",
    "混合样品盘": "mixed_sample_carousel",
    "分析天平": "analytical_balance",
    "转移台": "transfer_stage",
    "超声波清洗机槽1": "ultrasonic_cleaner_slot_01",
    "超声波清洗机槽2": "ultrasonic_cleaner_slot_02",
    "超声波清洗机槽3": "ultrasonic_cleaner_slot_03",
    "移液站": "pipetting_station",
    "搅拌器1": "mixer1",
    "搅拌器2": "mixer2",
    "堆栈1": "stack1",
    "堆栈3": "stack3",
    "天平": "tianping",
    "转移": "zhuanyi",
}

SHOOTING_POINTS_CN_LIST = list(SHOOTING_POINTS_CN.keys())

CONTAINERS_CN: dict[int, str] = {
    1: "烧杯", 2: "试管模型1", 3: "试管模型2",
    4: "6孔板", 5: "11孔板", 6: "24孔板",
    7: "48孔板", 8: "96孔板模型1",
    9: "96孔板模型2", 10: "磁力搅拌器1",
    11: "磁力搅拌器2", 12: "储液槽", 13: "超声波清洗机",
}

ANOMALY_TYPES_CN: dict[int, str] = {
    1: "正常", 2: "污渍", 3: "破损", 4: "液体残留",
    5: "固体残留", 6: "盖子异常", 7: "标签异常", 8: "摆放错误",
}

ANOMALY_SUBCATEGORIES_CN: dict[str, str] = {
    "water_stain": "水渍", "pigment_stain": "颜料污渍",
    "scratch": "划痕", "crack": "裂痕",
    "colorless_liquid": "无色液体", "colored_clear_liquid": "带颜色透明液体",
    "turbid_liquid": "浑浊液体", "wall_liquid_residue": "杯壁液体",
    "powder": "粉末", "crystalline_residue": "结晶残留",
    "cracked_lid": "盖子裂痕", "incorrect_lid": "盖子盖错", "missing_lid": "没有盖子",
    "label_soiling": "标签脏污", "label_detachment": "标签脱落", "label_damage": "标签破损",
    "tilted_placement": "斜放",
}


# ────────────────────────────────────────────────────────────────────────────
# PreviewCaptureGUI
# ────────────────────────────────────────────────────────────────────────────


class PreviewCaptureGUI:
    """Standalone tkinter application that combines live camera preview
    with parameter-driven capture directly from the video stream."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title("拍照控制 — 实时预览")
        root.minsize(1000, 800)

        # Internal state
        self._camera_manager: CameraManager | None = None
        self._preview_active = False
        self._capturing = False
        self._current_camera = REALSENSE
        self._imgtk: ImageTk.PhotoImage | None = None
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

        # Row 0: container + anomaly type
        row0 = ttk.Frame(section)
        row0.pack(fill=tk.X, pady=1)
        ttk.Label(row0, text="容器:", width=10).pack(side=tk.LEFT)
        self._container_var = tk.StringVar()
        self._container_cb = ttk.Combobox(
            row0, textvariable=self._container_var, state="readonly", width=30
        )
        self._container_cb.pack(side=tk.LEFT, padx=(0, 16))
        self._container_var.trace_add("write", self._on_path_field_change)

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
        self._point_var = tk.StringVar(value=SHOOTING_POINTS_CN_LIST[0])
        self._point_cb = ttk.Combobox(
            row1, textvariable=self._point_var, values=SHOOTING_POINTS_CN_LIST, width=28
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

    def _populate_params(self) -> None:
        """Fill comboboxes with values from path_config_standard."""
        c_items = [f"{k}: {v}" for k, v in sorted(CONTAINERS_CN.items())]
        self._container_cb["values"] = c_items
        if c_items:
            self._container_var.set(c_items[0])

        a_items = [f"{k}: {v}" for k, v in sorted(ANOMALY_TYPES_CN.items())]
        self._anomaly_cb["values"] = a_items
        if a_items:
            self._anomaly_var.set(a_items[0])

        self._update_subcategories()

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

    def _on_anomaly_change(self, *_args) -> None:
        self._photo_var.set(1)
        self._update_subcategories()
        self._update_path_preview()

    def _on_path_field_change(self, *_args) -> None:
        self._photo_var.set(1)
        self._update_path_preview()

    def _get_shooting_point(self) -> str:
        cn = self._point_var.get().strip()
        return SHOOTING_POINTS_CN.get(cn, cn)

    def _get_subcategory_value(self) -> str:
        sub = self._sub_var.get().strip()
        if sub == NO_SUBCATEGORY:
            return NO_SUBCATEGORY
        subs_en = {v: k for k, v in ANOMALY_SUBCATEGORIES_CN.items()}
        return subs_en.get(sub, sub)

    def _update_subcategories(self) -> None:
        text = self._anomaly_var.get()
        if not text:
            return
        try:
            aid = int(text.split(":")[0])
        except (ValueError, IndexError):
            aid = 1

        subs = ANOMALY_SUBCATEGORIES.get(aid, [])
        subs_display = [ANOMALY_SUBCATEGORIES_CN.get(s, s) for s in subs]
        if aid == 1 or not subs:
            self._sub_cb["state"] = tk.DISABLED
            self._sub_var.set(NO_SUBCATEGORY)
            self._sub_cb["values"] = [NO_SUBCATEGORY]
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
        cid, aid, sub, point, view, _photo = self._parse_params()
        return build_shot_dir(cid, aid, sub, point, view)

    def _build_output_paths(self) -> dict[str, Path]:
        """Return ``{camera_id: output_file_path}`` for the current
        parameter selection."""
        cid, aid, sub, point, view, photo = self._parse_params()
        shot_dir = build_shot_dir(cid, aid, sub, point, view)

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
            self._camera_manager = CameraManager()
        except Exception as exc:
            self._log(f"初始化 CameraManager 失败: {exc}")
            messagebox.showerror("相机初始化失败", str(exc))
            self._set_buttons_preview_stopped()
            return

        # Start cameras in a background thread so the UI stays responsive
        def _start_and_begin() -> None:
            try:
                results = self._camera_manager.start_all(ORBBEC_C1_SERIAL)
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
                text = list_connected_cameras()
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
    root = tk.Tk()
    PreviewCaptureGUI(root)
    root.mainloop()
