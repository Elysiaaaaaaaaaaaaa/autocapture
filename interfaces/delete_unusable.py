#!/usr/bin/env python3
"""
根据 CSV 文件批量移除数据集中无法使用的图片（默认移入回收目录，可恢复）。

支持两种 CSV 格式（自动检测）：
  1. 带 source_relative_path 列（如 unusable_images.csv）—— 路径以 empty_container/ 开头
  2. 带 image_path 列（如 delete.csv）—— 完整绝对路径，自动提取 empty_container/... 部分

无论哪种格式，最终路径统一为：--root / empty_container/...（相对路径部分）

CSV 中绝对路径的系统风格用 --system 指定：
  win — Windows 路径（反斜杠，如 D:\\...\\empty_container\\...）
  lin — Linux 路径（正斜杠，如 /home/.../empty_container/...）

默认将文件移动到 --trash（保留相对路径），可用 --restore 移回数据集；
加 --purge 才真正删除（不可恢复）。
"""

import sys
import csv
import shutil
from pathlib import Path

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp"}


def count_images(directory: Path) -> int:
    """递归统计目录下的图片数量"""
    if not directory.is_dir():
        return 0
    count = 0
    for entry in directory.rglob("*"):
        if entry.is_file() and entry.suffix.lower() in IMAGE_EXTENSIONS:
            count += 1
    return count


def extract_empty_container_rel(abs_path_str: str, system: str) -> Path | None:
    """从绝对路径中提取 empty_container/... 之后的相对路径部分。

    system: 'win' 按 Windows 反斜杠拆分；'lin' 按 Linux 正斜杠拆分。
    """
    s = abs_path_str.strip().strip('"')
    if system == "win":
        s = s.replace("\\", "/")
    parts = Path(s).parts
    try:
        idx = parts.index("empty_container")
        return Path(*parts[idx:])
    except ValueError:
        print(f"警告: 路径中未找到 'empty_container' 目录: {s}")
        return None


def resolve_rel(row, use_absolute: bool, system: str) -> Path | None:
    """从 CSV 行解析出相对 --root 的路径（以 empty_container/ 开头）。"""
    if use_absolute:
        return extract_empty_container_rel(row["image_path"], system)
    rel = row["source_relative_path"].strip().strip('"').replace("\\", "/")
    return Path(rel)


def move_file(src: Path, dst: Path, dry_run: bool, verb: str) -> bool:
    """移动文件，必要时创建父目录。成功返回 True。"""
    if dry_run:
        print(f"[dry-run] 将{verb}: {src} -> {dst}")
        return True
    if dst.exists():
        print(f"跳过（目标已存在）: {dst}")
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dst))
    print(f"已{verb}: {src} -> {dst}")
    return True


# --root 默认指向 empty_container 的父目录，统一 + empty_container/... 构建完整路径
DATASET_ROOT = Path("/home/qy/dataset-202607/quality test/dataset")
CSV_PATH = Path(__file__).parent / "unusable_images.csv"
DEFAULT_TRASH_NAME = ".unusable_trash"


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="批量移除无法使用的图片（默认移入回收目录，可 --restore 恢复）"
    )
    parser.add_argument("--root", type=str, default=str(DATASET_ROOT),
                        help="数据集根目录（empty_container 的父目录），默认 %(default)s")
    parser.add_argument("--csv", type=str, default=str(CSV_PATH),
                        help="CSV 文件路径，默认 %(default)s")
    parser.add_argument("--system", choices=["win", "lin"], default="lin",
                        help="CSV 中绝对路径的系统类型：win=Windows 反斜杠，lin=Linux 正斜杠，默认 %(default)s")
    parser.add_argument("--trash", type=str, default=None,
                        help=f"回收目录路径，默认 <root>/{DEFAULT_TRASH_NAME}")
    parser.add_argument("--restore", action="store_true",
                        help="从回收目录按 CSV 列表移回数据集（恢复）")
    parser.add_argument("--purge", action="store_true",
                        help="真正删除（不可恢复）。默认只是移到回收目录")
    parser.add_argument("--dry-run", action="store_true",
                        help="只预览不实际移动/删除")
    args = parser.parse_args()

    if args.restore and args.purge:
        print("错误: --restore 与 --purge 不能同时使用")
        return 1

    root = Path(args.root)
    csv_path = Path(args.csv)
    trash_root = Path(args.trash) if args.trash else root / DEFAULT_TRASH_NAME

    if not csv_path.is_file():
        print(f"错误: {csv_path} 不存在")
        return 1
    if not root.is_dir():
        print(f"错误: {root} 不是有效目录")
        return 1
    if args.restore and not trash_root.is_dir():
        print(f"错误: 回收目录不存在: {trash_root}")
        return 1

    # 读取第一行检测 CSV 格式（用 utf-8-sig 兼容 BOM）
    with open(csv_path, encoding="utf-8-sig") as f:
        first_row = f.readline().strip()

    use_absolute = "image_path" in first_row and "source_relative_path" not in first_row

    empty_container_dir = root / "empty_container"
    before_count = count_images(empty_container_dir)

    ok = 0
    not_found = 0
    skipped = 0

    with open(csv_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rel = resolve_rel(row, use_absolute, args.system)
            if rel is None:
                not_found += 1
                continue

            dataset_path = root / rel
            trash_path = trash_root / rel

            if args.restore:
                src, dst, verb = trash_path, dataset_path, "恢复"
            elif args.purge:
                # 优先删数据集中的文件；若不在则删回收目录中的副本
                if dataset_path.exists():
                    src, dst, verb = dataset_path, None, "永久删除"
                elif trash_path.exists():
                    src, dst, verb = trash_path, None, "永久删除"
                else:
                    print(f"未找到: {dataset_path}")
                    not_found += 1
                    continue
            else:
                src, dst, verb = dataset_path, trash_path, "移入回收目录"

            if not src.exists():
                print(f"未找到: {src}")
                not_found += 1
                continue

            if args.purge:
                if args.dry_run:
                    print(f"[dry-run] 将{verb}: {src}")
                    ok += 1
                else:
                    src.unlink()
                    print(f"已{verb}: {src}")
                    ok += 1
            else:
                if move_file(src, dst, args.dry_run, verb):
                    ok += 1
                else:
                    skipped += 1

    if args.dry_run:
        after_count = before_count
    else:
        after_count = count_images(empty_container_dir)

    action = "恢复" if args.restore else ("永久删除" if args.purge else "移入回收目录")
    print(f"\n总计: 处理 {ok + not_found + skipped}, {action} {ok}, "
          f"未找到 {not_found}, 跳过 {skipped}")
    print(f"数据集 empty_container 保留: {after_count} 张图片")
    if before_count != after_count:
        print(f"     （处理前 {before_count} 张 → 处理后 {after_count} 张）")
    if not args.purge and not args.restore:
        print(f"回收目录: {trash_root}")
    if args.dry_run:
        print("这是预览模式，未实际修改任何文件。去掉 --dry-run 执行操作。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
