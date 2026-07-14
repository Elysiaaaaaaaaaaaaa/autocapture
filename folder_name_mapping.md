# 实验室容器与仪器异常数据集：文件夹名称映射清单

本清单用于将当前目录中的中英文混合命名，统一为适合实验室数据管理、论文描述和模型训练的机器可读英文名称。

约定：

- 使用小写英文、数字和下划线；不使用空格、拼音或拼写错误。
- 保持原有目录层级不变，只修改同一层目录的名称。
- 场景目录统一采用 `{object_type}_{scene_type}-{angle_id}`，例如 `beaker_sample_carousel-001`。
- `001`、`002` 等表示该场景下的拍摄角度编号，不表示新的样本层级。
- `tianping` 与 `tianping1` 统一表示同一台分析天平，不区分设备。
- `stack1/2/3` 表示同一台可编程旋转样品转盘的装载配置，不表示容器堆叠状态。
- 当前目录实际检出 `stack1` 和 `stack3`；`stack2` 按已确认的实验语义保留映射。
- 本文件只提供映射，不自动修改现有数据目录。

## 1. 根目录

| 当前名称 | 规范名称 | 备注 |
|---|---|---|
| `empty container` | `empty_container` | 建议作为规范化副本的根目录；原始目录可保留为 `raw_original/empty container` |
| `结构示意.txt` | `structure_readme.txt` | 结构说明文件 |

## 2. 容器、器皿与仪器名称

| 当前名称 | 规范名称 | 类别 |
|---|---|---|
| `6-well plate` | `multiwell_plate_06` | 多孔板 |
| `11-well plate` | `multiwell_plate_11` | 多孔板；保留实际孔数 |
| `24-well plate` | `multiwell_plate_24` | 多孔板 |
| `48-well plate` | `multiwell_plate_48` | 多孔板 |
| `96-well plate modle1` | `multiwell_plate_96_model_01` | 修正 `modle` 拼写 |
| `96-well plate modle 2` | `multiwell_plate_96_model_02` | 修正 `modle` 拼写 |
| `test tube` | `test_tube_model_01` | 若不存在型号差异，可简化为 `test_tube` |
| `test tube modle2` | `test_tube_model_02` | 修正 `modle` 拼写 |
| `beaker` | `beaker` | 烧杯 |
| `glass rod` | `glass_stirring_rod` | 若确实用于搅拌；否则使用 `glass_rod` |
| `rewservoir` | `liquid_reservoir` | 修正拼写；若该槽专门用于移液取液，可进一步改为 `reagent_reservoir` |
| `magnetic mixer 1` | `magnetic_stirrer_01` | 磁力搅拌器 1 |
| `magnetic mixer 2` | `magnetic_stirrer_02` | 磁力搅拌器 2 |

## 3. 异常一级分类

| 当前名称 | 规范名称 |
|---|---|
| `正常` | `normal` |
| `主体破损` | `damage` |
| `破损` | `damage` |
| `盖子异常` | `lid_anomaly` |
| `固体残留` | `solid_residue` |
| `液体残留` | `liquid_residue` |
| `污渍` | `stain` |
| `标签异常` | `label_anomaly` |
| `摆放错误` | `placement_error` |

## 4. 异常二级分类

| 当前名称 | 规范名称 |
|---|---|
| `裂痕` | `crack` |
| `scratch` | `scratch` |
| `wear` | `wear` |
| `damaged` | `crack` |
| `盖子盖错` | `incorrect_lid` |
| `盖子裂痕` | `cracked_lid` |
| `没有盖子` | `missing_lid` |
| `粉末` | `powder` |
| `crystal` | `crystalline_residue` |
| `bottom-powder` | `bottom_powder_residue` |
| `wall-powder` | `wall_powder_residue` |
| `solid residue` | `solid_residue` |
| `liquid residue` | `liquid_residue` |
| `无色液体` | `colorless_liquid` |
| `带颜色透明液体` | `colored_clear_liquid` |
| `color` | `colored_liquid` |
| `non-color` | `colorless_liquid` |
| `颜料污渍` | `pigment_stain` |
| `color dirt` | `pigment_stain` |
| `water dirt` | `water_stain` |
| `斜放` | `tilted_placement` |
| `标签脱落` | `label_detachment` |
| `标签污染` | `label_contamination` |
| `标签脏污` | `label_soiling` |
| `object residue` | `foreign_object_residue` |
| `tag` | `label_anomaly` |

