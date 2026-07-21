# autocapture

实验室容器质量检测数据集采集工具。控制 1 台 RealSense + 2 台 Orbbec 相机拍摄容器照片，按层级目录组织保存。

## 文件结构

| 文件 | 作用 |
|------|------|
| `para_cap_standard.py` | **当前主力脚本**，并行采集，英文命名 |
| `capture_base.py` | 通用拍摄引擎，含 `--dry-run` |
| `path_config_standard.py` | 英文规范路径配置模块 |
| `path_config_material.py` | 材料数据的三状态分层路径配置 |
| `capture.py` | 旧版顺序采集（中文/混合命名） |
| `parallel_cap.py` | 旧版并行采集（中文/混合命名） |
| `solve_green.py` | 修复 RealSense 偏绿图片 |
| `generate_dataset_table.mjs` | 扫描数据集并生成 Excel 统计表 |

## 快速使用

```bash
# 查看帮助
python para_cap_standard.py --help

# 查看容器/异常类型编号
python para_cap_standard.py --list-types

# 采集：容器1(beaker) 异常1(normal) 点位magnetic_stirrer_01 视角1 第1张
python para_cap_standard.py 1 1 - magnetic_stirrer_01 1 1

# 采集：容器1 异常3(damage) 小类crack 点位magnetic_stirrer_01 视角1 第1张
python para_cap_standard.py 1 3 crack magnetic_stirrer_01 1 1
```

6 个位置参数顺序固定：容器编号 → 异常类型 → 小类 → 拍摄点位 → 视角编号 → 照片编号。正常类小类填 `-`。

## 路径验证（新功能）

```bash
python para_cap_standard.py 1 1 - magnetic_stirrer_01 1 1 --dry-run
```

`--dry-run` 跳过相机连接，在目标路径生成带文件名水印的灰色占位图，用于确认目录结构是否正确。

## 预览 GUI

实时预览三台相机画面并直接拍摄，无需反复启停 pipeline：

```bash
# 从项目根目录启动（两种方式等价）
python -m preview_mode.preview_gui
python preview_mode/preview_gui.py
```

预览 GUI 默认使用 `path_config_material.py`，图片保存到
`/home/qy/dataset-202607/quality test/material`。打开后依次选择材料状态、具体材料、
异常类型、容器种类、拍摄点位和视角。材料异常不设小类目录，路径示例：

```text
material/raw_material_powder/polyvinyl_alcohol/caking/soft_bottle/soft_bottle_slot-001/
material/intermediate_solution/liquid1/color_anomaly/liquid_reservoir/magnetic_stirrer_01-001/
material/finished_gel/gel1/uncured/liquid_reservoir/transfer_stage-001/
```

原材料粉末可使用储液槽或软胶瓶，软胶瓶保留标准点位并新增 `soft_bottle_slot`；
中间溶液和成品凝胶暂时只使用储液槽。

如需继续采集空容器数据，可显式指定原配置：

```bash
python -m preview_mode.preview_gui --config path_config_standard
```

## 配置切换

`capture_base.py` 顶部 `from path_config_standard import *` 决定使用哪套命名规范。如需改用中文命名体系，将这一行替换为对应的配置模块即可（如 `path_config_chinese.py`，需自行创建，内容参照 `capture.py` 中的字典）。

## 依赖

```bash
pip install opencv-python numpy pyrealsense2 pyorbbecsdk
```

所有脚本为单文件无模块拆分风格，无 `requirements.txt`。`DATASET_ROOT`、`ORBBEC_C1_SERIAL`、分类字典均在配置模块顶部硬编码，按需修改。

## 生成数据集统计表

脚本会递归统计常见图片格式，并生成“数据总览”和“视角明细”两个工作表。`top1`、`top2`、`view_top_1` 等俯视子目录中的图片会排除，不计入所属“点位-视角”的统计。

```bash
# 使用默认数据集目录和输出目录
node generate_dataset_table.mjs

# 指定数据集与输出文件
node generate_dataset_table.mjs \
  --input "/home/qy/dataset-202607/quality test/empty_container" \
  --output "/home/qy/dataset-202607/empty_container_数据集统计表.xlsx"
```

运行环境需提供 Node.js 和 `@oai/artifact-tool`。也可通过 `DATASET_ROOT` 环境变量设置默认数据集目录；完整选项见 `node generate_dataset_table.mjs --help`。
