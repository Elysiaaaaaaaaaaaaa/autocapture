from pathlib import Path

DATASET_ROOT = Path("/home/qy/dataset-202607/quality test/empty_container")
ORBBEC_C1_SERIAL = "CL8K14100H4"
WARMUP_FRAMES = 40

# ---- 异常类型（来源：异常汇总.xlsx → Sheet3 清洗槽） ----
# Sheet3 定义了三类清洗槽特有异常：
#   异物残留（烧杯/6-96孔板/储液槽/螺丝）
#   水位异常（水位过高/水位过低）
#   水质污染（浑浊/带颜色）

ANOMALY_TYPES: dict[int, str] = {
    1: "normal",
    2: "foreign_object",
    3: "water_level_anomaly",
    4: "water_quality",
}

ANOMALY_SUBCATEGORIES: dict[int, list[str]] = {
    1: [],
    2: ["beaker", "well_plate", "reservoir", "screw"],
    3: ["water_level_high", "water_level_low"],
    4: ["turbid", "colored"],
}

NO_SUBCATEGORY = "-"

CONTAINERS: dict[int, str] = {
    1: "ultrasonic_cleaner",
}

CONTAINERS_CN: dict[int, str] = {
    1: "超声波清洗机",
}

ANOMALY_TYPES_CN: dict[int, str] = {
    1: "正常", 2: "异物残留", 3: "水位异常", 4: "水质污染",
}

ANOMALY_SUBCATEGORIES_CN: dict[str, str] = {
    "beaker": "烧杯", "well_plate": "孔板",
    "reservoir": "储液槽", "screw": "螺丝",
    "water_level_high": "水位过高", "water_level_low": "水位过低",
    "turbid": "浑浊", "colored": "带颜色",
}

# 清洗槽拍摄点位（三个槽位）
SHOOTING_POINTS: dict[str, str] = {
    "ultrasonic_cleaner_slot_01": "超声波清洗机槽1",
    "ultrasonic_cleaner_slot_02": "超声波清洗机槽2",
    "ultrasonic_cleaner_slot_03": "超声波清洗机槽3",
}

# 反向映射：中文 → 英文（供 GUI 下拉框使用）
SHOOTING_POINTS_CN: dict[str, str] = {v: k for k, v in SHOOTING_POINTS.items()}
SHOOTING_POINTS_CN_LIST: list[str] = list(SHOOTING_POINTS_CN.keys())

VIEW_NAMES: dict[int, str] = {
    1: "view_top_01",
    2: "view_top_02",
    3: "view_top_03",
    4: "view_top_04",
    5: "view_top_05",
    6: "view_top_06",
    7: "view_top_07",
}

IMAGE_NAMES: dict[str, str] = {
    "realsense": "view_{:03d}_rgb.png",
    "orbbec_c1": "camera_01_rgb.png",
    "orbbec_c2": "camera_02_rgb.png",
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
    lines = ["清洗槽异常类型编号与小类:"]
    for code in sorted(ANOMALY_TYPES):
        name = ANOMALY_TYPES[code]
        subs = ANOMALY_SUBCATEGORIES[code]
        if subs:
            lines.append(f"  {code} {name}")
            lines.append(f"     小类: {', '.join(subs)}")
        else:
            lines.append(f"  {code} {name}（无小类，小类参数填 {NO_SUBCATEGORY}）")
    return "\n".join(lines)


def format_shooting_points() -> str:
    lines = ["清洗槽拍摄点位:"]
    for name, desc in SHOOTING_POINTS.items():
        lines.append(f"  {name}  ({desc})")
    return "\n".join(lines)


def format_view_suffix(view_number: int | str) -> str:
    """纯数字视角编号补零到 3 位（如 1 -> 001）；字符串原样使用（如 A1）。"""
    text = str(view_number).strip()
    if not text:
        raise ValueError("视角编号不能为空")
    if text.isdigit():
        return f"{int(text):03d}"
    return text


def resolve_view_name(view_number: int) -> str:
    known = ", ".join(f"{k}->{v}" for k, v in VIEW_NAMES.items())
    if view_number not in VIEW_NAMES:
        raise ValueError(f"未知视角编号 {view_number}，可选: {known}")
    return VIEW_NAMES[view_number]


def resolve_image_name(camera_role: str, photo_number: int = 1) -> str:
    template = IMAGE_NAMES.get(camera_role)
    if template is None:
        known = ", ".join(IMAGE_NAMES)
        raise ValueError(f"未知相机角色 '{camera_role}'，可选: {known}")
    return template.format(photo_number)


def build_shot_dir(
    container_id: int,
    anomaly_type: int,
    sub_anomaly: str,
    shooting_point: str,
    view_number: int | str,
) -> Path:
    container = resolve_container(container_id)
    anomaly_folder = ANOMALY_TYPES[anomaly_type]
    view_suffix = format_view_suffix(view_number)
    point_name = shooting_point.strip("/")
    sub_name = sub_anomaly.strip()

    if not point_name or "/" in point_name:
        raise ValueError("拍摄点位应直接填写点位名，例如 ultrasonic_cleaner_slot_01")

    if point_name not in SHOOTING_POINTS:
        known = ", ".join(SHOOTING_POINTS)
        raise ValueError(
            f"清洗槽拍摄点位 '{point_name}' 不在预设列表中，可选: {known}"
        )

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
        )

    return DATASET_ROOT / container / anomaly_folder / sub_name / leaf