以下名称的具体语义仅凭文件夹名不能完全确定，建议在正式改名之前根据图像确认：

| 当前名称 | 暂定规范名称 | 需要确认 |
|---|---|---|
| `fall` | `label_detachment` | 是标签脱落、容器跌落，还是其他现象 |
| `dip` | `dip` | 是浸入、倾斜，还是液体浸润 |
| `dirty` | `label_soiling` | 是一般脏污、外壁污渍，还是污染物残留 |

## 5. 拍摄场景与承载设备

| 当前名称/模式 | 规范名称 | 说明 |
|---|---|---|
| `tianping-001` | `analytical_balance-001` | 分析天平第 1 个拍摄角度 |
| `tianping-002` | `analytical_balance-002` | 分析天平第 2 个拍摄角度 |
| `tianping-003` | `analytical_balance-003` | 分析天平第 3 个拍摄角度 |
| `tianping1-001` | `analytical_balance-001` | `tianping1` 不作为另一台设备 |
| `tianping1-002` | `analytical_balance-002` | `tianping1` 不作为另一台设备 |
| `zhuanyi-001` | `transfer_stage-001` | 转移台第 1 个拍摄角度 |
| `zhuanyi-002` | `transfer_stage-002` | 转移台第 2 个拍摄角度 |
| `mixer1-001` | `magnetic_stirrer_01-001` | 磁力搅拌器 1 的第 1 个拍摄角度 |
| `mixer1-002` | `magnetic_stirrer_01-002` | 磁力搅拌器 1 的第 2 个拍摄角度 |
| `mixer2-001` | `magnetic_stirrer_02-001` | 磁力搅拌器 2 的第 1 个拍摄角度 |
| `mixer2-002` | `magnetic_stirrer_02-002` | 磁力搅拌器 2 的第 2 个拍摄角度 |
| `mixer2-003` | `magnetic_stirrer_02-003` | 磁力搅拌器 2 的第 3 个拍摄角度 |
| `stack1-001` | `beaker_sample_carousel-001` | 烧杯样品转盘第 1 个拍摄角度 |
| `stack1-002` | `beaker_sample_carousel-002` | 烧杯样品转盘第 2 个拍摄角度 |
| `stack1-###` | `beaker_sample_carousel-###` | 样品转盘：纯烧杯配置 |
| `stack2-###` | `plate_reservoir_sample_carousel-###` | 样品转盘：孔板/储液槽配置 |
| `stack3-001` | `mixed_sample_carousel-001` | 混合样品转盘第 1 个拍摄角度 |
| `stack3-002` | `mixed_sample_carousel-002` | 混合样品转盘第 2 个拍摄角度 |
| `stack3-###` | `mixed_sample_carousel-###` | 样品转盘：混合配置 |

`sample_carousel` 表示可旋转、具有固定槽位并可由程序控制的样品转盘；配置通过场景目录前缀体现，不新增目录层级。

## 6. 视角与图像文件名

| 当前名称 | 规范名称 |
|---|---|
| `top1` | `view_top_01` |
| `top2` | `view_top_02` |
| `top3` | `view_top_03` |
| `top4` | `view_top_04` |
| `top5` | `view_top_05` |
| `top6` | `view_top_06` |
| `top7` | `view_top_07` |
| `top1-5` | `overview_top_01_05` | 当前图片呈现为全局俯视概览 |
| `top6-10` | `overview_top_06_10` | 当前图片呈现为全局俯视概览 |
| `001_Color.png`–`010_Color.png` | `view_001_rgb.png`–`view_010_rgb.png` |
| `c1_Color.png` | `camera_01_rgb.png` |
| `c2_Color.png` | `camera_02_rgb.png` |
| `备注.txt` | `notes.txt` |

