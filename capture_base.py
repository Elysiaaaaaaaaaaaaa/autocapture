#!/usr/bin/env python3
import argparse
import concurrent.futures
import sys
from pathlib import Path

import cv2
import numpy as np

from path_config_standard import *


def _create_dry_run_placeholder(output_file: Path) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    img = np.full((480, 640, 3), 160, dtype=np.uint8)
    label = output_file.name
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.8
    thickness = 2
    (tw, th), _ = cv2.getTextSize(label, font, font_scale, thickness)
    x = (640 - tw) // 2
    y = (480 + th) // 2
    cv2.putText(img, label, (x, y), font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)
    cv2.imwrite(str(output_file), img)
    print(f"[DRY-RUN] {output_file}")


def frame_to_bgr_image(frame) -> np.ndarray | None:
    from pyorbbecsdk import (
        FormatConvertFilter,
        OBConvertFormat,
        OBFormat,
    )

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
    import pyrealsense2 as rs
    from pyorbbecsdk import Context

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
    import pyrealsense2 as rs

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

        fmt = color_frame.get_profile().format()
        if fmt == rs.format.rgb8:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        elif fmt == rs.format.bgr8:
            pass
        else:
            print(f"警告: RealSense 未知格式 {fmt}，尝试直接保存")
            if len(image.shape) == 3 and image.shape[2] == 4:
                image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)

        output_file.parent.mkdir(parents=True, exist_ok=True)
        if not cv2.imwrite(str(output_file), image):
            raise RuntimeError(f"RealSense 图片保存失败: {output_file}")
        print(f"RealSense -> {output_file}")
    finally:
        pipeline.stop()


def capture_orbbec_single(serial: str, output_file: Path) -> None:
    from pyorbbecsdk import (
        Config,
        Context,
        OBError,
        OBFrameAggregateOutputMode,
        OBSensorType,
        Pipeline,
        VideoStreamProfile,
    )

    ctx = Context()
    device_list = ctx.query_devices()
    device = None
    for i in range(device_list.get_count()):
        if device_list.get_device_serial_number_by_index(i) == serial:
            device = device_list.get_device_by_index(i)
            break
    if device is None:
        raise RuntimeError(f"未找到序列号为 {serial} 的 Orbbec 设备")

    pipeline = Pipeline(device)
    config = Config()
    profile_list = pipeline.get_stream_profile_list(OBSensorType.COLOR_SENSOR)
    if profile_list is None:
        raise RuntimeError(f"Orbbec {serial} 不支持彩色流")
    color_profile: VideoStreamProfile = profile_list.get_default_video_stream_profile()
    config.enable_stream(color_profile)
    config.set_frame_aggregate_output_mode(OBFrameAggregateOutputMode.FULL_FRAME_REQUIRE)

    try:
        pipeline.start(config)
    except OBError as exc:
        raise RuntimeError(f"Orbbec {serial} 启动失败: {exc}") from exc

    try:
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
                output_file.parent.mkdir(parents=True, exist_ok=True)
                if not cv2.imwrite(str(output_file), image):
                    raise RuntimeError(f"Orbbec {serial} 图片保存失败: {output_file}")
                print(f"Orbbec {serial} -> {output_file}")
                return

        raise RuntimeError(f"Orbbec {serial} 未获取到有效彩色帧")
    finally:
        pipeline.stop()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="采集 1 台 RealSense + 2 台 Orbbec 彩色图并保存到数据集目录（并行采集）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
{format_containers()}

{format_anomaly_types()}

示例:
  # beaker/normal/magnetic_stirrer_01-001/ 下第 1 张
  python capture.py 1 1 - magnetic_stirrer_01 1 1

  # 同一视角 magnetic_stirrer_01-001 下第 2 张
  python capture.py 1 1 - magnetic_stirrer_01 1 2

  # 换视角 magnetic_stirrer_01-002 下第 1 张
  python capture.py 1 1 - magnetic_stirrer_01 2 1

  # beaker/damage/crack/magnetic_stirrer_01-001/
  python capture.py 1 3 crack magnetic_stirrer_01 1 1

参数说明:
  1. 容器编号     1-13，见上方列表
  2. 异常类型     1-8，见上方列表
  3. 小类         第三层文件夹名；正常类填 {NO_SUBCATEGORY}
  4. 拍摄点位     如 magnetic_stirrer_01 / beaker_sample_carousel
  5. 视角编号     决定文件夹名，如 1 -> magnetic_stirrer_01-001，2 -> magnetic_stirrer_01-002
  6. 照片编号     文件夹内的第几张，如 1 -> 001_Color.png 和 top1/

保存规则:
  - 目录: {{拍摄点位}}-{{视角编号:03d}}/，如 magnetic_stirrer_01-001
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
        help="异常类型编号 (1-8)",
    )
    parser.add_argument(
        "sub_anomaly",
        nargs="?",
        help=f"小类文件夹名；正常类填 {NO_SUBCATEGORY}，如 crack / water_stain / crystalline_residue",
    )
    parser.add_argument(
        "shooting_point",
        nargs="?",
        help="拍摄点位名，如 magnetic_stirrer_01 / beaker_sample_carousel",
    )
    parser.add_argument(
        "view_number",
        nargs="?",
        type=int,
        help="视角编号，决定文件夹名，如 1 -> magnetic_stirrer_01-001",
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
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="不连接相机，在目标路径保存带文件名水印的灰色占位图，用于验证路径配置",
    )
    return parser.parse_args()


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
    orbbec_dir = shot_dir / f"view_top_{args.photo_number}"
    orbbec_c1_file = orbbec_dir / "camera1_Color.png"
    orbbec_c2_file = orbbec_dir / "camera2_Color.png"

    print(f"保存目录: {shot_dir}")

    if args.dry_run:
        for f in (realsense_file, orbbec_c1_file, orbbec_c2_file):
            _create_dry_run_placeholder(f)
        print("DRY-RUN 完成 — 未连接任何相机")
        return 0

    from pyorbbecsdk import Context

    ctx = Context()
    device_list = ctx.query_devices()
    count = device_list.get_count()
    if count != 2:
        print(f"需要 2 台 Orbbec 相机，当前检测到 {count} 台", file=sys.stderr)
        return 1

    serials = [device_list.get_device_serial_number_by_index(i) for i in range(count)]
    if ORBBEC_C1_SERIAL not in serials:
        print(f"未找到 c1 相机 (SN={ORBBEC_C1_SERIAL})", file=sys.stderr)
        return 1

    c1_serial = ORBBEC_C1_SERIAL
    c2_serial = [s for s in serials if s != c1_serial][0]

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(capture_realsense_color, realsense_file),
            executor.submit(capture_orbbec_single, c1_serial, orbbec_c1_file),
            executor.submit(capture_orbbec_single, c2_serial, orbbec_c2_file),
        ]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as exc:
                print(f"采集过程中发生错误: {exc}", file=sys.stderr)
                return 1

    print("采集完成")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
