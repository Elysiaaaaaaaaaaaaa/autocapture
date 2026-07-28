#!/usr/bin/env python3
"""孔板材料采集 GUI — 基于 preview_gui，增加逐孔异常标注。

路径层级（path_config_plate_material）::

    <root>/<state>/<material>/<container>/<point>-<view>/

拍照时在 RealSense 图片同目录写入同名 txt（如 ``001_Color.txt``），
内容为每个孔位的异常类型（默认 blank）。

Usage::

    python -m preview_mode.plate_material_gui
    python preview_mode/plate_material_gui.py
"""

from __future__ import annotations

import argparse
import sys
import tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox

_PARENT = Path(__file__).resolve().parent.parent
if str(_PARENT) not in sys.path:
    sys.path.insert(0, str(_PARENT))

from capture_base import _create_dry_run_placeholder
from preview_mode.camera_manager import ORBBEC_C1, ORBBEC_C2, REALSENSE
from preview_mode.preview_gui import (
    PreviewCaptureGUI,
    _load_path_config,
)

# 孔位按钮背景色（按异常 id）
_WELL_COLORS: dict[int, str] = {
    0: "#E8E8E8",   # blank
    1: "#C8E6C9",   # normal
    2: "#FFCCBC",   # impurity
    3: "#FFE0B2",   # insufficient_quantity
    4: "#D7CCC8",   # caking
    5: "#F8BBD0",   # label_anomaly
    6: "#E1BEE7",   # color_anomaly
    7: "#B3E5FC",   # undissolved
    8: "#B2EBF2",   # bubbles
    9: "#FFCDD2",   # fracture
    10: "#FFF9C4",  # missing_corner
}


