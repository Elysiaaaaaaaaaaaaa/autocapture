from pathlib import Path

DATASET_ROOT = Path("/home/qy/dataset-202607/quality test/empty_container")
ORBBEC_C1_SERIAL = "CL8K14100H4"
WARMUP_FRAMES = 40

ANOMALY_TYPES: dict[int, str] = {
    1: "normal",
    2: "stain",
    3: "damage",
    4: "liquid_residue",
    5: "solid_residue",
    6: "lid_anomaly",
    7: "label_anomaly",
    8: "placement_error",
}

ANOMALY_SUBCATEGORIES: dict[int, list[str]] = {
    1: [],
    2: ["water_stain", "pigment_stain"],
    3: ["scratch", "crack"],
    4: ["colorless_liquid", "colored_clear_liquid", "turbid_liquid", "wall_liquid_residue"],
    5: ["powder", "crystalline_residue"],
    6: ["cracked_lid", "incorrect_lid", "missing_lid"],
    7: ["label_soiling", "label_detachment", "label_damage"],
    8: ["tilted_placement"],
}

NO_SUBCATEGORY = "-"

CONTAINERS: dict[int, str] = {
    1: "beaker",
    2: "test_tube_model_01",
    3: "test_tube_model_02",
    4: "multiwell_plate_06",
    5: "multiwell_plate_11",
    6: "multiwell_plate_24",
    7: "multiwell_plate_48",
    8: "multiwell_plate_96_model_01",
    9: "multiwell_plate_96_model_02",
    10: "magnetic_stirrer_01",
    11: "magnetic_stirrer_02",
    12: "liquid_reservoir",
    13: "ultrasonic_cleaner",
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


def format_view_suffix(view_number: int | str) -> str:
    """纯数字视角编号补零到 3 位（如 1 -> 001）；字符串原样使用（如 A1）。"""
    text = str(view_number).strip()
    if not text:
        raise ValueError("视角编号不能为空")
    if text.isdigit():
        return f"{int(text):03d}"
    return text


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
        raise ValueError("拍摄点位应直接填写点位名，例如 magnetic_stirrer_01")

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
