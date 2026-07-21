#!/usr/bin/env python3
"""
根据 chosen.csv 仅保留其中列出的图片，删除数据集中其余所有图片文件。
"""

import sys
import csv
from pathlib import Path

DATASET_ROOT = Path("/home/qy/dataset-202607/quality test/empty_container")
CSV_PATH = Path(__file__).parent / "chosen.csv"

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp"}


def resolve_path(row, root):
    cat = row["object_category"]
    rel = row["source_relative_path"]
    rel = rel.replace("\\", "/")
    if rel.startswith(cat + "/"):
        return (root / rel).resolve()
    else:
        return (root / cat / rel).resolve()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="仅保留 chosen.csv 中的图片，删除其余所有图片")
    parser.add_argument("--root", type=str, default=str(DATASET_ROOT),
                        help="数据集根目录，默认 %(default)s")
    parser.add_argument("--csv", type=str, default=str(CSV_PATH),
                        help="CSV 文件路径，默认 %(default)s")
    parser.add_argument("--dry-run", action="store_true",
                        help="只预览不实际删除")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    csv_path = Path(args.csv)

    if not csv_path.is_file():
        print(f"错误: {csv_path} 不存在")
        return 1
    if not root.is_dir():
        print(f"错误: {root} 不是有效目录")
        return 1

    keep_set = set()
    with csv_path.open(encoding="gbk") as f:
        reader = csv.DictReader(f)
        for row in reader:
            keep_set.add(resolve_path(row, root))

    print(f"chosen.csv 共 {len(keep_set)} 条唯一路径")

    deleted = 0
    skipped = 0
    errors = 0

    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        resolved = p.resolve()
        if resolved in keep_set:
            skipped += 1
            continue
        if args.dry_run:
            print(f"[dry-run] 将删除: {resolved}")
        else:
            try:
                p.unlink()
                print(f"已删除: {resolved}")
            except Exception as e:
                print(f"删除失败: {resolved} ({e})")
                errors += 1
        deleted += 1

    kept = len(keep_set)
    print(f"\n总计: 保留 {kept}, 跳过 {skipped}, 删除 {deleted}, 失败 {errors}")

    # 检查 chosen.csv 中有哪些路径在数据集中不存在
    missing = [p for p in keep_set if not p.is_file()]
    if missing:
        print(f"\nchosen.csv 中有 {len(missing)} 条路径在数据集中未找到:")
        for p in missing:
            print(f"  未找到: {p}")
    else:
        print("\nchosen.csv 中的所有路径均在数据集中找到。")

    if args.dry_run:
        print("这是预览模式，未实际删除任何文件。去掉 --dry-run 执行删除。")
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