class PlateMaterialGUI(PreviewCaptureGUI):
    """preview_gui 子集 + 孔位标注网格。"""

    def __init__(self, root: tk.Tk, cfg=None) -> None:
        if cfg is None:
            cfg = _load_path_config("path_config_plate_material")
        if not getattr(cfg, "USES_PLATE_WELL_ANNOTATION", False):
            raise SystemExit(
                "plate_material_gui 需要 USES_PLATE_WELL_ANNOTATION=True 的配置"
                "（请使用 path_config_plate_material）"
            )

        # 孔位状态：well_id -> anomaly_id，默认 blank
        self._well_anomaly: dict[str, int] = {}
        self._well_buttons: dict[str, tk.Button] = {}
        self._well_grid_frame: ttk.Frame | None = None
        self._paint_anomaly_var = tk.IntVar(value=cfg.BLANK_ANOMALY_ID)
        self._palette_frame: ttk.Frame | None = None

        super().__init__(root, cfg=cfg)
        root.title("拍照控制 — 孔板材料（逐孔标注）")
        root.minsize(1100, 900)

    # ── UI overrides ──────────────────────────────────────────────────

    def _build_ui(self) -> None:
        outer = ttk.Frame(self.root)
        outer.pack(fill=tk.BOTH, expand=True)

        self._scroll_canvas = tk.Canvas(outer, highlightthickness=0)
        vsb = ttk.Scrollbar(
            outer, orient=tk.VERTICAL, command=self._scroll_canvas.yview
        )
        self._scroll_canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self._scroll_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        main = ttk.Frame(self._scroll_canvas, padding=12)
        self._scroll_window = self._scroll_canvas.create_window(
            (0, 0), window=main, anchor=tk.NW
        )

        main.bind("<Configure>", self._on_scroll_content_configure)
        self._scroll_canvas.bind("<Configure>", self._on_scroll_canvas_configure)
        # 全局滚轮（避免移入子控件后 Enter/Leave 解绑失效）
        self.root.bind_all("<MouseWheel>", self._on_mousewheel, add="+")
        self.root.bind_all("<Button-4>", self._on_mousewheel, add="+")
        self.root.bind_all("<Button-5>", self._on_mousewheel, add="+")

        self._build_preview_section(main)
        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=6)
        self._build_param_section(main)
        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=4)
        self._build_well_annotation_section(main)
        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=6)
        self._build_button_section(main)
        self._build_log_section(main)
        self._setup_keyboard_shortcuts()

    def _on_scroll_content_configure(self, _event=None) -> None:
        self._scroll_canvas.configure(scrollregion=self._scroll_canvas.bbox("all"))

    def _on_scroll_canvas_configure(self, event: tk.Event) -> None:
        self._scroll_canvas.itemconfigure(self._scroll_window, width=event.width)

    def _scroll_by_event(self, event: tk.Event) -> None:
        if getattr(event, "num", None) == 5 or getattr(event, "delta", 0) < 0:
            self._scroll_canvas.yview_scroll(3, "units")
        elif getattr(event, "num", None) == 4 or getattr(event, "delta", 0) > 0:
            self._scroll_canvas.yview_scroll(-3, "units")

    def _on_mousewheel(self, event: tk.Event) -> str | None:
        # 日志区自身滚动，不抢事件
        w = event.widget
        if isinstance(w, tk.Text):
            return None
        self._scroll_by_event(event)
        return "break"

    def _on_combobox_mousewheel(self, event: tk.Event) -> str:
        """悬停下拉框时：只滚页面，不切换选项。"""
        self._scroll_by_event(event)
        return "break"

    def _disable_combobox_mousewheel(self, *comboboxes: ttk.Combobox) -> None:
        for cb in comboboxes:
            cb.bind("<MouseWheel>", self._on_combobox_mousewheel)
            cb.bind("<Button-4>", self._on_combobox_mousewheel)
            cb.bind("<Button-5>", self._on_combobox_mousewheel)

    def _on_close(self) -> None:
        self.root.unbind_all("<MouseWheel>")
        self.root.unbind_all("<Button-4>")
        self.root.unbind_all("<Button-5>")
        super()._on_close()

    def _build_material_param_fields(self, section: ttk.Frame) -> None:
        """材料参数：无全局异常类型（异常按孔标注）。"""
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
        ttk.Label(row1, text="容器种类:", width=10).pack(side=tk.LEFT)
        self._container_var = tk.StringVar()
        self._container_cb = ttk.Combobox(
            row1, textvariable=self._container_var, state="readonly", width=30
        )
        self._container_cb.pack(side=tk.LEFT, padx=(0, 16))
        self._container_var.trace_add("write", self._on_container_change)

        ttk.Label(row1, text="拍摄点位:", width=10).pack(side=tk.LEFT)
        self._point_var = tk.StringVar()
        self._point_cb = ttk.Combobox(
            row1, textvariable=self._point_var, state="readonly", width=30
        )
        self._point_cb.pack(side=tk.LEFT)
        self._point_var.trace_add("write", self._on_path_field_change)

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

        # 父类逻辑仍会查 _anomaly_var；占位即可（路径不使用）
        self._anomaly_var = tk.StringVar(value="0: 空白")
        self._anomaly_cb = ttk.Combobox(
            section, textvariable=self._anomaly_var, state="disabled", width=1
        )

        # 禁用悬停滚轮切换下拉选项（仍滚动页面）
        self._disable_combobox_mousewheel(
            self._state_cb,
            self._material_cb,
            self._container_cb,
            self._point_cb,
            self._anomaly_cb,
        )

        self._populate_params()

    def _build_well_annotation_section(self, parent: ttk.Frame) -> None:
        section = ttk.LabelFrame(
            parent,
            text="孔位标注（先选异常类型，再点击孔位；默认空白）",
            padding=6,
        )
        section.pack(fill=tk.X)

        self._palette_frame = ttk.Frame(section)
        self._palette_frame.pack(fill=tk.X, pady=(0, 4))

        tools = ttk.Frame(section)
        tools.pack(fill=tk.X, pady=(0, 4))
        ttk.Button(
            tools, text="全部设为当前类型", command=self._fill_all_wells
        ).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(
            tools, text="全部清空为空白", command=self._clear_all_wells
        ).pack(side=tk.LEFT)

        self._well_grid_frame = ttk.Frame(section)
        self._well_grid_frame.pack(fill=tk.X)

        self._rebuild_anomaly_palette()
        self._rebuild_well_grid()

    # ── well / palette helpers ────────────────────────────────────────

    def _rebuild_anomaly_palette(self) -> None:
        if self._palette_frame is None:
            return
        for child in self._palette_frame.winfo_children():
            child.destroy()

        state_id = self._current_combo_id(self._state_var)
        if state_id is None:
            anomaly_ids = [self._cfg.BLANK_ANOMALY_ID]
        else:
            anomaly_ids = self._cfg.get_anomaly_types(state_id)

        current = self._paint_anomaly_var.get()
        if current not in anomaly_ids:
            self._paint_anomaly_var.set(self._cfg.BLANK_ANOMALY_ID)

        ttk.Label(self._palette_frame, text="画笔:").pack(side=tk.LEFT, padx=(0, 4))
        for aid in anomaly_ids:
            cn = self._cfg.ANOMALY_TYPES_CN[aid]
            color = _WELL_COLORS.get(aid, "#DDDDDD")
            rb = tk.Radiobutton(
                self._palette_frame,
                text=f"{aid}:{cn}",
                variable=self._paint_anomaly_var,
                value=aid,
                indicatoron=False,
                width=10,
                bg=color,
                activebackground=color,
                selectcolor=color,
                relief=tk.RAISED,
                bd=1,
            )
            rb.pack(side=tk.LEFT, padx=2, pady=1)

    def _rebuild_well_grid(self) -> None:
        if self._well_grid_frame is None:
            return
        for child in self._well_grid_frame.winfo_children():
            child.destroy()
        self._well_buttons.clear()

        container_id = self._current_combo_id(self._container_var)
        if container_id is None:
            return

        try:
            well_ids = self._cfg.well_ids_for_container(container_id)
            cells = self._cfg.well_grid_cells(container_id)
            spec = self._cfg.get_plate_spec(container_id)
        except (ValueError, AttributeError):
            return

        blank = self._cfg.BLANK_ANOMALY_ID
        new_state = {wid: self._well_anomaly.get(wid, blank) for wid in well_ids}
        self._well_anomaly = new_state

        naming = spec["naming"]
        if naming == "alpha":
            rows, cols = spec["layout"]
            for c in range(1, cols + 1):
                ttk.Label(
                    self._well_grid_frame, text=str(c), width=4, anchor=tk.CENTER
                ).grid(row=0, column=c, padx=1, pady=1)
            for r in range(rows):
                row_letter = chr(ord("A") + r)
                ttk.Label(
                    self._well_grid_frame, text=row_letter, width=3, anchor=tk.CENTER
                ).grid(row=r + 1, column=0, padx=1, pady=1)
            row_offset, col_offset = 1, 1
        else:
            row_offset, col_offset = 0, 0

        for wid, r, c in cells:
            btn = tk.Button(
                self._well_grid_frame,
                text=wid,
                width=5,
                height=2,
                relief=tk.RAISED,
                bd=1,
                command=lambda w=wid: self._paint_well(w),
            )
            btn.grid(row=r + row_offset, column=c + col_offset, padx=1, pady=1)
            self._well_buttons[wid] = btn
            self._refresh_well_button(wid)

    def _refresh_well_button(self, well_id: str) -> None:
        btn = self._well_buttons.get(well_id)
        if btn is None:
            return
        aid = self._well_anomaly.get(well_id, self._cfg.BLANK_ANOMALY_ID)
        color = _WELL_COLORS.get(aid, "#DDDDDD")
        cn = self._cfg.ANOMALY_TYPES_CN.get(aid, "?")
        btn.configure(bg=color, activebackground=color, text=f"{well_id}\n{cn}")

    def _paint_well(self, well_id: str) -> None:
        self._well_anomaly[well_id] = self._paint_anomaly_var.get()
        self._refresh_well_button(well_id)

    def _fill_all_wells(self) -> None:
        aid = self._paint_anomaly_var.get()
        for wid in self._well_anomaly:
            self._well_anomaly[wid] = aid
            self._refresh_well_button(wid)

    def _clear_all_wells(self) -> None:
        blank = self._cfg.BLANK_ANOMALY_ID
        for wid in self._well_anomaly:
            self._well_anomaly[wid] = blank
            self._refresh_well_button(wid)

    # ── parameter callback overrides ──────────────────────────────────

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
            self._container_cb,
            self._container_var,
            {
                cid: self._cfg.CONTAINERS_CN[cid]
                for cid in self._cfg.get_containers(state_id)
            },
            self._current_combo_id(self._container_var),
        )
        self._update_material_points()
        self._rebuild_anomaly_palette()
        self._rebuild_well_grid()

    def _on_container_change(self, *_args) -> None:
        self._photo_var.set(1)
        self._update_material_points()
        self._rebuild_well_grid()
        self._update_path_preview()

    def _on_material_state_change(self, *_args) -> None:
        if not self._material_mode:
            return
        self._photo_var.set(1)
        self._update_material_dependent_fields()
        self._update_path_preview()

    # ── path building (无 anomaly 层) ─────────────────────────────────

    def _parse_plate_params(self) -> tuple[int, int, int, str, str, int]:
        state_id = self._require_combo_id(self._state_var, "材料状态")
        material_id = self._require_combo_id(self._material_var, "具体材料")
        container_id = self._require_combo_id(self._container_var, "容器类型")
        point = self._get_shooting_point()
        view = self._view_var.get().strip()
        photo = self._photo_var.get()

        if not point:
            raise ValueError("请选择拍摄点位")
        if not view:
            raise ValueError("请填写视角编号")

        return state_id, material_id, container_id, point, view, photo

    def _build_output_dir(self) -> Path:
        state, material, container, point, view, _photo = self._parse_plate_params()
        return self._cfg.build_shot_dir(state, material, container, point, view)

    def _build_output_paths(self) -> dict[str, Path]:
        state, material, container, point, view, photo = self._parse_plate_params()
        shot_dir = self._cfg.build_shot_dir(
            state, material, container, point, view
        )
        photo_id = f"{photo:03d}"
        orbbec_dir = shot_dir / f"view_top_{photo}"
        return {
            REALSENSE: shot_dir / f"{photo_id}_Color.png",
            ORBBEC_C1: orbbec_dir / "camera1_Color.png",
            ORBBEC_C2: orbbec_dir / "camera2_Color.png",
        }

    def _annotation_path(self, paths: dict[str, Path]) -> Path:
        return self._cfg.annotation_path_for_image(paths[REALSENSE])

    def _ordered_well_anomalies(self) -> dict[str, str]:
        """按孔位顺序返回 {well_id: anomaly_en}。"""
        container_id = self._require_combo_id(self._container_var, "容器类型")
        well_ids = self._cfg.well_ids_for_container(container_id)
        blank = self._cfg.BLANK_ANOMALY_ID
        result = {}
        for wid in well_ids:
            aid = self._well_anomaly.get(wid, blank)
            result[wid] = self._cfg.ANOMALY_TYPES[aid]
        return result

    def _save_well_annotation(self, paths: dict[str, Path]) -> Path:
        ann_path = self._annotation_path(paths)
        ann_path.parent.mkdir(parents=True, exist_ok=True)
        content = self._cfg.format_well_annotation(self._ordered_well_anomalies())
        ann_path.write_text(content, encoding="utf-8")
        return ann_path

    def _confirm_overwrite(self, paths: dict[str, Path]) -> bool:
        check = dict(paths)
        check["annotation"] = self._annotation_path(paths)
        existing = [p for p in check.values() if p.exists()]
        if not existing:
            return True
        msg = "以下文件已存在:\n" + "\n".join(str(p) for p in existing)
        msg += "\n\n是否覆盖？"
        return messagebox.askyesno("文件已存在", msg)

    # ── capture / dry-run：同步写 txt ─────────────────────────────────

    def _on_capture_done(
        self, results: dict[str, bool], paths: dict[str, Path]
    ) -> None:
        for cam_id, ok in results.items():
            label = {REALSENSE: "RealSense", ORBBEC_C1: "Orbbec C1", ORBBEC_C2: "Orbbec C2"}.get(
                cam_id, cam_id
            )
            if ok:
                self._log(f"  ✓ {label} → {paths[cam_id]}")
            else:
                self._log(f"  ✗ {label} 失败 (无可用帧)")

        try:
            ann_path = self._save_well_annotation(paths)
            self._log(f"  ✓ 孔位标注 → {ann_path}")
        except Exception as exc:
            self._log(f"  ✗ 孔位标注写入失败: {exc}")
            messagebox.showerror("标注保存失败", str(exc))

        self._log("拍照完成")
        self._capturing = False
        self._capture_btn["state"] = tk.NORMAL

        current = self._photo_var.get()
        self._photo_var.set(current + 1)
        self._update_path_preview()
        self._ensure_shortcut_focus()

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
        try:
            ann_path = self._save_well_annotation(paths)
            self._log(f"  ✓ 孔位标注 → {ann_path}")
        except Exception as exc:
            self._log(f"  ✗ 孔位标注写入失败: {exc}")
        self._log("dry-run 完成 — 未连接任何相机")

        current = self._photo_var.get()
        self._photo_var.set(current + 1)
        self._update_path_preview()

    # ── keyboard: 去掉全局异常快捷键 E ───────────────────────────────

    def _on_key_press(self, event: tk.Event) -> str | None:
        if self._capturing:
            return "break"

        focus = self.root.focus_get()
        editable = self._is_editable_widget(focus)

        if event.keysym == "space" and not editable:
            if self._kb_mode is None:
                self._do_capture()
            self._ensure_shortcut_focus()
            return "break"

        if event.keysym == "Escape" and self._kb_mode is not None:
            self._kb_cancel()
            return "break"

        if event.char in ("m", "M") and not editable:
            self._enter_kb_mode("material")
            return "break"

        # E 不再绑定全局异常（异常在孔位网格上选择）

        if event.char in "0123456789" and self._kb_mode is not None and not editable:
            self._kb_append_digit(event.char)
            return "break"

        if event.keysym == "BackSpace" and self._kb_mode is not None and not editable:
            self._kb_backspace()
            return "break"

        if event.keysym == "Return" and self._kb_mode is not None:
            self._kb_submit()
            return "break"

        return None

    def _kb_submit(self) -> None:
        if not self._kb_buffer:
            return

        item_id = int(self._kb_buffer)
        mode = self._kb_mode

        if mode == "material":
            ok = self._select_kb_item(self._material_cb, self._material_var, item_id)
            if ok:
                label = self._material_var.get()
                self._kb_status_var.set(f"✓ {label}")
                self._schedule_kb_clear()
            else:
                valid = self._get_kb_valid_ids(self._material_cb)
                self._kb_status_var.set(f"无效编号，可选: {', '.join(valid)}")
                self.root.bell()
                return
        else:
            self._kb_cancel()
            return

        self._kb_mode = None
        self._kb_buffer = ""
        self._ensure_shortcut_focus()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="孔板材料采集 GUI — 实时预览 + 逐孔异常标注"
    )
    parser.add_argument(
        "--config",
        default="path_config_plate_material",
        help="路径配置模块名，默认 %(default)s",
    )
    args = parser.parse_args()

    cfg = _load_path_config(args.config)
    print(f"[配置] 使用 {args.config}")

    root = tk.Tk()
    PlateMaterialGUI(root, cfg=cfg)
    root.mainloop()
