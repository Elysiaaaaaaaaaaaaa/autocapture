#!/usr/bin/env python3
"""GUI 拍照控制 — 支持三个采集脚本的图形界面"""

from __future__ import annotations

import subprocess
import sys
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from pathlib import Path

# ── 三个脚本的配置数据 ──────────────────────────────────────────────
# 数据来源: capture.py / parallel_cap.py / path_config_standard.py

SCRIPT_DIR = Path(__file__).parent.resolve()
BASE = Path("/home/qy/dataset-202607/quality test")

CAPTURE_CONFIG = {
    "dataset_root": BASE / "empty container",
    "containers": {1: "beaker", 2: "test tube", 3: "test tube modle2",
                   4: "6-well plate", 5: "11-well plate", 6: "24-well plate",
                   7: "48-well plate", 8: "96-well plate modle1",
                   9: "96-well plate modle 2", 10: "magnetic mixer 1",
                   11: "magnetic mixer 2", 12: "rewservoir", 13: "超声波清洗机器"},
    "anomaly_types": {1: "正常", 2: "主体破损", 3: "粉末残留",
                      4: "液体残留", 5: "污渍", 6: "object residue", 7: "tag"},
    "anomaly_subcategories": {
        1: [], 2: ["crack", "scratch", "wear"],
        3: ["bottom-powder", "crystal", "wall-powder"],
        4: ["color", "dip", "non-color"],
        5: ["color dirt", "water dirt"],
        6: ["glass rod"],
        7: ["damaged", "dirty", "fall"],
    },
}

PARALLEL_CONFIG = {
    "dataset_root": BASE / "empty_container",
    "containers": {1: "beaker", 2: "test tube", 3: "test tube modle2",
                   4: "6-well plate", 5: "11-well plate", 6: "24-well plate",
                   7: "48-well plate", 8: "96-well plate modle1",
                   9: "96-well plate modle 2", 10: "magnetic mixer 1",
                   11: "magnetic mixer 2", 12: "rewservoir", 13: "超声波清洗机器"},
    "anomaly_types": {1: "正常", 2: "污渍", 3: "破损", 4: "液体残留",
                      5: "固体残留", 6: "盖子异常", 7: "标签异常", 8: "摆放错误"},
    "anomaly_subcategories": {
        1: [], 2: ["水渍", "颜料污渍"], 3: ["划痕", "裂痕"],
        4: ["无色液体", "带颜色透明液体", "浑浊液体", "杯壁液体"],
        5: ["粉末", "结晶"], 6: ["盖子裂痕", "盖子盖错", "没有盖子"],
        7: ["标签脏污", "标签脱落", "标签破损"], 8: ["斜放"],
    },
}

STANDARD_CONFIG = {
    "dataset_root": BASE / "empty_container",
    "containers": {1: "beaker", 2: "test_tube_model_01", 3: "test_tube_model_02",
                   4: "multiwell_plate_06", 5: "multiwell_plate_11",
                   6: "multiwell_plate_24", 7: "multiwell_plate_48",
                   8: "multiwell_plate_96_model_01", 9: "multiwell_plate_96_model_02",
                   10: "magnetic_stirrer_01", 11: "magnetic_stirrer_02",
                   12: "liquid_reservoir", 13: "ultrasonic_cleaner"},
    "anomaly_types": {1: "normal", 2: "stain", 3: "damage", 4: "liquid_residue",
                      5: "solid_residue", 6: "lid_anomaly",
                      7: "label_anomaly", 8: "placement_error"},
    "anomaly_subcategories": {
        1: [], 2: ["water_stain", "pigment_stain"],
        3: ["scratch", "crack"],
        4: ["colorless_liquid", "colored_clear_liquid", "turbid_liquid", "wall_liquid_residue"],
        5: ["powder", "crystalline_residue"],
        6: ["cracked_lid", "incorrect_lid", "missing_lid"],
        7: ["label_soiling", "label_detachment", "label_damage"],
        8: ["tilted_placement"],
    },
}

