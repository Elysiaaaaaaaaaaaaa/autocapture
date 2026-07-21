#!/usr/bin/env python3
"""Capture color frames from 1 RealSense and 2 Orbbec cameras."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np
import pyrealsense2 as rs
from pyorbbecsdk import (
    Config,
    Context,
    FormatConvertFilter,
    OBConvertFormat,
    OBError,
    OBFormat,
    OBFrameAggregateOutputMode,
    OBSensorType,
    Pipeline,
    VideoFrame,
    VideoStreamProfile,
)

DATASET_ROOT = Path("/home/qy/dataset-202607/quality test/dataset/empty_container")
ORBBEC_C1_SERIAL = "CL8K14100H4"
WARMUP_FRAMES = 100

# 异常类型编号 -> 第二层目录名
# 1 正常（无小类子目录，小类参数填 -）
# 2 主体破损
# 3 粉末残留
# 4 液体残留
# 5 污渍
# 6 object residue（物体残留）
# 7 tag（标签异常）
ANOMALY_TYPES: dict[int, str] = {
    1: "正常",
    2: "主体破损",
    3: "粉末残留",
    4: "液体残留",
    5: "污渍",
    6: "object residue",
    7: "tag",
}

# 各大类下已有的小类子目录（供校验和 --list-types 参考）
ANOMALY_SUBCATEGORIES: dict[int, list[str]] = {
    1: [],
    2: ["crack", "scratch", "wear"],
    3: ["bottom-powder", "crystal", "wall-powder"],
    4: ["color", "dip", "non-color"],
    5: ["color dirt", "water dirt"],
    6: ["glass rod"],
    7: ["damaged", "dirty", "fall"],
}

NO_SUBCATEGORY = "-"

# 容器编号 -> 第一层目录名
CONTAINERS: dict[int, str] = {
    1: "beaker",
    2: "test tube",
    3: "test tube modle2",
    4: "6-well plate",
    5: "11-well plate",
    6: "24-well plate",
    7: "48-well plate",
    8: "96-well plate modle1",
    9: "96-well plate modle 2",
    10: "magnetic mixer 1",
    11: "magnetic mixer 2",
    12: "rewservoir",
    13: "超声波清洗机器",
}


def format_containers() -> str:
    lines = ["容器编号:"]
    for code in sorted(CONTAINERS):
        lines.append(f"  {code} {CONTAINERS[code]}")
    return "\n".join(lines)


def resolve_container(container_id: int) -> str:
    if container_id not in CONTAINERS:
        known = ", ".join(str(code) for code in sorted(CONTAINERS))
        raise ValueError(f"未知容器编号 {container_id}，可选: {known}")
    return CONTAINERS[container_id]


def format_anomaly_types() -> str:
    lines = ["异常类型编号与小类:"]
    for code in sorted(ANOMALY_TYPES):
        name = ANOMALY_TYPES[code]
        subs = ANOMALY_SUBCATEGORIES[code]
        if subs:
            lines.append(f"  {code} {name}")
            lines.append(f"     小类: {', '.join(subs)}")
        else:
            lines.append(f"  {code} {name}（无小类，小类参数填 {NO_SUBCATEGORY}）")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="采集 1 台 RealSense + 2 台 Orbbec 彩色图并保存到数据集目录",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
{format_containers()}

{format_anomaly_types()}

示例:
  # beaker/主体破损/crack/mixer1-001/ 下第 1 张
  python capture.py 1 2 crack mixer1 1 1

  # 同一视角 mixer1-001 下第 2 张
  python capture.py 1 2 crack mixer1 1 2

  # 换视角 mixer1-002 下第 1 张
  python capture.py 1 2 crack mixer1 2 1

  # beaker/正常/mixer1-001/
  python capture.py 1 1 - mixer1 1 1

参数说明:
  1. 容器编号     1-13，见上方列表
  2. 异常类型     1-7，见上方列表
  3. 小类         第三层文件夹名；正常类填 {NO_SUBCATEGORY}
  4. 拍摄点位     如 mixer1 / stack1
  5. 视角编号     决定文件夹名，如 1 -> mixer1-001，2 -> mixer1-002
  6. 照片编号     文件夹内的第几张，如 1 -> 001_Color.png 和 top1/

保存规则:
  - 目录: {{拍摄点位}}-{{视角编号:03d}}/，如 mixer1-001
  - RealSense: {{目录}}/{{照片编号:03d}}_Color.png
  - Orbbec:    {{目录}}/top{{照片编号}}/c1_Color.png, c2_Color.png
    CL8K14100H4 -> c1，另一台 Orbbec -> c2
""",
    )
    parser.add_argument(
        "container",
        nargs="?",
        type=int,
        choices=sorted(CONTAINERS),
        help="容器编号 (1-13)",
    )
    parser.add_argument(
        "anomaly_type",
        nargs="?",
        type=int,
        choices=sorted(ANOMALY_TYPES),
        help="异常类型编号 (1-7)",
    )
    parser.add_argument(
        "sub_anomaly",
        nargs="?",
        help=f"小类文件夹名；正常类填 {NO_SUBCATEGORY}，如 crack / dirty / crystal",
    )
    parser.add_argument(
        "shooting_point",
        nargs="?",
        help="拍摄点位名，如 mixer1 / stack1",
    )
    parser.add_argument(
        "view_number",
        nargs="?",
        type=int,
        help="视角编号，决定文件夹名，如 1 -> mixer1-001",
    )
    parser.add_argument(
        "photo_number",
        nargs="?",
        type=int,
        help="照片编号，文件夹内的第几张，如 1 -> 001_Color.png 和 top1",
    )
    parser.add_argument(
        "--list-cameras",
        action="store_true",
        help="列出已连接的 RealSense / Orbbec 相机后退出",
    )
    parser.add_argument(
        "--list-types",
        action="store_true",
        help="列出容器编号、异常类型编号及对应小类后退出",
    )
    return parser.parse_args()


