#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""grab.py — 从数据集中按“图片序列”抽取图片，重命名、写描述、打包压缩。

工作原理
--------
1. 你在脚本顶部的「↓↓↓ 在这里填写 ↓↓↓」配置区里，直接写一串“图片序列”条目，
   每条由四部分组成：
       (category, 容器/材料类型, 异常类型, 点位-视角)
   category 取值: empty_container | material
2. 脚本自动在数据集里定位对应的视角目录（{point}-{view}），
   并把该目录下的所有图片复制到 output 文件夹。
3. 图片按顺序重命名：相同 容器/材料类型、异常类型、点位 但不同视角的图片，
   按视角编号作为前缀，如 01-001.png, 01-002.png（同视角内 001/002 为图片序号）。
4. 把描述文本写入 output/description.txt。
5. 最后把 output 文件夹打成压缩包（<output>.zip）。

定位策略（兼容两种目录结构）
---------------------------
- 用 leaf 目录名（点位-视角）做递归查找，再用“容器/材料类型 + 异常类型（+可选约束）”
  在祖先目录名中做 token 匹配，因此 empty_container 与 material 两种层级都不用硬编码。

配置方式（推荐）
----------------
直接改脚本顶部的 DESCRIPTION / ITEMS / OUTPUT_DIR 等变量，然后运行：
    python grab.py
命令行参数可作为一次性覆盖（不传则用脚本里写的）：
    python grab.py --dry-run            # 只预览
    python grab.py --category empty_container --type beaker ...   # 临时用 CLI
