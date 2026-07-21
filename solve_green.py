#!/usr/bin/env python3
"""
批量修复特定视角下 RealSense 图片的颜色（因通道顺序错误导致的偏绿）。
用法：python fix_color_by_views.py /path/to/dataset_root --views stack1-004 stack1-005
"""

import sys
from pathlib import Path
import cv2
import argparse

def fix_image(path: Path, dry_run: bool = False) -> None:
    """修复单张图片：BGR→RGB 通道互换（因为原图本质是 RGB 但存为 BGR）"""
    img = cv2.imread(str(path))
    if img is None:
        print(f"⚠️ 无法读取: {path}")
        return

    # 修复：将 BGR 顺序转为 RGB（保存时会自动再转回 BGR，所以最终正确）
    fixed = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    if dry_run:
        print(f"[dry-run] 将修复: {path}")
        return

    if not cv2.imwrite(str(path), fixed):
        print(f"❌ 保存失败: {path}")
    else:
        print(f"✅ 已修复: {path}")

def main():
    parser = argparse.ArgumentParser(
        description="批量修复特定视角的 RealSense 偏绿图片"
    )
    parser.add_argument("root", type=str, help="数据集根目录，例如 /home/qy/dataset-202607/quality test/dataset/empty_container")
    parser.add_argument("--views", nargs="+", required=True, help="要修复的视角目录名，例如 stack1-004 stack1-005")
    parser.add_argument("--dry-run", action="store_true", help="只预览不实际修改")
    parser.add_argument("--suffix", default="_Color.png", help="要修复的文件后缀，默认为 _Color.png")
    args = parser.parse_args()

    root = Path(args.root)
    if not root.is_dir():
        print(f"错误: {root} 不是有效目录")
        return 1

    view_set = set(args.views)
    pattern = f"*{args.suffix}"
    targets = []

    for p in root.rglob(pattern):
        parent = p.parent
        # 条件：父目录名在指定视角中，并且父目录的父目录不是 top*（即排除 Orbbec 图片）
        if parent.name in view_set and not parent.parent.name.startswith("top"):
            targets.append(p)

    if not targets:
        print(f"未找到需要修复的图片（视角: {', '.join(view_set)}）")
        return 0

    print(f"找到 {len(targets)} 个文件待修复")
    for p in targets:
        fix_image(p, dry_run=args.dry_run)

    if args.dry_run:
        print("\n这是预览模式，未实际修改任何文件。去掉 --dry-run 执行修复。")
    else:
        print("\n修复完成！")

    return 0

if __name__ == "__main__":
    sys.exit(main())