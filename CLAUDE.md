# AGENTS.md — autocapture

## 项目简介

实验室容器质量检测数据集采集工具。控制 1 台 RealSense + 2 台 Orbbec 相机拍摄容器照片，按层级目录组织保存。
该项目实际部署并在实验室的ubuntu系统电脑上使用，只有在那台电脑上才能连接相机。

## 脚本一览

| 脚本 | 说明 |
|------|------|
| `capture.py` | 顺序采集，中文/混合文件名，`WARMUP_FRAMES=100` |
| `parallel_cap.py` | 并行采集，中文/混合文件名，`WARMUP_FRAMES=15` |
| `para_cap_standard.py` | 并行采集，**全英文规范命名**，`WARMUP_FRAMES=15`目前正在使用的拍摄脚本 |
| `solve_green.py` | 修复 RealSense 偏绿图片（RGB/BGR 通道顺序错误） |

## 关键约束

- **无 `requirements.txt` / `pyproject.toml`** — 手动安装依赖：
  ```
  pip install opencv-python numpy pyrealsense2 pyorbbecsdk
  ```
- **硬编码路径**：`DATASET_ROOT` 在脚本顶部，需按环境修改
- **Orbbec c1 序列号** `CL8K14100H4` 硬编码在脚本中
- **必须 2 台 Orbbec**，少一台报错退出
- **RealSense 偏绿问题**：`solve_green.py` 按视角目录批量修复（`--dry-run` 预览）
- **`venv/` 已纳入 git**，修改依赖后需提交
- **无测试**、无 lint、无 typecheck、无 CI

## 目录命名体系

同一层级存在**两套命名**，修改文件时注意对应关系：

| 文件 | 一级分类(异常) | 二级分类(小类) | 容器名 |
|------|--------------|--------------|--------|
| `capture.py` / `parallel_cap.py` | 中文 | 中英混合 | 中英混合 |
| `para_cap_standard.py` | 英文 | 英文 | 英文 |

详细映射见 `folder_name_mapping.md`。

## 采集命令

所有 6 个位置参数必须同时提供，顺序固定:

```
python capture.py <容器编号> <异常类型> <小类> <拍摄点位> <视角编号> <照片编号>
```

示例：
```
python capture.py 1 1 - mixer1 1 1                    # beaker/正常/mixer1-001/001_Color.png
python capture.py 1 3 crack magnetic_stirrer_01 1 1   # beaker/damage/crack/magnetic_stirrer_01-001/
```

`--list-cameras` 和 `--list-types` 可单独使用查看信息。

## 并行采集 (推荐)

`parallel_cap.py` / `para_cap_standard.py` 使用 `ThreadPoolExecutor(max_workers=3)` 并行采集三台相机。每台 Orbbec 使用独立 `Context()` 实例，这是线程安全的必要条件。

## 转盘控制 (ROS2)

通过 Docker 控制自动化转盘，见 `# docker容器查询.md`:

```
docker start ros2_VLA_robot
docker exec -it -u ros ros2_VLA_robot  bash
ros2 launch lab_turntable turntables.launch.py
# 通过 topic 控制转角
```

## 避坑

- 不要假定有测试/构建脚本可用
- `DATASET_ROOT` 包含空格（`empty container`），`para_cap_standard.py` 改为 `empty_container`
- 修改异常/容器分类时同步更新三个脚本中的字典
- 新增脚本请遵循现有风格（无类型标注、argparse CLI、无模块拆分）