def build_shot_dir(
    container_id: int,
    anomaly_type: int,
    sub_anomaly: str,
    shooting_point: str,
    view_number: int,
) -> Path:
    container = resolve_container(container_id)
    anomaly_folder = ANOMALY_TYPES[anomaly_type]
    view_suffix = f"{view_number:03d}"
    point_name = shooting_point.strip("/")
    sub_name = sub_anomaly.strip()

    if not point_name or "/" in point_name:
        raise ValueError("拍摄点位应直接填写点位名，例如 mixer1")

    leaf = f"{point_name}-{view_suffix}"

    if anomaly_type == 1:
        if sub_name not in ("", NO_SUBCATEGORY):
            raise ValueError(f"正常类不需要小类，小类参数请填 {NO_SUBCATEGORY}")
        return DATASET_ROOT / container / anomaly_folder / leaf

    if sub_name in ("", NO_SUBCATEGORY):
        known = ", ".join(ANOMALY_SUBCATEGORIES[anomaly_type]) or "(无)"
        raise ValueError(
            f"异常类型 {anomaly_type} ({anomaly_folder}) 必须指定小类文件夹名，"
            f"可选: {known}"
        )

    known_subs = ANOMALY_SUBCATEGORIES[anomaly_type]
    if known_subs and sub_name not in known_subs:
        print(
            f"警告: 小类 '{sub_name}' 不在预设列表 [{', '.join(known_subs)}] 中，仍将使用该名称创建目录",
            file=sys.stderr,
        )

    return DATASET_ROOT / container / anomaly_folder / sub_name / leaf


def frame_to_bgr_image(frame: VideoFrame) -> np.ndarray | None:
    width = frame.get_width()
    height = frame.get_height()
    color_format = frame.get_format()
    data = np.asanyarray(frame.get_data())

    if color_format == OBFormat.RGB:
        image = np.resize(data, (height, width, 3))
        return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    if color_format == OBFormat.BGR:
        return np.resize(data, (height, width, 3))
    if color_format == OBFormat.YUYV:
        image = np.resize(data, (height, width, 2))
        return cv2.cvtColor(image, cv2.COLOR_YUV2BGR_YUYV)
    if color_format == OBFormat.UYVY:
        image = np.resize(data, (height, width, 2))
        return cv2.cvtColor(image, cv2.COLOR_YUV2BGR_UYVY)
    if color_format == OBFormat.MJPG:
        return cv2.imdecode(data, cv2.IMREAD_COLOR)

    convert_map = {
        OBFormat.I420: OBConvertFormat.I420_TO_RGB888,
        OBFormat.MJPG: OBConvertFormat.MJPG_TO_RGB888,
        OBFormat.YUYV: OBConvertFormat.YUYV_TO_RGB888,
        OBFormat.NV21: OBConvertFormat.NV21_TO_RGB888,
        OBFormat.NV12: OBConvertFormat.NV12_TO_RGB888,
        OBFormat.UYVY: OBConvertFormat.UYVY_TO_RGB888,
    }
    convert_format = convert_map.get(color_format)
    if convert_format is None:
        print(f"不支持的 Orbbec 彩色格式: {color_format}")
        return None

    convert_filter = FormatConvertFilter()
    convert_filter.set_format_convert_format(convert_format)
    rgb_frame = convert_filter.process(frame)
    if rgb_frame is None:
        return None

    rgb = np.asanyarray(rgb_frame.get_data())
    rgb = np.resize(rgb, (height, width, 3))
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)


def list_cameras() -> None:
    rs_ctx = rs.context()
    rs_devices = rs_ctx.query_devices()
    print(f"RealSense: {len(rs_devices)} 台")
    for dev in rs_devices:
        print(f"  - {dev.get_info(rs.camera_info.name)}  SN={dev.get_info(rs.camera_info.serial_number)}")

    ob_ctx = Context()
    ob_list = ob_ctx.query_devices()
    print(f"Orbbec: {ob_list.get_count()} 台")
    for index in range(ob_list.get_count()):
        serial = ob_list.get_device_serial_number_by_index(index)
        name = ob_list.get_device_name_by_index(index)
        role = "c1" if serial == ORBBEC_C1_SERIAL else "c2"
        print(f"  - {name}  SN={serial}  -> {role}")


