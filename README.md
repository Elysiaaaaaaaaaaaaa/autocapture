# autocapture

实验室容器质量检测数据集采集工具。控制 1 台 RealSense + 2 台 Orbbec 相机拍摄容器照片，按层级目录组织保存。

## 文件结构

| 文件 | 作用 |
|------|------|
| `para_cap_standard.py` | **当前主力脚本**，并行采集，英文命名 |
| `capture_base.py` | 通用拍摄引擎，含 `--dry-run` |
| `path_config_standard.py` | 英文规范路径配置模块 |
| `capture.py` | 旧版顺序采集（中文/混合命名） |
| `parallel_cap.py` | 旧版并行采集（中文/混合命名） |
| `solve_green.py` | 修复 RealSense 偏绿图片 |

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

## 配置切换

`capture_base.py` 顶部 `from path_config_standard import *` 决定使用哪套命名规范。如需改用中文命名体系，将这一行替换为对应的配置模块即可（如 `path_config_chinese.py`，需自行创建，内容参照 `capture.py` 中的字典）。

## 依赖

```bash
pip install opencv-python numpy pyrealsense2 pyorbbecsdk
```

所有脚本为单文件无模块拆分风格，无 `requirements.txt`。`DATASET_ROOT`、`ORBBEC_C1_SERIAL`、分类字典均在配置模块顶部硬编码，按需修改。