SCRIPTS: dict[str, dict] = {
    "capture.py":              CAPTURE_CONFIG,
    "parallel_cap.py":         PARALLEL_CONFIG,
    "para_cap_standard.py":    STANDARD_CONFIG,
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


class CaptureGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title("拍照控制")
        root.minsize(680, 520)

        self.cfg: dict | None = None
        self._running = False

        try:
            ttk.Style().theme_use("vista")
        except tk.TclError:
            pass

        self._build_ui()
        self._select_script("para_cap_standard.py")

    # ── UI 构建 ──────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        main = ttk.Frame(self.root, padding=12)
        main.pack(fill=tk.BOTH, expand=True)

        # 脚本选择
        row = ttk.Frame(main)
        row.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(row, text="拍摄脚本:", width=10).pack(side=tk.LEFT)
        self.script_var = tk.StringVar()
        self.script_cb = ttk.Combobox(
            row, textvariable=self.script_var,
            values=list(SCRIPTS), state="readonly", width=30,
        )
        self.script_cb.pack(side=tk.LEFT, padx=4)
        self.script_cb.bind("<<ComboboxSelected>>",
                            lambda e: self._select_script(self.script_var.get()))

        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=6)

        # 参数行
        self._param_row(main, "容器:", "container", 0)
        self._param_row(main, "异常类型:", "anomaly", 1)
        self._param_row(main, "小类:", "sub", 2)
        self._param_row(main, "拍摄点位:", "point", 3)
        self._param_row(main, "视角编号:", "view", 4)
        self._param_row(main, "照片编号:", "photo", 5)

        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=6)

        # 路径预览
        row = ttk.Frame(main)
        row.pack(fill=tk.X, pady=2)
        ttk.Label(row, text="保存路径:", width=10).pack(side=tk.LEFT)
        self.path_var = tk.StringVar()
        ttk.Entry(row, textvariable=self.path_var, state="readonly",
                  font=("Consolas", 9)).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 按钮行
        btn_row = ttk.Frame(main)
        btn_row.pack(fill=tk.X, pady=6)
        self.list_btn = ttk.Button(btn_row, text="列出相机",
                                   command=self._list_cameras)
        self.list_btn.pack(side=tk.LEFT, padx=(0, 8))
        self.cap_btn = ttk.Button(btn_row, text="开始拍摄",
                                  command=self._start_capture)
        self.cap_btn.pack(side=tk.LEFT)

        self.preview_btn = ttk.Button(btn_row, text="预览 (dry-run)",
                                      command=self._dry_run)
        self.preview_btn.pack(side=tk.LEFT, padx=(8, 0))

        # 日志
        ttk.Label(main, text="日志:").pack(anchor=tk.W, pady=(4, 0))
        self.log_area = scrolledtext.ScrolledText(
            main, height=12, font=("Consolas", 9), wrap=tk.WORD, state=tk.DISABLED,
        )
        self.log_area.pack(fill=tk.BOTH, expand=True)

    def _param_row(self, parent: ttk.Frame, label: str,
                   key: str, row_id: int) -> None:
        row = ttk.Frame(parent)
        row.pack(fill=tk.X, pady=1)
        ttk.Label(row, text=label, width=10).pack(side=tk.LEFT)

        if key == "container":
            self.container_var = tk.StringVar()
            self.container_var.trace_add("write", self._update_preview)
            self.container_cb = ttk.Combobox(row, textvariable=self.container_var,
                                              state="readonly", width=40)
            self.container_cb.pack(side=tk.LEFT, fill=tk.X, expand=True)

        elif key == "anomaly":
            self.anomaly_var = tk.StringVar()
            self.anomaly_var.trace_add("write", self._on_anomaly_change)
            self.anomaly_cb = ttk.Combobox(row, textvariable=self.anomaly_var,
                                            state="readonly", width=40)
            self.anomaly_cb.pack(side=tk.LEFT, fill=tk.X, expand=True)

        elif key == "sub":
            self.sub_var = tk.StringVar()
            self.sub_var.trace_add("write", self._update_preview)
            self.sub_cb = ttk.Combobox(row, textvariable=self.sub_var,
                                        state="readonly", width=40)
            self.sub_cb.pack(side=tk.LEFT, fill=tk.X, expand=True)

        elif key == "point":
            self.point_var = tk.StringVar(value="magnetic_stirrer_01")
            self.point_var.trace_add("write", self._update_preview)
            self.point_cb = ttk.Combobox(row, textvariable=self.point_var,
                                          values=SHOOTING_POINTS, width=38)
            self.point_cb.pack(side=tk.LEFT, fill=tk.X, expand=True)

        elif key == "view":
            self.view_var = tk.IntVar(value=1)
            self.view_var.trace_add("write", self._update_preview)
            ttk.Spinbox(row, from_=1, to=999, textvariable=self.view_var,
                        width=8).pack(side=tk.LEFT)

        elif key == "photo":
            self.photo_var = tk.IntVar(value=1)
            self.photo_var.trace_add("write", self._update_preview)
            ttk.Spinbox(row, from_=1, to=999, textvariable=self.photo_var,
                        width=8).pack(side=tk.LEFT)

    # ── 脚本切换 ─────────────────────────────────────────────────────

    def _select_script(self, name: str) -> None:
        self.cfg = SCRIPTS[name]

        c_items = [f"{k}: {v}" for k, v in sorted(self.cfg["containers"].items())]
        self.container_cb["values"] = c_items
        self.container_var.set(c_items[0] if c_items else "")

        a_items = [f"{k}: {v}" for k, v in sorted(self.cfg["anomaly_types"].items())]
        self.anomaly_cb["values"] = a_items
        self.anomaly_var.set(a_items[0] if a_items else "")

        self._on_anomaly_change()
        self._update_preview()

    def _on_anomaly_change(self, *_args) -> None:
        self._update_subcategories()
        self._update_preview()

    def _update_subcategories(self) -> None:
        if not self.cfg:
            return
        text = self.anomaly_var.get()
        if not text:
            return
        try:
            aid = int(text.split(":")[0])
        except (ValueError, IndexError):
            aid = 1

        subs = self.cfg["anomaly_subcategories"].get(aid, [])
        if aid == 1 or not subs:
            self.sub_cb["state"] = tk.DISABLED
            self.sub_var.set("-")
            self.sub_cb["values"] = ["-"]
        else:
            self.sub_cb["state"] = "readonly"
            self.sub_cb["values"] = subs
            self.sub_var.set(subs[0])

    # ── 路径预览 ─────────────────────────────────────────────────────

    def _update_preview(self, *_args) -> None:
        if not self.cfg:
            return
        try:
            path = self._build_path()
            self.path_var.set(str(path))
        except Exception:
            self.path_var.set("(参数不完整)")

    def _build_path(self) -> Path:
        cid = int(self.container_var.get().split(":")[0])
        aid = int(self.anomaly_var.get().split(":")[0])
        sub = self.sub_var.get().strip()
        point = self.point_var.get().strip()
        view = self.view_var.get()

        root = self.cfg["dataset_root"]
        container = self.cfg["containers"][cid]
        anom = self.cfg["anomaly_types"][aid]
        leaf = f"{point}-{view:03d}"

        if aid == 1:
            return root / container / anom / leaf
        if sub in ("", "-"):
            return root / container / anom / leaf
        return root / container / anom / sub / leaf

    # ── 操作 ─────────────────────────────────────────────────────────

    def _build_cmd(self, dry_run: bool = False) -> list[str]:
        cid = int(self.container_var.get().split(":")[0])
        aid = int(self.anomaly_var.get().split(":")[0])
        sub = self.sub_var.get().strip()
        point = self.point_var.get().strip()
        view = self.view_var.get()
        photo = self.photo_var.get()

        if aid == 1:
            sub_final = "-"
        elif not sub or sub == "-":
            msg = "请选择小类"
            messagebox.showwarning("参数不完整", msg)
            raise ValueError(msg)
        else:
            sub_final = sub

        if not point:
            msg = "请填写拍摄点位"
            messagebox.showwarning("参数不完整", msg)
            raise ValueError(msg)

        script = str(SCRIPT_DIR / self.script_var.get())
        cmd = [sys.executable, script,
               str(cid), str(aid), sub_final,
               point, str(view), str(photo)]
        if dry_run:
            cmd.append("--dry-run")
        return cmd

    def _list_cameras(self) -> None:
        script = str(SCRIPT_DIR / self.script_var.get())
        self._log(f"> {sys.executable} {script} --list-cameras")
        self._set_buttons_disabled(True)
        t = threading.Thread(target=self._run_cli,
                             args=([sys.executable, script, "--list-cameras"],),
                             daemon=True)
        t.start()

    def _dry_run(self) -> None:
        try:
            cmd = self._build_cmd(dry_run=True)
        except ValueError:
            return
        self._log(f"> {' '.join(cmd)}")
        self._set_buttons_disabled(True)
        t = threading.Thread(target=self._run_cli, args=(cmd,), daemon=True)
        t.start()

    def _start_capture(self) -> None:
        try:
            cmd = self._build_cmd()
        except ValueError:
            return
        self._log(f"> {' '.join(cmd)}")
        self._set_buttons_disabled(True)
        self._running = True
        t = threading.Thread(target=self._run_cli, args=(cmd,), daemon=True)
        t.start()

    def _run_cli(self, cmd: list[str]) -> None:
        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            for line in proc.stdout:
                self.root.after(0, self._log, line.rstrip())
            proc.wait()
            self.root.after(0, self._on_cli_done, proc.returncode)
        except Exception as e:
            self.root.after(0, self._log, f"错误: {e}")
            self.root.after(0, self._set_buttons_disabled, False)

    def _on_cli_done(self, retcode: int) -> None:
        if retcode == 0:
            self._log("✓ 完成")
        else:
            self._log(f"✗ 退出码 {retcode}")
        self._set_buttons_disabled(False)
        self._running = False

    def _set_buttons_disabled(self, disabled: bool) -> None:
        state = tk.DISABLED if disabled else tk.NORMAL
        self.list_btn["state"] = state
        self.cap_btn["state"] = state
        self.preview_btn["state"] = state
        self.script_cb["state"] = state

    # ── 日志 ─────────────────────────────────────────────────────────

    def _log(self, msg: str) -> None:
        self.log_area["state"] = tk.NORMAL
        self.log_area.insert(tk.END, msg + "\n")
        self.log_area.see(tk.END)
        self.log_area["state"] = tk.DISABLED


if __name__ == "__main__":
    root = tk.Tk()
    CaptureGUI(root)
    root.mainloop()