## 7. 推荐的规范化目录示例

```text
laboratory_labware_anomaly_dataset/
└── beaker/
    └── residue/
        └── powder_residue/
            └── beaker_sample_carousel-001/
                └── view_top_01/
                    ├── camera_01_rgb.png
                    └── camera_02_rgb.png
```

规范化后仍保持原有层级。例如：

```text
beaker/
└── normal/
    └── beaker_sample_carousel-001/
        └── view_top_01/
```

不要额外添加 `none`、`capture_001` 或 `sample_carousel/beaker_only` 等目录层级。

## 8. 重命名前的保留规则

1. 先保留原目录作为 `raw_original`，不要直接覆盖。
2. 只替换同一层目录名称，不改变目录层级和图像所在层级。
3. `tianping-###` 与 `tianping1-###` 统一为 `analytical_balance-###` 时，先检查同编号图像是否确实为同一拍摄角度。
4. `fall`、`dip`、`dirty` 等语义不明确的目录先不要自动改名。
5. `magnetic mixer 1/2` 与 `mixer1/mixer2` 应通过名称映射关联到同一设备体系，不新增仪器层级。

## 9. 图片实物核查结果

以下结论来自对当前目录代表性图片的视觉检查，不替代实验人员对具体样本的最终标注。场景目录按照 `{object_type}_{scene_type}-{angle_id}` 保持单层命名。

| 检查对象 | 图片观察 | 命名结论 |
|---|---|---|
| `6-well plate` | 可见 2×3 共 6 个孔 | 名称匹配，建议使用 `multiwell_plate_06` |
| `11-well plate` | 可见 4+3+4 共 11 个孔 | 名称匹配，建议使用 `multiwell_plate_11` |
| `24-well plate` | 可见 24 个孔的矩阵结构 | 名称匹配，建议使用 `multiwell_plate_24` |
| `48-well plate` | 可见 48 个孔的矩阵结构 | 名称匹配，建议使用 `multiwell_plate_48` |
| `beaker` | 透明带嘴烧杯，部分图片中含玻璃棒 | `beaker` 正确；`glass rod` 可改为 `glass_stirring_rod` |
| `rewservoir` | 可见矩形塑料储液/承载槽 | `reservoir` 语义基本正确；功能未确认前优先使用 `liquid_reservoir` |
| `mixer1-###` | 可见带金属加热/搅拌面的磁力搅拌器 | 建议使用 `magnetic_stirrer_01` |
| `mixer2-###` | 可见第二个磁力搅拌器位置 | 建议使用 `magnetic_stirrer_02` |
| `stack1-###` | 可见旋转圆盘及多个烧杯槽位 | 应命名为 `sample_carousel/beaker_only` |
| `stack3-###` | 可见同一类旋转圆盘及混合槽位 | 应命名为 `sample_carousel/mixed` |
| `top1-5`、`top6-10` | 图片是实验台全局俯视图，而不是单个局部视角 | 建议使用 `overview_top_01_05`、`overview_top_06_10` |
| `tianping*` | 图片中主要显示样品承载位置，未清楚显示天平显示屏或防风罩 | 根据实验记录可使用 `analytical_balance`，但仅凭图片无法独立确认 |
| `zhuanyi*` | 图片中显示样品位/承载平台，具体机械功能不完全可见 | 根据实验记录可使用 `transfer_stage`，图片本身只能作场景佐证 |

当前工作区中 `96-well plate modle1/2`、`test tube`、`test tube modle2`、`magnetic mixer 1/2` 顶层目录未检出图像文件，因此这些名称暂不能通过当前图片独立核验；它们仍按已确认的实验语义保留映射。
