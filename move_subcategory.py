#!/usr/bin/env python3
"""
将某个异常大类下的小类目录，批量移动到另一个异常大类下。

目录层级（规范命名）:
  <container>/<anomaly_type>/<subcategory>/<scene>/...

示例:
  # 预览：把所有容器下 damage/crack 移到 stain/crack
  python move_subcategory.py --from damage --sub crack --to stain --dry-run

  # 实际执行，且只处理 beaker
  python move_subcategory.py --from damage --sub crack --to stain --container beaker

  # 移动同时改名小类
  python move_subcategory.py --from solid_residue --sub powder --to stain --rename powder_stain

  # 列出某大类下已有小类
  python move_subcategory.py --list --from damage
"""

import argparse
import shutil
import sys
from pathlib import Path

from path_config_standard import DATASET_ROOT


def iter_containers(root, container=None):
    if container:
        path = root / container
        if not path.is_dir():
            raise SystemExit(f"错误: 容器目录不存在: {path}")
        yield path
        return
    for path in sorted(p for p in root.iterdir() if p.is_dir()):
        yield path


def find_moves(root, src_anomaly, subcategory, dst_anomaly, container=None, new_name=None):
    """返回 [(src_dir, dst_dir), ...]"""
    dest_sub = new_name or subcategory
    moves = []
    for cont in iter_containers(root, container):
        src = cont / src_anomaly / subcategory
        if not src.is_dir():
            continue
        dst = cont / dst_anomaly / dest_sub
        moves.append((src, dst))
    return moves


def list_subcategories(root, src_anomaly, container=None):
    found = {}
    for cont in iter_containers(root, container):
        anomaly_dir = cont / src_anomaly
        if not anomaly_dir.is_dir():
            continue
        subs = sorted(p.name for p in anomaly_dir.iterdir() if p.is_dir())
        if subs:
            found[cont.name] = subs
    return found


def merge_or_move(src, dst, dry_run=False):
    """
    若目标不存在：直接 rename/move 整个小类目录。
    若目标已存在：逐个子目录合并；同名子目录冲突则跳过并报告。
    """
    if not dst.exists():
        if dry_run:
            print(f"[dry-run] mv  {src}")
            print(f"          -> {dst}")
            return "move", 1, 0
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        print(f"已移动: {src} -> {dst}")
        return "move", 1, 0

    # 目标已存在，合并子项（通常是拍摄场景目录）
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
        # 源目录若已空则删除；若还有冲突残留则保留
        remaining = list(src.iterdir())
        if not remaining:
            src.rmdir()
            print(f"已清空并删除源目录: {src}")
        else:
            print(f"源目录仍有 {len(remaining)} 项未移动，保留: {src}")

    return "merge", moved, skipped


def main():
    parser = argparse.ArgumentParser(
        description="批量将异常小类目录从一个大类移动到另一个大类",
    )
    parser.add_argument(
        "--root",
        type=str,
        default=str(DATASET_ROOT),
        help=f"数据集根目录（默认: {DATASET_ROOT}）",
    )
    parser.add_argument("--from", dest="src_anomaly", required=True, help="源异常大类名，如 damage")
    parser.add_argument("--to", dest="dst_anomaly", help="目标异常大类名，如 stain")
    parser.add_argument("--sub", dest="subcategory", help="要移动的小类名，如 crack")
    parser.add_argument("--rename", dest="new_name", help="移动后的小类新名称（可选）")
    parser.add_argument("--container", help="只处理指定容器（默认处理全部容器）")
    parser.add_argument("--list", action="store_true", help="列出源大类下已有小类后退出")
    parser.add_argument("--dry-run", action="store_true", help="只预览，不实际移动")
    args = parser.parse_args()

    root = Path(args.root)
    if not root.is_dir():
        print(f"错误: {root} 不是有效目录")
        return 1

    if args.list:
        found = list_subcategories(root, args.src_anomaly, args.container)
        if not found:
            print(f"未找到大类 '{args.src_anomaly}' 下的小类目录")
            return 0
        print(f"大类 '{args.src_anomaly}' 下的小类:")
        for cont, subs in found.items():
            print(f"  {cont}: {', '.join(subs)}")
        return 0

    if not args.dst_anomaly or not args.subcategory:
        print("错误: 移动操作需要同时提供 --to 和 --sub（或使用 --list 查看）")
        return 1

    if args.src_anomaly == args.dst_anomaly and not args.new_name:
        print("错误: 源大类与目标大类相同，且未指定 --rename，无需移动")
        return 1

    moves = find_moves(
        root,
        args.src_anomaly,
        args.subcategory,
        args.dst_anomaly,
        container=args.container,
        new_name=args.new_name,
    )

    if not moves:
        scope = args.container or "全部容器"
        print(
            f"未找到待移动目录: <container>/{args.src_anomaly}/{args.subcategory}/ "
            f"（范围: {scope}）"
        )
        return 0

    dest_sub = args.new_name or args.subcategory
    print(
        f"将移动 {len(moves)} 处: "
        f".../{args.src_anomaly}/{args.subcategory}/ "
        f"-> .../{args.dst_anomaly}/{dest_sub}/"
    )
    if args.dry_run:
        print("（预览模式）\n")

    total_moved = 0
    total_skipped = 0
    for src, dst in moves:
        _, moved, skipped = merge_or_move(src, dst, dry_run=args.dry_run)
        total_moved += moved
        total_skipped += skipped

    print()
    if args.dry_run:
        print(
            f"预览完成: 将处理 {len(moves)} 处，"
            f"约移动 {total_moved} 项，跳过冲突 {total_skipped} 项。"
            f"去掉 --dry-run 后执行。"
        )
    else:
        print(
            f"完成: 处理 {len(moves)} 处，"
            f"移动 {total_moved} 项，跳过冲突 {total_skipped} 项。"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