def capture_realsense_color(output_file: Path) -> None:
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color)

    try:
        pipeline.start(config)
    except RuntimeError as exc:
        raise RuntimeError(f"RealSense 启动失败: {exc}") from exc

    try:
        for _ in range(WARMUP_FRAMES):
            pipeline.wait_for_frames()

        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        if not color_frame:
            raise RuntimeError("RealSense 未获取到彩色帧")

        image = np.asanyarray(color_frame.get_data())
        output_file.parent.mkdir(parents=True, exist_ok=True)
        if not cv2.imwrite(str(output_file), image):
            raise RuntimeError(f"RealSense 图片保存失败: {output_file}")
        print(f"RealSense -> {output_file}")
    finally:
        pipeline.stop()


def start_orbbec_color_pipeline(device) -> Pipeline:
    pipeline = Pipeline(device)
    config = Config()
    profile_list = pipeline.get_stream_profile_list(OBSensorType.COLOR_SENSOR)
    if profile_list is None:
        raise RuntimeError("Orbbec 设备不支持彩色流")
    color_profile: VideoStreamProfile = profile_list.get_default_video_stream_profile()
    config.enable_stream(color_profile)
    config.set_frame_aggregate_output_mode(OBFrameAggregateOutputMode.FULL_FRAME_REQUIRE)
    pipeline.start(config)
    return pipeline


def capture_orbbec_color(pipeline: Pipeline) -> np.ndarray:
    for _ in range(WARMUP_FRAMES):
        pipeline.wait_for_frames(1000)

    for _ in range(30):
        frames = pipeline.wait_for_frames(1000)
        if frames is None:
            continue
        color_frame = frames.get_color_frame()
        if color_frame is None:
            continue
        image = frame_to_bgr_image(color_frame)
        if image is not None:
            return image

    raise RuntimeError("Orbbec 未获取到有效彩色帧")


def capture_orbbec_cameras(top_dir: Path) -> None:
    ctx = Context()
    device_list = ctx.query_devices()
    count = device_list.get_count()
    if count != 2:
        raise RuntimeError(f"需要 2 台 Orbbec 相机，当前检测到 {count} 台")

    serials: list[str] = []
    for index in range(count):
        serial = device_list.get_device_serial_number_by_index(index)
        serials.append(serial)
        print(f"Orbbec[{index}] SN={serial} -> {'c1' if serial == ORBBEC_C1_SERIAL else 'c2'}")

    if ORBBEC_C1_SERIAL not in serials:
        raise RuntimeError(f"未找到 c1 相机 (SN={ORBBEC_C1_SERIAL})")

    top_dir.mkdir(parents=True, exist_ok=True)

    for serial in serials:
        role = "c1" if serial == ORBBEC_C1_SERIAL else "c2"
        output_file = top_dir / f"{role}_Color.png"
        device = device_list.get_device_by_serial_number(serial)
        pipeline = None
        try:
            pipeline = start_orbbec_color_pipeline(device)
            image = capture_orbbec_color(pipeline)
            if not cv2.imwrite(str(output_file), image):
                raise RuntimeError(f"Orbbec 图片保存失败: {output_file}")
            print(f"Orbbec {role} (SN={serial}) -> {output_file}")
        except OBError as exc:
            raise RuntimeError(f"Orbbec {role} (SN={serial}) 采集失败: {exc}") from exc
        finally:
            if pipeline is not None:
                pipeline.stop()


def main() -> int:
    args = parse_args()

    if args.list_cameras:
        list_cameras()
        return 0

    if args.list_types:
        print(format_containers())
        print()
        print(format_anomaly_types())
        return 0

    missing = [
        name
        for name, value in (
            ("container", args.container),
            ("anomaly_type", args.anomaly_type),
            ("sub_anomaly", args.sub_anomaly),
            ("shooting_point", args.shooting_point),
            ("view_number", args.view_number),
            ("photo_number", args.photo_number),
        )
        if value is None
    ]
    if missing:
        print(f"缺少参数: {', '.join(missing)}", file=sys.stderr)
        print("运行 python capture.py --help 查看用法", file=sys.stderr)
        return 1

    if args.view_number <= 0:
        print("视角编号必须是正整数", file=sys.stderr)
        return 1

    if args.photo_number <= 0:
        print("照片编号必须是正整数", file=sys.stderr)
        return 1

    try:
        shot_dir = build_shot_dir(
            args.container,
            args.anomaly_type,
            args.sub_anomaly,
            args.shooting_point,
            args.view_number,
        )
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1

    photo_id = f"{args.photo_number:03d}"
    realsense_file = shot_dir / f"{photo_id}_Color.png"
    orbbec_dir = shot_dir / f"top{args.photo_number}"

    print(f"保存目录: {shot_dir}")

    try:
        capture_realsense_color(realsense_file)
        capture_orbbec_cameras(orbbec_dir)
    except RuntimeError as exc:
        print(exc, file=sys.stderr)
        return 1

    print("采集完成")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
