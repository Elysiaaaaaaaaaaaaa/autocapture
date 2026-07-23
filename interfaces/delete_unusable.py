#!/usr/bin/env python3
"""
根据 CSV 文件批量删除数据集中无法使用的图片。

支持两种 CSV 格式（自动检测）：
  1. 带 source_relative_path 列（如 unusable_images.csv）—— 路径以 empty_container/ 开头
  2. 带 image_path 列（如 delete.csv）—— 完整绝对路径，自动提取 empty_container/... 部分

无论哪种格式，最终删除路径统一为：--root / empty_container/...（相对路径部分）
"""

import sys
import csv
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


def extract_empty_container_rel(abs_path_str: str) -> Path | None:
    """从绝对路径中提取 empty_container/... 之后的相对路径部分"""
    p = Path(abs_path_str.strip('"'))
    try:
        idx = p.parts.index("empty_container")
        return Path(*p.parts[idx:])
    except ValueError:
        print(f"警告: 路径中未找到 'empty_container' 目录: {p}")
        return None


# --root 默认指向 empty_container 的父目录，统一 + empty_container/... 构建完整路径
DATASET_ROOT = Path("/home/qy/dataset-202607/quality test/dataset")
CSV_PATH = Path(__file__).parent / "unusable_images.csv"


def main():
    import argparse
    parser = argparse.ArgumentParser(description="批量删除数据集中无法使用的图片")
    parser.add_argument("--root", type=str, default=str(DATASET_ROOT),
                        help="数据集根目录（empty_container 的父目录），默认 %(default)s")
    parser.add_argument("--csv", type=str, default=str(CSV_PATH),
                        help="CSV 文件路径，默认 %(default)s")
    parser.add_argument("--dry-run", action="store_true",
                        help="只预览不实际删除")
    args = parser.parse_args()

    root = Path(args.root)
    csv_path = Path(args.csv)

    if not csv_path.is_file():
        print(f"错误: {csv_path} 不存在")
        return 1
    if not root.is_dir():
        print(f"错误: {root} 不是有效目录")
        return 1

    # 读取第一行检测 CSV 格式（用 utf-8-sig 兼容 BOM）
    with open(csv_path, encoding="utf-8-sig") as f:
        first_row = f.readline().strip()

    use_absolute = "image_path" in first_row and "source_relative_path" not in first_row

    # 只统计 empty_container 目录下的图片（删除操作仅影响该子目录）
    empty_container_dir = root / "empty_container"
    before_count = count_images(empty_container_dir)

    deleted = 0
    not_found = 0

    with open(csv_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if use_absolute:
                # 从绝对路径中提取 empty_container/... 再拼接 --root
                rel = extract_empty_container_rel(row["image_path"])
                if rel is None:
                    not_found += 1
                    continue
                file_path = root / rel
            else:
                # 相对路径格式（unusable_images.csv），直接以 empty_container/... 形式拼接
                file_path = root / row["source_relative_path"]

            if not file_path.exists():
                print(f"未找到: {file_path}")
                not_found += 1
                continue

            if args.dry_run:
                print(f"[dry-run] 将删除: {file_path}")
            else:
                file_path.unlink()
                print(f"已删除: {file_path}")
            deleted += 1

    # 处理后统计剩余
    if args.dry_run:
        after_count = before_count  # 未实际删除，数量不变
    else:
        after_count = count_images(empty_container_dir)

    print(f"\n总计: 处理 {deleted + not_found}, 删除 {deleted}, 未找到 {not_found}")
    print(f"保留: {after_count} 张图片")
    if before_count != after_count:
        print(f"     （处理前 {before_count} 张 → 处理后 {after_count} 张）")
    if args.dry_run:
        print("这是预览模式，未实际删除任何文件。去掉 --dry-run 执行删除。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
