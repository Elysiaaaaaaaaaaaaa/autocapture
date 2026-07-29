from pathlib import Path

from dataset_base import DATASET_BASE

DATASET_ROOT = DATASET_BASE / "material"
ORBBEC_C1_SERIAL = "CL8K14100H4"
WARMUP_FRAMES = 40

USES_MATERIAL_HIERARCHY = True

MATERIAL_STATES: dict[int, str] = {
    1: "raw_material",
    2: "solution",
    3: "gel",
    4: "original_solution",
}

MATERIAL_STATES_CN: dict[int, str] = {
    1: "原材料",
    2: "溶液",
    3: "凝胶",
    4: "原液"
}

MATERIALS: dict[int, dict[int, str]] = {
    1: {
        1: "01:polyvinyl_alcohol",
        2: "02:acrylamide",
        3: "03:potassium_persulfate",
        4: "04:absolute_ethanol",
        5: "05:ethanol_95",
        6: "06:n_n_methylenebisacrylamide",
        7: "07:sodium_methanesulfonate",
        8: "08:carboxymethyl_chitosan",
        9: "09:acetate_sodium_acetate_buffer",
        10: "10:ammonium_persulfate",
        11: "11:reduced_l_glutathione",
        12: "12:phosphate_buffered_saline",
        13: "13:short_multiwalled_carbon_nanotubes",
        14: "14:water_soluble_gold_nanorods",
        15: "15:sodium_tetraborate",
        16: "16:pedot_pss",
        17: "17:dpph",
        18: "18:abts_diammonium_salt",
        19: "19:ferric_chloride",
        20: "20:dmso",
        21: "21:acrylamide+n_n_methylenebisacrylamide",
    },
    2: {
        1: "liquid1",
        2: "liquid2",
        3: "liquid3",
        4: "liquid4",
    },
    3: {
        1: "gel1",
        2: "gel2",
        3: "gel3",
    },
    4: {
        1: "01:polyvinyl_alcohol",
        2: "02:acrylamide",
        3: "03:potassium_persulfate",
        4: "04:absolute_ethanol",
        5: "05:ethanol_95",
        6: "06:n_n_methylenebisacrylamide",
        7: "07:sodium_methanesulfonate",
        8: "08:carboxymethyl_chitosan",
        9: "09:acetate_sodium_acetate_buffer",
        10: "10:ammonium_persulfate",
        11: "11:reduced_l_glutathione",
        12: "12:phosphate_buffered_saline",
        13: "13:short_multiwalled_carbon_nanotubes",
        14: "14:water_soluble_gold_nanorods",
        15: "15:sodium_tetraborate",
        16: "16:pedot_pss",
        17: "17:dpph",
        18: "18:abts_diammonium_salt",
        19: "19:ferric_chloride",
        20: "20:dmso",
        21: "21:acrylamide+n_n_methylenebisacrylamide",
    },
}

MATERIALS_CN: dict[int, dict[int, str]] = {
    1: {
        1: "聚乙烯醇",
        2: "丙烯酰胺",
        3: "过硫酸钾",
        4: "无水乙醇",
        5: "95%乙醇",
        6: "N-N‘-亚甲基双丙烯酰胺",
        7: "甲磺酸钠",
        8: "羧甲基壳聚糖",
        9: "醋酸-醋酸钠缓冲液",
        10: "过硫酸铵",
        11: "L-还原型谷胱甘肽",
        12: "PBS缓冲液",
        13: "短多壁碳纳米管",
        14: "水溶性金纳米棒",
        15: "四硼酸钠",
        16: "PEDOT:PSS",
        17: "2,2-联苯基-1-苦基肼基",
        18: "2,2-联氮双(3-乙基苯并噻唑啉-6-磺酸)二铵盐",
        19: "氯化铁",
        20: "DMSO",
        21: "丙烯酰胺+N-N‘-亚甲基双丙烯酰胺",
    },
    2: {
        1: "液体1",
        2: "液体2",
        3: "液体3",
        4: "液体4",
    },
    3: {
        1: "凝胶1",
        2: "凝胶2",
        3: "凝胶3",
    },
    4:{
        1: "聚乙烯醇",
        2: "丙烯酰胺",
        3: "过硫酸钾",
        4: "无水乙醇",
        5: "95%乙醇",
        6: "N-N‘-亚甲基双丙烯酰胺",
        7: "甲磺酸钠",
        8: "羧甲基壳聚糖",
        9: "醋酸-醋酸钠缓冲液",
        10: "过硫酸铵",
        11: "L-还原型谷胱甘肽",
        12: "PBS缓冲液",
        13: "短多壁碳纳米管",
        14: "水溶性金纳米棒",
        15: "四硼酸钠",
        16: "PEDOT:PSS",
        17: "2,2-联苯基-1-苦基肼基",
        18: "2,2-联氮双(3-乙基苯并噻唑啉-6-磺酸)二铵盐",
        19: "氯化铁",
        20: "DMSO",
        21: "丙烯酰胺+N-N‘-亚甲基双丙烯酰胺",
    },
}

ANOMALY_TYPES: dict[int, str] = {
    1: "normal",
    2: "impurity",
    3: "insufficient_quantity",
    4: "caking",
    5: "label_anomaly",
    6: "color_anomaly",
    7: "undissolved",
    8: "bubbles",
    9: "fracture",
    10: "missing_corner",
}