"""

# ==========================================================================
# ↓↓↓ 在这里填写 ↓↓↓
# ==========================================================================

# 1) 文本说明（会保存为 output/description.txt）
DESCRIPTION = """烧杯正常样本，磁力搅拌器1双视角。
"""

# 2) 图片序列：每行一个条目。顺序即抓取顺序。
#    字段说明：
#      category   : "empty_container" 或 "material"
#      type       : 容器/材料类型（文件夹名，如 beaker / polyvinyl_alcohol）
#      anomaly    : 异常类型（可带小类，用 "/" 分隔，如 "stain/water_stain"）
#      point_view : 点位-视角（如 "magnetic_stirrer_01-001"；仅写点位则抓该点位全部视角）
#      sub        : 小类名（消歧用，可留 None），如 "water_stain"
#      container  : 容器名（material 消歧用，可留 None），如 "liquid_reservoir"
#      state      : 材料状态（material 消歧用，可留 None），如 "raw_material"
ITEMS = [
    {"category": "empty_container", "type": "beaker", "anomaly": "normal",
     "point_view": "magnetic_stirrer_01-001", "sub": None, "container": None, "state": None},
    {"category": "empty_container", "type": "beaker", "anomaly": "normal",
     "point_view": "magnetic_stirrer_01-002", "sub": None, "container": None, "state": None},
    # 更多条目照上面格式往下加即可，例如：
    # {"category": "empty_container", "type": "beaker", "anomaly": "stain/water_stain",
    #  "point_view": "beaker_sample_carousel-001", "sub": "water_stain", "container": None, "state": None},
    # {"category": "material", "type": "polyvinyl_alcohol", "anomaly": "normal",
    #  "point_view": "magnetic_stirrer_01-001", "sub": None, "container": "liquid_reservoir", "state": None},
]

# 3) 数据集根目录（留 None 则按 category 自动从 path_config_standard.py / path_config_material.py 读取）
DATASET_ROOT = None

# 4) 输出目录（留 None 则自动生成 grabbed/<时间戳>）
OUTPUT_DIR = None

# 5) 开关
DRY_RUN = False    # True: 只打印计划，不复制/打包
NO_ZIP = False     # True: 不打包，仅生成文件夹

# ==========================================================================
# ↑↑↑ 填写区结束，下面一般不用改 ↑↑↑
# ==========================================================================


import argparse
import csv
import importlib
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PARENT_DIR = SCRIPT_DIR.parent  # 项目根目录（放有 path_config_*.py）

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}


def log(msg: str) -> None:
    print(msg, flush=True)


# --------------------------------------------------------------------------
# 数据集根目录推断
# --------------------------------------------------------------------------
def get_root_from_config(category: str):
    mod_name = {
        "empty_container": "path_config_standard",
        "material": "path_config_material",
    }.get(category)
    if not mod_name:
        return None
    try:
        if str(PARENT_DIR) not in sys.path:
            sys.path.insert(0, str(PARENT_DIR))
        mod = importlib.import_module(mod_name)
        return Path(mod.DATASET_ROOT)
    except Exception as exc:  # noqa: BLE001
        log(f"[警告] 无法从配置模块 {mod_name} 读取 DATASET_ROOT: {exc}")
        return None


# --------------------------------------------------------------------------
# 目录匹配
# --------------------------------------------------------------------------
def part_matches(req: str, folder_name: str) -> bool:
    """req 是否匹配某个祖先目录名：
    - 完全相等；或
    - folder_name 按 ':' '_' 空格 切分后的某个 token 与之相等。
    （例如 req='polyvinyl_alcohol' 可匹配 '01:polyvinyl_alcohol'；
       req='stain' 可匹配 'water_stain' 但不会匹配 'label_soiling'）
    """
    req_l = req.strip().lower()
    f_l = folder_name.lower()
    if not req_l:
        return True
    if req_l == f_l:
        return True
    tokens = re.split(r"[:_\s]+", f_l)
    return req_l in tokens


def ancestors_satisfy(rel_parts, required) -> bool:
    for req in required:
        if not any(part_matches(req, p) for p in rel_parts):
            return False
    return True


def split_multi(value: str):
    return [v for v in re.split(r"[/,;\s]+", value) if v]


def view_number_of(leaf_name: str):
    """leaf 如 magnetic_stirrer_01-001 -> 1；无数字视角则返回 None。"""
    if "-" in leaf_name:
        last = leaf_name.rsplit("-", 1)[-1]
        if last.isdigit():
            return int(last)
    return None


def resolve_dirs(root: Path, point_view: str, required):
    """返回匹配到的视角目录列表（按其视角编号排序）。"""
    point_view = point_view.strip()
    exact = [p for p in root.rglob(point_view) if p.is_dir()]
    if exact:
        candidates = exact
        mode = "exact"
    else:
        candidates = [p for p in root.rglob(f"{point_view}-*") if p.is_dir()]
        mode = "prefix" if candidates else "none"

    filtered = [
        d for d in candidates
        if ancestors_satisfy(d.relative_to(root).parts[:-1], required)
    ]
    # 按视角编号、再按目录名排序，保证 01,02,03... 顺序稳定
    filtered.sort(key=lambda d: (view_number_of(d.name) or 0, d.name))

    if not filtered:
        if candidates:
            log("[错误] 找到候选目录，但约束不匹配，请检查 "
                "type/anomaly/sub/container/state 是否正确。候选示例:")
            for d in candidates[:5]:
                log(f"    {d}")
        else:
            log(f"[错误] 未找到匹配目录: point-view='{point_view}', 约束={required}")
            log(f"        数据集根: {root}")
        raise SystemExit(2)

    if mode == "exact" and len(filtered) > 1:
        log("[错误] 精确匹配到多个目录，存在歧义，请用 sub/container/state 消歧:")
        for d in filtered:
            log(f"    {d}")
        raise SystemExit(2)

    return filtered


def collect_images(view_dir: Path):
    imgs = [
        f for f in view_dir.rglob("*")
        if f.is_file() and f.suffix.lower() in IMAGE_EXTS
    ]

    def sort_key(p):
        rel = str(p.relative_to(view_dir))
        return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", rel)]

    imgs.sort(key=sort_key)
    return imgs


def safe_name(base: str, used: set, hint: str = ""):
    """返回不重复的文件名；发生碰撞时优先用 hint(源目录leaf)区分，再退化为 _2/_3。"""
    if base not in used:
        used.add(base)
        return base
    stem, dot, ext = base.rpartition(".")
    ext = ("." + ext) if dot else ""
    if hint:
        cand = f"{stem}__{hint}{ext}"
        if cand not in used:
            used.add(cand)
            return cand
    i = 2
    while True:
        cand = f"{stem}_{i}{ext}"
        if cand not in used:
            used.add(cand)
            return cand
        i += 1


# --------------------------------------------------------------------------
# 主流程
# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(
        description="从数据集按图片序列抽取图片，重命名、写描述、打包压缩。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--manifest", help="清单文件，每行: category,type,anomaly,point-view[,sub,container,state] (覆盖脚本 ITEMS)")
    ap.add_argument("-c", "--category", choices=["empty_container", "material"], help="覆盖 ITEMS 中每条的 category")
    ap.add_argument("-t", "--type", help="覆盖 ITEMS 中每条的 type")
    ap.add_argument("-a", "--anomaly", help="覆盖 ITEMS 中每条的 anomaly")
    ap.add_argument("-p", "--point-view", action="append",
                    help="覆盖 ITEMS 中的 point_view (可重复)")
    ap.add_argument("--sub", help="覆盖 ITEMS 中每条的 sub")
    ap.add_argument("--container", help="覆盖 ITEMS 中每条的 container")
    ap.add_argument("--state", help="覆盖 ITEMS 中每条的 state")
    ap.add_argument("--desc", help="覆盖脚本 DESCRIPTION")
    ap.add_argument("--desc-file", help="从文件读取描述文本 (覆盖脚本 DESCRIPTION)")
    ap.add_argument("--dataset-root", help="数据集根目录 (覆盖脚本 DATASET_ROOT)")
    ap.add_argument("--output", help="输出目录 (覆盖脚本 OUTPUT_DIR)")
    ap.add_argument("--no-zip", action="store_true", help="不打压缩包，仅生成文件夹")
    ap.add_argument("--dry-run", action="store_true", help="只打印计划，不复制/打包")
    args = ap.parse_args()

    # 1) 收集条目：优先 CLI，其次 manifest，最后用脚本内 ITEMS
    items = []
    if args.manifest:
        mpath = Path(args.manifest)
        if not mpath.is_file():
            log(f"[错误] 清单文件不存在: {mpath}")
            return 2
        with mpath.open(encoding="utf-8") as fh:
            for ln, line in enumerate(fh, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                cols = [c.strip() for c in line.split(",")]
                if len(cols) < 4:
                    log(f"[警告] 第 {ln} 行字段不足(至少4列)，跳过: {line}")
                    continue
                cat, typ, ano, pv = cols[0], cols[1], cols[2], cols[3]
                sub = cols[4] if len(cols) > 4 and cols[4] else None
                cont = cols[5] if len(cols) > 5 and cols[5] else None
                st = cols[6] if len(cols) > 6 and cols[6] else None
                items.append((cat, typ, ano, pv, sub, cont, st))
    elif args.category and args.type and args.anomaly and args.point_view:
        # CLI 单条覆盖模式
        for pv in args.point_view:
            items.append((args.category, args.type, args.anomaly, pv,
                          args.sub, args.container, args.state))
    else:
        # 使用脚本顶部填写的 ITEMS
        for e in ITEMS:
            cat = e.get("category")
            typ = e.get("type")
            ano = e.get("anomaly")
            pv = e.get("point_view")
            if not (cat and typ and ano and pv):
                log(f"[错误] ITEMS 中某条缺少必填字段 (category/type/anomaly/point_view): {e}")
                return 2
            items.append((cat, typ, ano, pv,
                          e.get("sub"), e.get("container"), e.get("state")))

    if not items:
        log("[错误] 没有任何要抓取的条目（脚本 ITEMS 为空，也未提供 CLI 参数 / --manifest）")
        return 2

    # 2) 描述文本：CLI > 脚本 DESCRIPTION
    desc = args.desc
    if args.desc_file:
        dp = Path(args.desc_file)
        if not dp.is_file():
            log(f"[错误] 描述文件不存在: {dp}")
            return 2
        desc = dp.read_text(encoding="utf-8")
    if desc is None:
        desc = DESCRIPTION
    if not desc:
        desc = ""
        log("[警告] 未提供描述文本，将写入空描述。")

    # 3) 数据集根 / 输出目录 / 开关：CLI > 脚本配置
    root_override = args.dataset_root or DATASET_ROOT
    out_override = args.output or OUTPUT_DIR
    no_zip = args.no_zip or NO_ZIP
    dry_run = args.dry_run or DRY_RUN

    # 4) 解析每个条目 -> 视角目录 + 图片
    plan = []
    for cat, typ, ano, pv, sub, cont, st in items:
        if root_override:
            root = Path(root_override)
        else:
            root = get_root_from_config(cat)
        if root is None:
            log(f"[错误] 无法确定数据集根目录 (category={cat})，请用参数或脚本 DATASET_ROOT 指定")
            return 2
        if not root.is_dir():
            log(f"[错误] 数据集根目录不存在: {root}")
            return 2
        required = split_multi(ano) + [typ]
        if sub:
            required += split_multi(sub)
        if cont:
            required.append(cont)
        if st:
            required.append(st)
        for d in resolve_dirs(root, pv, required):
            imgs = collect_images(d)
            if not imgs:
                log(f"[警告] 目录无图片，跳过: {d}")
                continue
            plan.append((cat, typ, ano, pv, d, imgs))

    if not plan:
        log("[错误] 没有任何可复制的图片")
        return 2

    # 5) 输出目录
    if out_override:
        out_dir = Path(out_override)
    else:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir = SCRIPT_DIR / "grabbed" / ts
    if not dry_run:
        out_dir.mkdir(parents=True, exist_ok=True)

    # 6) 复制 + 重命名
    used = set()
    manifest_rows = []
    for cat, typ, ano, pv, d, imgs in plan:
        vn = view_number_of(d.name)
        prefix = f"{vn:02d}" if vn is not None else "00"
        idx = 1
        for img in imgs:
            ext = img.suffix.lower()
            base = safe_name(f"{prefix}-{idx:03d}{ext}", used, hint=d.name)
            dest = out_dir / base
            if dry_run:
                log(f"[DRY-RUN] {img}  ->  {dest}")
            else:
                shutil.copy2(img, dest)
            manifest_rows.append({
                "output": base,
                "source": str(img),
                "view_dir": str(d),
                "category": cat,
                "type": typ,
                "anomaly": ano,
                "point_view": pv,
                "view_prefix": prefix,
            })
            idx += 1

    total = len(manifest_rows)
    log(f"共复制 {total} 张图片到 {out_dir}")

    # 7) 写描述
    desc_path = out_dir / "description.txt"
    if dry_run:
        log(f"[DRY-RUN] 将写入描述: {desc_path}")
    else:
        with desc_path.open("w", encoding="utf-8") as fh:
            fh.write(desc)
            if desc and not desc.endswith("\n"):
                fh.write("\n")
            fh.write("\n# ---- 抓取清单 (自动生成) ----\n")
            for r in manifest_rows:
                fh.write(f"# {r['output']}  <-  {r['source']}\n")

    # 8) 写 manifest.csv
    if not dry_run:
        with (out_dir / "manifest.csv").open("w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(
                fh,
                fieldnames=["output", "source", "view_dir",
                            "category", "type", "anomaly", "point_view", "view_prefix"],
            )
            w.writeheader()
            w.writerows(manifest_rows)

    # 9) 打包
    if no_zip:
        log("已跳过压缩包 (NO_ZIP)")
        return 0
    if dry_run:
        log(f"[DRY-RUN] 将打包为 {out_dir}.zip")
        return 0
    zip_path = shutil.make_archive(str(out_dir), "zip", out_dir)
    log(f"已生成压缩包: {zip_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
