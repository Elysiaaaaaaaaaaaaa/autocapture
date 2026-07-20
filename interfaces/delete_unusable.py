#!/usr/bin/env python3
"""
根据 unusable_images.csv 批量删除数据集中无法使用的图片。
"""

import sys
import csv
from pathlib import Path

DATASET_ROOT = Path("/home/qy/dataset-202607/quality test/empty_container")
CSV_PATH = Path(__file__).parent / "unusable_images.csv"


def main():
    import argparse
    parser = argparse.ArgumentParser(description="批量删除数据集中无法使用的图片")
    parser.add_argument("--root", type=str, default=str(DATASET_ROOT),
                        help="数据集根目录，默认 %(default)s")
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

    deleted = 0
    not_found = 0

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rel = row["source_relative_path"]
            # source_relative_path 以 "empty_container/" 开头，去掉该前缀
            if rel.startswith("empty_container/"):
                rel = rel[len("empty_container/"):]
            file_path = root / rel

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

    print(f"\n总计: 处理 {deleted + not_found}, 删除 {deleted}, 未找到 {not_found}")
    if args.dry_run:
        print("这是预览模式，未实际删除任何文件。去掉 --dry-run 执行删除。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
