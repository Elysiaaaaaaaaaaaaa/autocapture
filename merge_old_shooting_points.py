#!/usr/bin/env python3
"""
将 material 数据集中旧拍摄点位目录，合并/重命名为新点位命名。

新旧映射:
  tianping  -> analytical_balance          (天平 -> 分析天平)
  stack1    -> beaker_sample_carousel      (栈1 -> 烧杯样品盘)
  stack2    -> plate_reservoir_sample_carousel  (栈2 -> 孔板样品盘)
  stack3    -> mixed_sample_carousel_level6  (栈3 -> 混合样品盘-level6)

目录叶节点格式: <point>-<view>，例如 tianping-001 -> analytical_balance-001

示例:
  # 预览
  python merge_old_shooting_points.py --dry-run

  # 实际执行（默认 root 取 path_config_material.DATASET_ROOT）
  python merge_old_shooting_points.py

  # 指定根目录
  python merge_old_shooting_points.py --root "/path/to/material"
"""

import argparse
import shutil
import sys
from pathlib import Path

from path_config_material import DATASET_ROOT

# 旧英文点位名 -> 新英文点位名
POINT_RENAME: dict[str, str] = {
    "tianping": "analytical_balance",
    "stack1": "beaker_sample_carousel",
    "stack2": "plate_reservoir_sample_carousel",
    "stack3": "mixed_sample_carousel-level6",
}


def parse_leaf(name: str) -> tuple[str, str] | None:
    """若 name 形如 <old_point>-<view>，返回 (old_point, view_suffix)；否则 None。"""
    for old in POINT_RENAME:
        prefix = old + "-"
        if name.startswith(prefix) and len(name) > len(prefix):
            return old, name[len(prefix) :]
    return None


def find_renames(root: Path) -> list[tuple[Path, Path]]:
    """遍历数据集，返回 [(src_dir, dst_dir), ...]。"""
    pairs = []
    for path in sorted(root.rglob("*")):
        if not path.is_dir():
            continue
        parsed = parse_leaf(path.name)
        if parsed is None:
            continue
        old_point, view = parsed
        new_point = POINT_RENAME[old_point]
        dst = path.parent / f"{new_point}-{view}"
        pairs.append((path, dst))
    return pairs


def merge_or_move(src: Path, dst: Path, dry_run: bool = False) -> tuple[str, int, int]:
    """
    目标不存在：直接 rename。
    目标已存在：逐项合并子文件/子目录；同名冲突则跳过。
    返回 (action, moved, skipped)。
    """
    if not dst.exists():
        if dry_run:
            print(f"[dry-run] mv  {src}")
            print(f"          -> {dst}")
            return "move", 1, 0
        shutil.move(str(src), str(dst))
        print(f"已重命名: {src} -> {dst}")
        return "move", 1, 0

    moved = 0
    skipped = 0
    children = list(src.iterdir())
    if not children:
        if dry_run:
            print(f"[dry-run] 源目录为空，将删除: {src}")
        else:
            src.rmdir()
            print(f"源目录为空，已删除: {src}")
        return "merge", 0, 0

    for child in children:
        target = dst / child.name
        if target.exists():
            print(f"跳过(目标已存在): {child} -> {target}")
            skipped += 1
            continue
        if dry_run:
            print(f"[dry-run] mv  {child}")
            print(f"          -> {target}")
            moved += 1
            continue
        shutil.move(str(child), str(target))
        print(f"已合并: {child} -> {target}")
        moved += 1

    if not dry_run:
        remaining = list(src.iterdir())
        if not remaining:
            src.rmdir()
            print(f"已清空并删除源目录: {src}")
        else:
            print(f"源目录仍有 {len(remaining)} 项未移动，保留: {src}")

    return "merge", moved, skipped


def main() -> int:
    parser = argparse.ArgumentParser(
        description="将 material 数据集旧拍摄点位目录合并到新点位命名",
    )
    parser.add_argument(
        "--root",
        type=str,
        default=str(DATASET_ROOT),
        help=f"数据集根目录（默认: {DATASET_ROOT}）",
    )
    parser.add_argument("--dry-run", action="store_true", help="只预览，不实际移动")
    args = parser.parse_args()

    root = Path(args.root)
    if not root.is_dir():
        print(f"错误: {root} 不是有效目录")
        return 1

    print("点位映射:")
    for old, new in POINT_RENAME.items():
        print(f"  {old} -> {new}")
    print()

    pairs = find_renames(root)
    if not pairs:
        print("未找到使用旧点位命名的目录。")
        return 0

    by_old: dict[str, int] = {}
    for src, _ in pairs:
        old = parse_leaf(src.name)[0]
        by_old[old] = by_old.get(old, 0) + 1
    print(f"找到 {len(pairs)} 个待处理目录:")
    for old in POINT_RENAME:
        if old in by_old:
            print(f"  {old}: {by_old[old]}")
    if args.dry_run:
        print("（预览模式）")
    print()

    total_moved = 0
    total_skipped = 0
    rename_count = 0
    merge_count = 0
    for src, dst in pairs:
        action, moved, skipped = merge_or_move(src, dst, dry_run=args.dry_run)
        total_moved += moved
        total_skipped += skipped
        if action == "move":
            rename_count += 1
        else:
            merge_count += 1

    print()
    if args.dry_run:
        print(
            f"预览完成: {len(pairs)} 处"
            f"（直接重命名 {rename_count}，需合并 {merge_count}），"
            f"约移动 {total_moved} 项，跳过冲突 {total_skipped} 项。"
            f"去掉 --dry-run 后执行。"
        )
    else:
        print(
            f"完成: {len(pairs)} 处"
            f"（直接重命名 {rename_count}，合并 {merge_count}），"
            f"移动 {total_moved} 项，跳过冲突 {total_skipped} 项。"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
