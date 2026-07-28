#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
empty_container 部分删除点位图片审核 GUI
==========================================

用途
----
辅助人工逐张审核 "部分删除点位" 中被 curation 删掉的图片（共 550 张），
由审核者决定每张到底是「删除」还是「保留」。审核完成后导出新的 delete.csv，
作为 delete_unusable.py 的输入（与旧 delete.csv 格式一致：image_path 列）。

判定逻辑（来自前期分析，已校验：REVIEW=550 / beaker整删=55 / liquid整删=114）
- chosen.csv 是「保留」清单；raw/empty_container 是删除前完整集。
- 被删图片 = raw 中存在、但 chosen.csv 未指向的图片。
- 整点位删除：beaker 的 3 个点确认为正确删除，直接写入 delete.csv；
              liquid_reservoir 的 6 个点确认为误删，不写入（恢复/保留）。
- 部分删除点位的 550 张：逐张由人工审核。

依赖
----
仅需标准库 + tkinter（Python 自带，无需 opencv/PIL）。
图片用 tkinter.PhotoImage 原生加载 PNG，并用 subsample 整数缩放适配窗口。

用法
----
    python review_deletions_gui.py            # 启动审核 GUI
    python review_deletions_gui.py --check    # 仅打印数量统计后退出（不弹窗）

导出
----
审核完成后按 E 或点「导出 delete.csv」：
    新 delete.csv = beaker 确认删除(55) + 审核标记为删除的图片
    导出前会自动把旧 delete.csv 备份为 delete.csv.bak