ANOMALY_TYPES_CN: dict[int, str] = {
    1: "正常",
    2: "杂质",
    3: "量过少",
    4: "结块",
    5: "标签异常",
    6: "颜色异常",
    7: "未溶解",
    8: "气泡",
    9: "断裂",
    10: "缺角",
}

STATE_ANOMALY_TYPES: dict[int, list[int]] = {
    1: [1, 2, 3, 4, 5, 6],
    2: [1, 2, 6, 7, 8],
    3: [1, 2, 9, 10, 8],
    4: [1, 2, 6, 7, 8]
}

CONTAINERS: dict[int, str] = {
    1: "liquid_reservoir",
    2: "soft_bottle",
    3: "beaker",
    4: "well_plate_06",
    5: "well_plate_24",
    6: "well_plate_48",
    7: "mold",
}

CONTAINERS_CN: dict[int, str] = {
    1: "储液槽",
    2: "软胶瓶",
    3: "烧杯",
    4: "6孔板",
    5: "24孔板",
    6: "48孔板",
    7: "模具"
}

SHOOTING_POINTS: dict[str, str] = {
    "magnetic_stirrer_01": "磁力搅拌器1",
    "magnetic_stirrer_02": "磁力搅拌器2",
    "beaker_sample_carousel": "烧杯样品盘",
    "plate_reservoir_sample_carousel": "孔板/储液槽样品盘",
    "mixed_sample_carousel": "混合样品盘",
    "mixed_sample_carousel_level6": "混合样品盘-level6",
    "analytical_balance": "分析天平",
    "transfer_stage": "转移台",
    "ultrasonic_cleaner_slot_01": "超声波清洗机槽1",
    "ultrasonic_cleaner_slot_02": "超声波清洗机槽2",
    "ultrasonic_cleaner_slot_03": "超声波清洗机槽3",
    "pipetting_station": "移液站",
    "mixer1": "搅拌器1",
    "mixer2": "搅拌器2",
    "zhuanyi": "转移",
    "soft_bottle_slot_01": "软胶瓶槽1",
    "soft_bottle_slot_02": "软胶瓶槽2",
    "soft_bottle_slot_03": "软胶瓶槽3",
    "soft_bottle_slot_04": "软胶瓶槽4",
    "soft_bottle_slot_05": "软胶瓶槽5",
}

SHOOTING_POINTS_CN: dict[str, str] = {v: k for k, v in SHOOTING_POINTS.items()}
SHOOTING_POINTS_CN_LIST: list[str] = list(SHOOTING_POINTS_CN.keys())

def _resolve(mapping: dict[int, str], value_id: int, label: str) -> str:
    try:
        return mapping[value_id]
    except KeyError as exc:
        known = ", ".join(str(code) for code in sorted(mapping))
        raise ValueError(f"未知{label}编号 {value_id}，可选: {known}") from exc


def get_materials(state_id: int) -> dict[int, str]:
    _resolve(MATERIAL_STATES, state_id, "材料状态")
    return MATERIALS[state_id]


def get_anomaly_types(state_id: int) -> list[int]:
    _resolve(MATERIAL_STATES, state_id, "材料状态")
    return STATE_ANOMALY_TYPES[state_id]


def get_containers(state_id: int) -> list[int]:
    _resolve(MATERIAL_STATES, state_id, "材料状态")
    return sorted(CONTAINERS)


def get_shooting_points(state_id: int, container_id: int) -> list[str]:
    _resolve(MATERIAL_STATES, state_id, "材料状态")
    _resolve(CONTAINERS, container_id, "容器")
    return list(SHOOTING_POINTS)


def format_containers() -> str:
    lines = ["容器类型（所有材料状态共用）:"]
    for code in sorted(CONTAINERS):
        lines.append(f"  {code} {CONTAINERS[code]}")
    return "\n".join(lines)


def format_anomaly_types() -> str:
    lines = ["材料状态与异常类型:"]
    for state_id in sorted(MATERIAL_STATES):
        state = MATERIAL_STATES[state_id]
        anomalies = ", ".join(
            ANOMALY_TYPES[code] for code in get_anomaly_types(state_id)
        )
        lines.append(f"  {state_id} {state}: {anomalies}")
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
    state_id: int,
    material_id: int,
    anomaly_type: int,
    container_id: int,
    shooting_point: str,
    view_number: int | str,
) -> Path:
    state = _resolve(MATERIAL_STATES, state_id, "材料状态")
    material = _resolve(get_materials(state_id), material_id, "材料")

    if anomaly_type not in get_anomaly_types(state_id):
        known = ", ".join(str(code) for code in get_anomaly_types(state_id))
        raise ValueError(f"材料状态 {state} 不支持异常类型 {anomaly_type}，可选: {known}")
    anomaly = ANOMALY_TYPES[anomaly_type]

    allowed_points = get_shooting_points(state_id, container_id)
    container = _resolve(CONTAINERS, container_id, "容器")
    point = shooting_point.strip("/")
    if not point or "/" in point or "\\" in point:
        raise ValueError("拍摄点位应直接填写点位名，例如 magnetic_stirrer_01")
    if point not in allowed_points:
        known = ", ".join(allowed_points)
        raise ValueError(f"容器 {container} 不支持拍摄点位 '{point}'，可选: {known}")

    leaf = f"{point}-{format_view_suffix(view_number)}"
    return DATASET_ROOT / state / material / anomaly / container / leaf
