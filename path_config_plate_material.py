"""孔板材料采集路径配置。

目录层级（无异常类型层，异常写在每孔 txt 标注中）::

    <DATASET_ROOT>/<state>/<material>/<container>/<point>-<view>/

与 ``path_config_material`` 的区别：
- 仅包含孔板容器（6 / 24 / 48）
- 材料名下直接到容器类型 → 拍摄点位
- 异常类型供 GUI 按孔标注，含 ``blank``（空白）
"""

from pathlib import Path

from dataset_base import DATASET_BASE

DATASET_ROOT = DATASET_BASE / "material"
ORBBEC_C1_SERIAL = "CL8K14100H4"
WARMUP_FRAMES = 40

USES_MATERIAL_HIERARCHY = True
USES_PLATE_WELL_ANNOTATION = True

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
    4: "原液",
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
    4: {
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

# 0 = blank（空白孔）；其余与 path_config_material 一致
ANOMALY_TYPES: dict[int, str] = {
    0: "blank",
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
    11: "explosion",
}

ANOMALY_TYPES_CN: dict[int, str] = {
    0: "空白",
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
    11: "爆炸",
}

# 各材料状态下可选的孔位异常（始终含 blank=0）
STATE_ANOMALY_TYPES: dict[int, list[int]] = {
    1: [0, 1, 2, 3, 4, 5, 6],
    2: [0, 1, 2, 6, 7, 8],
    3: [0, 1, 2, 9, 10, 8,11,7],
    4: [0, 1, 2, 6, 7, 8],
}

BLANK_ANOMALY_ID = 0

CONTAINERS: dict[int, str] = {
    1: "well_plate_06",
    2: "well_plate_11",
    3: "well_plate_24",
    4: "well_plate_48",
    5: "mold",
    6: "well_plate_96"
}

CONTAINERS_CN: dict[int, str] = {
    1: "6孔板",
    2: "11孔板",
    3: "24孔板",
    4: "48孔板",
    5: "模具",
    6: "96孔板",
}

# naming:
#   "numeric" — 孔位 1..N（6/11孔板、模具）
#   "alpha"   — 标准 A1、A2…（24/48孔板）
PLATE_SPECS: dict[str, dict] = {
    "well_plate_06": {
        "naming": "numeric",
        "count": 6,
        "display_rows": [3, 3],  # 2×3
    },
    "well_plate_11": {
        "naming": "numeric",
        "count": 11,
        "display_rows": [4, 3, 4],  # 4+3+4
    },
    "well_plate_24": {
        "naming": "alpha",
        "layout": (4, 6),
    },
    "well_plate_48": {
        "naming": "alpha",
        "layout": (6, 8),
    },
    "mold": {
        "naming": "numeric",
        "count": 5,
        "display_rows": [5],  # 1×5
    },
    "well_plate_96": {
        "naming": "alpha",
        "layout": (8, 12),
    },
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
    "shaker": "摇床",
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


def get_plate_spec(container_id: int) -> dict:
    container = _resolve(CONTAINERS, container_id, "容器")
    try:
        return PLATE_SPECS[container]
    except KeyError as exc:
        raise ValueError(f"容器 {container} 无孔板布局定义") from exc


def get_plate_layout(container_id: int) -> tuple[int, int]:
    """返回显示用 (rows, cols)。numeric 孔板取 display_rows 的最大列数。"""
    spec = get_plate_spec(container_id)
    if spec["naming"] == "alpha":
        return spec["layout"]
    row_lens = spec["display_rows"]
    return len(row_lens), max(row_lens)


def well_ids_for_container(container_id: int) -> list[str]:
    """按顺序返回孔位 ID。

    - 6/11 孔板、模具：``['1','2',...,'N']``
    - 24/48 孔板：``['A1','A2',...,]`` 行优先
    """
    spec = get_plate_spec(container_id)
    if spec["naming"] == "numeric":
        return [str(i) for i in range(1, spec["count"] + 1)]

    rows, cols = spec["layout"]
    wells = []
    for r in range(rows):
        row_letter = chr(ord("A") + r)
        for c in range(1, cols + 1):
            wells.append(f"{row_letter}{c}")
    return wells


def well_grid_cells(container_id: int) -> list[tuple[str, int, int]]:
    """返回 ``(well_id, grid_row, grid_col)``，供 GUI 排布（0-based）。"""
    spec = get_plate_spec(container_id)
    cells: list[tuple[str, int, int]] = []

    if spec["naming"] == "numeric":
        well_ids = well_ids_for_container(container_id)
        idx = 0
        for r, n_cols in enumerate(spec["display_rows"]):
            # 较短行居中（如 11 孔板中间 3 孔）
            max_cols = max(spec["display_rows"])
            offset = (max_cols - n_cols + 1) // 2
            for c in range(n_cols):
                cells.append((well_ids[idx], r, offset + c))
                idx += 1
        return cells

    rows, cols = spec["layout"]
    for r in range(rows):
        row_letter = chr(ord("A") + r)
        for c in range(cols):
            cells.append((f"{row_letter}{c + 1}", r, c))
    return cells


def format_view_suffix(view_number: int | str) -> str:
    text = str(view_number).strip()
    if not text:
        raise ValueError("视角编号不能为空")
    if text.isdigit():
        return f"{int(text):03d}"
    return text


def build_shot_dir(
    state_id: int,
    material_id: int,
    container_id: int,
    shooting_point: str,
    view_number: int | str,
) -> Path:
    """材料名下直接到容器类型 / 拍摄点位（无异常类型目录）。"""
    state = _resolve(MATERIAL_STATES, state_id, "材料状态")
    material = _resolve(get_materials(state_id), material_id, "材料")
    container = _resolve(CONTAINERS, container_id, "容器")

    allowed_points = get_shooting_points(state_id, container_id)
    point = shooting_point.strip("/")
    if not point or "/" in point or "\\" in point:
        raise ValueError("拍摄点位应直接填写点位名，例如 plate_reservoir_sample_carousel")
    if point not in allowed_points:
        known = ", ".join(allowed_points)
        raise ValueError(f"容器 {container} 不支持拍摄点位 '{point}'，可选: {known}")

    leaf = f"{point}-{format_view_suffix(view_number)}"
    return DATASET_ROOT / state / material / container / leaf


def format_well_annotation(well_anomalies: dict[str, str]) -> str:
    """生成与图片同名的 txt 内容（每行 ``孔位: 异常英文名``）。"""
    lines = [f"{well}: {anomaly}" for well, anomaly in well_anomalies.items()]
    return "\n".join(lines) + "\n"


def annotation_path_for_image(image_path: Path) -> Path:
    """``001_Color.png`` → ``001_Color.txt``（同目录）。"""
    return image_path.with_suffix(".txt")