"""

import os
import sys
import csv
import json
import argparse
from pathlib import Path
from collections import defaultdict

# ======================= 可配置路径（按环境修改） =======================
BASE = Path(__file__).resolve().parent
RAW_ROOT = Path(r"D:\myproject\2026.7research\dataset\raw\empty_container")
CHOSEN_CSV = BASE / "chosen.csv"
FOLDER_MAP = BASE.parent / "folder_name_mapping.md"
STATE_FILE = BASE / "review_state.json"
DELETE_CSV = BASE / "delete.csv"

IMG_EXT = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp"}

# 整点位删除中「确认正确删除」的点位（直接写入 delete.csv，不参与逐张审核）
CONFIRMED_DELETE_POINTS = {
    ("beaker", "analytical_balance-003"),
    ("beaker", "mixer2-001"),
    ("beaker", "stack1-005"),
}
# ==========================================================================


def parse_mapping(map_path):
    """解析 folder_name_mapping.md 的异常一级/二级分类，构建别名组。"""
    alias = defaultdict(set)
    cur = None
    if not map_path.is_file():
        return alias
    for line in map_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            cur = line[3:].strip()
            continue
        if cur in ("3. 异常一级分类", "4. 异常二级分类") and line.strip().startswith("|"):
            cells = [c.strip().strip("`") for c in line.strip().strip("|").split("|")]
            if len(cells) >= 2 and cells[0] and cells[0] != "当前名称":
                cur_, std = cells[0], cells[1]
                alias[cur_] |= {std, cur_}
                alias[std] |= {cur_, std}
    return alias


def folder_tokens(p):
    rp = p.relative_to(RAW_ROOT).parts
    return set(rp[1:len(rp) - 1])


def path_target_tokens(rel, alias):
    parts = rel.replace("\\", "/").split("/")[:-2]
    t = set()
    for x in parts:
        t |= alias.get(x, {x})
    return t


def build_review_list():
    """返回 (review_items, beaker_confirmed_paths)。

    review_items: list[dict] 每项 {path, container, point, anomaly, subcat, filename}
    beaker_confirmed_paths: list[Path] 整点位正确删除的图片（直接进 delete.csv）
    """
    alias = parse_mapping(FOLDER_MAP)

    # 1) 索引 raw 文件: (container, sp, fn) -> [Path]
    raw_index = defaultdict(list)
    raw_files_all = []
    for r, d, fs in RAW_ROOT.walk():
        for fn in fs:
            if Path(fn).suffix.lower() in IMG_EXT:
                p = Path(r) / fn
                rel = p.relative_to(RAW_ROOT).parts
                raw_index[(rel[0], rel[-2], rel[-1])].append(p)
                raw_files_all.append(p)

    # 2) 两遍指派：每个 chosen 行认领恰好一个 raw 文件 -> kept 集合
    chosen_rows = []
    if CHOSEN_CSV.is_file():
        with CHOSEN_CSV.open(encoding="gbk") as f:
            for row in csv.DictReader(f):
                chosen_rows.append(row)

    claimed = {}
    # pass1: 精确路径
    for i, row in enumerate(chosen_rows):
        cat = row["object_category"].strip()
        rel = row["source_relative_path"].replace("\\", "/")
        c = RAW_ROOT / rel
        if c.exists() and c.resolve() not in claimed:
            claimed[c.resolve()] = i
            continue
        c = RAW_ROOT / cat / rel
        if c.exists() and c.resolve() not in claimed:
            claimed[c.resolve()] = i
    # pass2: 误命名行 -> 认领一个未占用的候选
    for i, row in enumerate(chosen_rows):
        if i in claimed.values():
            continue
        cat = row["object_category"].strip()
        parts = row["source_relative_path"].replace("\\", "/").split("/")
        sp = parts[-2]
        fn = parts[-1]
        dn = (row.get("defect_name") or "").strip()
        cands = raw_index.get((cat, sp, fn), [])
        unclaimed = [p for p in cands if p.resolve() not in claimed]
        if not unclaimed:
            continue
        target = path_target_tokens(row["source_relative_path"], alias)
        exact = [p for p in unclaimed if folder_tokens(p) == target] if target else []
        if exact:
            pick = exact[0]
        else:
            inter = [p for p in unclaimed if (folder_tokens(p) & target)] if target else []
            if inter:
                pick = inter[0]
            else:
                dn_match = [p for p in unclaimed if dn in folder_tokens(p)]
                pick = dn_match[0] if dn_match else unclaimed[0]
        claimed[pick.resolve()] = i

    kept_set = {p.resolve() for p in claimed}
    raw_resolved = {p.resolve() for p in raw_files_all}
    deleted_all = raw_resolved - kept_set

    # 3) 按点位统计
    raw_count = defaultdict(int)
    kept_count = defaultdict(int)
    for p in raw_files_all:
        rp = p.relative_to(RAW_ROOT).parts
        raw_count[(rp[0], rp[-2])] += 1
    for p in kept_set:
        rp = p.relative_to(RAW_ROOT).parts
        kept_count[(rp[0], rp[-2])] += 1

    partial_points = {k for k in raw_count if 0 < kept_count.get(k, 0) < raw_count[k]}
    full_del_points = {k for k in raw_count if kept_count.get(k, 0) == 0 and raw_count[k] > 0}

    # 4) 组装审核列表（部分删除点位的被删图片）
    review_items = []
    for p in deleted_all:
        rp = p.relative_to(RAW_ROOT).parts
        container, point = rp[0], rp[-2]
        if (container, point) not in partial_points:
            continue
        if len(rp) >= 4:
            anomaly = rp[1]
            subcat = rp[2] if len(rp) >= 5 else ""
        else:
            anomaly, subcat = "", ""
        review_items.append({
            "path": p,
            "container": container,
            "point": point,
            "anomaly": anomaly,
            "subcat": subcat,
            "filename": rp[-1],
        })

    # 5) beaker 整点位确认删除（直接进 delete.csv）
    beaker_confirmed = []
    for (container, point) in full_del_points:
        if (container, point) in CONFIRMED_DELETE_POINTS:
            for p in raw_files_all:
                rp = p.relative_to(RAW_ROOT).parts
                if rp[0] == container and rp[-2] == point:
                    beaker_confirmed.append(p)

    # 误删（整点位但非确认）的点位，仅打印提示
    mis_points = [k for k in full_del_points if k not in CONFIRMED_DELETE_POINTS]

    return review_items, beaker_confirmed, mis_points, raw_count, kept_count, len(deleted_all)


def run_check():
    items, beaker, mis, raw_count, kept_count, deleted_total = build_review_list()
    print(f"raw 总数: {sum(raw_count.values())}")
    print(f"保留(认领): {sum(kept_count.values())}")
    print(f"删除总数: {deleted_total}")
    print(f"部分删除点位待审核: {len(items)} 张")
    print(f"beaker 整点位确认删除: {len(beaker)} 张 -> 直接写入 delete.csv")
    print(f"误删(整点位，不写入): {mis} -> 共 {sum(raw_count[k] for k in mis)} 张")
    rc = defaultdict(int)
    for it in items:
        rc[it["container"]] += 1
    print("待审核按容器分布:", dict(rc))


# ============================ GUI ============================
def launch_gui():
    import tkinter as tk
    from tkinter import ttk, messagebox

    items, beaker_confirmed, mis_points, _, _, _ = build_review_list()
    total = len(items)
    if total == 0:
        messagebox.showerror("错误", "未生成待审核列表（可能数据已变更或路径不对）。")
        return

    # 加载已有进度
    decisions = {}
    cur_index = 0
    if STATE_FILE.is_file():
        try:
            st = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            decisions = st.get("decisions", {})
            cur_index = st.get("index", 0)
        except Exception:
            decisions, cur_index = {}, 0

    root = tk.Tk()
    root.title(f"empty_container 删除审核  ({total} 张待审)")
    root.geometry("1080x760")

    # ---- 顶部进度条 ----
    top = ttk.Frame(root)
    top.pack(fill="x", padx=10, pady=6)
    progress_var = tk.StringVar()
    ttk.Label(top, textvariable=progress_var, font=("Arial", 11)).pack(side="left")
    info_var = tk.StringVar()
    ttk.Label(top, textvariable=info_var, font=("Arial", 10), foreground="#555").pack(side="right")

    # ---- 图片 ----
    img_frame = ttk.Frame(root)
    img_frame.pack(fill="both", expand=True, padx=10)
    img_label = ttk.Label(img_frame)
    img_label.pack(expand=True)

    # ---- 元数据 ----
    meta_var = tk.StringVar()
    ttk.Label(root, textvariable=meta_var, font=("Consolas", 10), justify="left",
              foreground="#222", wraplength=1040).pack(fill="x", padx=12, pady=(0, 4))

    # ---- 按钮 ----
    btn_frame = ttk.Frame(root)
    btn_frame.pack(fill="x", padx=10, pady=8)
    b_keep = ttk.Button(btn_frame, text="保留 (K)")
    b_del = ttk.Button(btn_frame, text="删除 (D)")
    b_prev = ttk.Button(btn_frame, text="上一张 (←)")
    b_next = ttk.Button(btn_frame, text="下一张 (→)")
    b_export = ttk.Button(btn_frame, text="导出 delete.csv (E)")
    b_keep.pack(side="left", padx=4)
    b_del.pack(side="left", padx=4)
    b_prev.pack(side="left", padx=4)
    b_next.pack(side="left", padx=4)
    b_export.pack(side="right", padx=4)

    hint = tk.StringVar(value="提示：D=删除  K=保留  ←=上一张  →=下一张  E=导出。beaker 的 3 个整删点位已默认计入删除。")
    ttk.Label(root, textvariable=hint, font=("Arial", 9), foreground="#888").pack(fill="x", padx=12, pady=(0, 6))

    photo_ref = [None]  # 防止 GC

    def current_decision():
        if 0 <= cur_index < total:
            return decisions.get(str(items[cur_index]["path"]), "")
        return ""

    def refresh():
        if not (0 <= cur_index < total):
            # 全部审核完
            meta_var.set("✅ 已全部审核完毕。按 E 导出 delete.csv，或用 ← 回看。")
            img_label.config(image="")
            progress_var.set(f"进度 {total}/{total}（已决定 {len(decisions)}）")
            info_var.set(f"删除 {sum(1 for v in decisions.values() if v=='delete')} / 保留 {sum(1 for v in decisions.values() if v=='keep')}")
            return
        it = items[cur_index]
        # 图片
        try:
            img = tk.PhotoImage(file=str(it["path"]))
            w, h = img.width(), img.height()
            max_w, max_h = 1000, 600
            scale = max(w / max_w, h / max_h)
            if scale > 1:
                f = max(1, int(round(scale)))
                img = img.subsample(f, f)
            photo_ref[0] = img
            img_label.config(image=img)
        except Exception as e:
            photo_ref[0] = None
            img_label.config(image="")
            meta_var.set(f"[图片加载失败: {e}]")
        # 元数据
        rel = it["path"].relative_to(RAW_ROOT)
        dec = current_decision()
        dec_tag = f"  【当前: {dec}】" if dec else ""
        meta_var.set(
            f"容器={it['container']}   点位={it['point']}   异常类型={it['anomaly']}   子类={it['subcat']}   文件名={it['filename']}{dec_tag}\n"
            f"相对路径: {rel}"
        )
        dcount = sum(1 for v in decisions.values() if v == "delete")
        kcount = sum(1 for v in decisions.values() if v == "keep")
        progress_var.set(f"第 {cur_index+1} / {total} 张")
        info_var.set(f"已决定 {len(decisions)}（删除 {dcount} / 保留 {kcount}）未决定 {total - len(decisions)}")

    def save_state():
        STATE_FILE.write_text(json.dumps(
            {"index": cur_index, "decisions": decisions}, ensure_ascii=False, indent=2),
            encoding="utf-8")

    def decide(kind):
        nonlocal cur_index
        if not (0 <= cur_index < total):
            return
        decisions[str(items[cur_index]["path"])] = kind
        save_state()
        # 跳到下一张
        if cur_index < total - 1:
            cur_index += 1
        refresh()

    def go_prev():
        nonlocal cur_index
        if cur_index > 0:
            cur_index -= 1
        refresh()

    def go_next():
        nonlocal cur_index
        if cur_index < total - 1:
            cur_index += 1
        refresh()

    def export_csv():
        del_paths = [str(p) for p in beaker_confirmed]
        for it in items:
            if decisions.get(str(it["path"])) == "delete":
                del_paths.append(str(it["path"]))
        if not del_paths:
            messagebox.showwarning("提示", "还没有任何标记为删除的图片。")
            return
        # 备份旧文件
        if DELETE_CSV.is_file():
            bak = DELETE_CSV.with_suffix(".csv.bak")
            try:
                bak.write_bytes(DELETE_CSV.read_bytes())
            except Exception:
                pass
        with DELETE_CSV.open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f)
            w.writerow(["image_path"])
            for p in del_paths:
                w.writerow([p])
        dcount = sum(1 for v in decisions.values() if v == "delete")
        messagebox.showinfo(
            "导出完成",
            f"已写入 {DELETE_CSV.name}\n"
            f"共 {len(del_paths)} 张：\n"
            f"  · beaker 整点位确认删除 {len(beaker_confirmed)} 张\n"
            f"  · 审核标记为删除 {dcount} 张\n"
            f"（旧文件已备份为 delete.csv.bak）"
        )

    b_del.config(command=lambda: decide("delete"))
    b_keep.config(command=lambda: decide("keep"))
    b_prev.config(command=go_prev)
    b_next.config(command=go_next)
    b_export.config(command=export_csv)

    root.bind("<d>", lambda e: decide("delete"))
    root.bind("<k>", lambda e: decide("keep"))
    root.bind("<Left>", lambda e: go_prev())
    root.bind("<Right>", lambda e: go_next())
    root.bind("<e>", lambda e: export_csv())
    root.bind("<E>", lambda e: export_csv())

    # 启动定位到第一张未决定的
    if cur_index >= total:
        cur_index = total - 1
    # 若已决定则跳到下一个未决定
    while cur_index < total and str(items[cur_index]["path"]) in decisions:
        cur_index += 1
    if cur_index >= total:
        cur_index = total - 1
    refresh()
    root.mainloop()


def main():
    ap = argparse.ArgumentParser(description="empty_container 删除审核 GUI")
    ap.add_argument("--check", action="store_true", help="仅打印统计信息后退出")
    args = ap.parse_args()
    if args.check:
        run_check()
    else:
        launch_gui()


if __name__ == "__main__":
    main()
