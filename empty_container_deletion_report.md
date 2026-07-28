# empty_container 删除操作整理报告（修正版）

## 数据与方法（摘要）

- **保留集（chosen.csv）**：4105 张，状态均为 `visual_confirmed`。
- **原始集（raw/empty_container）**：4822 张。
- **删除判定**：`删除 = 原始集 − 保留集`。两个目录在“异常一级/二级分类”层级命名不一致（`damage/crack` vs `crack` 等），本报告先按「容器 + 点位」聚合，再对部分删除点位按「容器 + 异常类型 + 点位」精确匹配（通过子类名回构原始路径并校验存在性，匹配 4103/4105 条）。
- 本次修正：用户确认 **beaker 的整点位删除为正确删除**，**liquid_reservoir 的整点位删除为误删**；并在部分删除点位层面补充了被删的**异常类型**明细。

## 一、总体结论

- 共 **719** 张图片在 curation 中未保留（将被/已被删除）：
  - 整点位删除 **9** 个点位（共 169 张）：beaker 3 个（正确删除）、liquid_reservoir 6 个（**误删**）。
  - 部分删除 **125** 个点位，共删除 **550** 张。
- 数据异常 1 处：`multiwell_plate_96_model_01 / pipetting_station-B1` chosen 有 30 条、原始仅 28 张（2 条保留记录无对应原图），已修正计入。

## 二、各容器删除汇总

| 容器 | 原始 | 保留 | 删除 | 点位总数 | 发生删除点位数 | 整点位删除数 |
|---|---:|---:|---:|---:|---:|---:|
| beaker | 1117 | 861 | 256 | 33 | 22 | 3 |
| liquid_reservoir | 706 | 522 | 184 | 24 | 24 | 6 |
| multiwell_plate_06 | 666 | 623 | 43 | 26 | 16 | 0 |
| multiwell_plate_11 | 424 | 385 | 39 | 24 | 19 | 0 |
| multiwell_plate_24 | 640 | 560 | 80 | 24 | 23 | 0 |
| multiwell_plate_48 | 626 | 553 | 73 | 24 | 17 | 0 |
| multiwell_plate_96_model_01 | 643 | 601 | 44 | 24 | 13 | 0 |

## 三、整点位删除清单（及人工判定）

| 容器 | 点位 | 原始张数 | 判定 |
|---|---|---:|---|
| beaker | analytical_balance-003 | 45 | 正确删除 |
| beaker | mixer2-001 | 5 | 正确删除 |
| beaker | stack1-005 | 5 | 正确删除 |
| liquid_reservoir | mixed_sample_carousel-level3-2 | 21 | **误删** |
| liquid_reservoir | mixed_sample_carousel-level3-3 | 18 | **误删** |
| liquid_reservoir | mixed_sample_carousel-level5-1 | 16 | **误删** |
| liquid_reservoir | mixed_sample_carousel-level5-2 | 20 | **误删** |
| liquid_reservoir | mixed_sample_carousel-level6-1 | 19 | **误删** |
| liquid_reservoir | mixed_sample_carousel-level6-2 | 20 | **误删** |

## 四、部分删除点位：被删异常类型汇总

| 异常类型 | 删除张数 | 涉及点位数 |
|---|---:|---:|
| lid_anomaly（盖子异常） | 125 | 53 |
| stain（污渍） | 118 | 39 |
| solid_residue（固体残留） | 82 | 31 |
| damage（主体破损） | 69 | 48 |
| label_anomaly（标签异常） | 60 | 22 |
| liquid_residue（液体残留） | 60 | 25 |
| normal（正常） | 29 | 17 |
| placement_error（摆放错误） | 5 | 4 |
| foreign_object_residue（异物残留） | 2 | 2 |

> 部分删除合计 **550** 张（与按点位汇总一致）。

## 五、部分删除点位明细（被删异常类型）

按容器、删除张数降序。最后一列列出被删的异常类型及对应张数。

| 容器 | 点位 | 删除总张数 | 被删除的异常类型（张数） |
|---|---|---:|---|
| beaker | beaker_sample_carousel-004 | 18 | solid_residue（固体残留）×11、stain（污渍）×5、label_anomaly（标签异常）×2 |
| beaker | beaker_sample_carousel-005 | 18 | liquid_residue（液体残留）×5、solid_residue（固体残留）×5、stain（污渍）×5、label_anomaly（标签异常）×3 |
| beaker | beaker_sample_carousel-001 | 16 | label_anomaly（标签异常）×5、liquid_residue（液体残留）×5、stain（污渍）×5、damage（主体破损）×1 |
| beaker | beaker_sample_carousel-003 | 16 | label_anomaly（标签异常）×6、liquid_residue（液体残留）×4、stain（污渍）×4、normal（正常）×1、solid_residue（固体残留）×1 |
| beaker | beaker_sample_carousel-002 | 15 | stain（污渍）×7、solid_residue（固体残留）×5、label_anomaly（标签异常）×3 |
| beaker | transfer_stage-002 | 15 | stain（污渍）×5、label_anomaly（标签异常）×4、solid_residue（固体残留）×4、foreign_object_residue（异物残留）×1、liquid_residue（液体残留）×1 |
| beaker | analytical_balance-001 | 14 | label_anomaly（标签异常）×5、stain（污渍）×5、liquid_residue（液体残留）×4 |
| beaker | beaker_sample_carousel-006 | 14 | stain（污渍）×5、solid_residue（固体残留）×4、label_anomaly（标签异常）×3、liquid_residue（液体残留）×2 |
| beaker | mixed_sample_carousel-001 | 14 | label_anomaly（标签异常）×5、stain（污渍）×5、liquid_residue（液体残留）×4 |
| beaker | transfer_stage-001 | 12 | label_anomaly（标签异常）×5、stain（污渍）×5、damage（主体破损）×1、liquid_residue（液体残留）×1 |
| beaker | analytical_balance-002 | 10 | label_anomaly（标签异常）×5、stain（污渍）×5 |
| beaker | magnetic_stirrer_01-001 | 10 | solid_residue（固体残留）×4、stain（污渍）×2、damage（主体破损）×1、foreign_object_residue（异物残留）×1、label_anomaly（标签异常）×1、normal（正常）×1 |
| beaker | magnetic_stirrer_01-002 | 7 | stain（污渍）×6、label_anomaly（标签异常）×1 |
| beaker | mixed_sample_carousel-002 | 6 | stain（污渍）×5、label_anomaly（标签异常）×1 |
| beaker | magnetic_stirrer_02-001 | 5 | label_anomaly（标签异常）×2、stain（污渍）×2、solid_residue（固体残留）×1 |
| beaker | magnetic_stirrer_02-002 | 4 | stain（污渍）×2、label_anomaly（标签异常）×1、solid_residue（固体残留）×1 |
| beaker | stack1-006 | 4 | liquid_residue（液体残留）×4 |
| beaker | mixer2-002 | 2 | liquid_residue（液体残留）×2 |
| beaker | stack1-001 | 1 | liquid_residue（液体残留）×1 |
| liquid_reservoir | analytical_balance-001 | 11 | damage（主体破损）×4、stain（污渍）×4、liquid_residue（液体残留）×2、lid_anomaly（盖子异常）×1 |
| liquid_reservoir | magnetic_stirrer_01-001 | 7 | lid_anomaly（盖子异常）×2、liquid_residue（液体残留）×2、stain（污渍）×2、damage（主体破损）×1 |
| liquid_reservoir | magnetic_stirrer_01-002 | 6 | label_anomaly（标签异常）×2、liquid_residue（液体残留）×2、stain（污渍）×2 |
| liquid_reservoir | magnetic_stirrer_02-001 | 6 | damage（主体破损）×2、liquid_residue（液体残留）×2、stain（污渍）×2 |
| liquid_reservoir | transfer_stage-002 | 5 | damage（主体破损）×2、stain（污渍）×2、lid_anomaly（盖子异常）×1 |
| liquid_reservoir | pipetting_station-A3 | 4 | stain（污渍）×2、damage（主体破损）×1、normal（正常）×1 |
| liquid_reservoir | pipetting_station-B1 | 4 | stain（污渍）×2、damage（主体破损）×1、normal（正常）×1 |
| liquid_reservoir | analytical_balance-002 | 3 | stain（污渍）×2、damage（主体破损）×1 |
| liquid_reservoir | pipetting_station-B2 | 3 | stain（污渍）×2、damage（主体破损）×1 |
| liquid_reservoir | pipetting_station-C1 | 3 | stain（污渍）×2、damage（主体破损）×1 |
| liquid_reservoir | pipetting_station-C2 | 3 | stain（污渍）×2、damage（主体破损）×1 |
| liquid_reservoir | pipetting_station-C3 | 3 | stain（污渍）×2、damage（主体破损）×1 |
| liquid_reservoir | pipetting_station-D3 | 3 | stain（污渍）×2、lid_anomaly（盖子异常）×1 |
| liquid_reservoir | magnetic_stirrer_02-002 | 2 | stain（污渍）×2 |
| liquid_reservoir | pipetting_station-D1 | 2 | stain（污渍）×2 |
| liquid_reservoir | pipetting_station-D2 | 2 | stain（污渍）×2 |
| liquid_reservoir | transfer_stage-001 | 2 | stain（污渍）×2 |
| liquid_reservoir | pipetting_station-B3 | 1 | stain（污渍）×1 |
| multiwell_plate_06 | analytical_balance-002 | 6 | lid_anomaly（盖子异常）×2、liquid_residue（液体残留）×2、solid_residue（固体残留）×2 |
| multiwell_plate_06 | analytical_balance-001 | 5 | liquid_residue（液体残留）×2、solid_residue（固体残留）×2、lid_anomaly（盖子异常）×1 |
| multiwell_plate_06 | magnetic_stirrer_02-002 | 4 | damage（主体破损）×1、label_anomaly（标签异常）×1、lid_anomaly（盖子异常）×1、placement_error（摆放错误）×1 |
| multiwell_plate_06 | transfer_stage-001 | 4 | lid_anomaly（盖子异常）×2、liquid_residue（液体残留）×2 |
| multiwell_plate_06 | transfer_stage-002 | 4 | lid_anomaly（盖子异常）×2、liquid_residue（液体残留）×2 |
| multiwell_plate_06 | magnetic_stirrer_01-002 | 3 | lid_anomaly（盖子异常）×2、damage（主体破损）×1 |
| multiwell_plate_06 | magnetic_stirrer_02-001 | 3 | damage（主体破损）×2、label_anomaly（标签异常）×1 |
| multiwell_plate_06 | pipetting_station-C3 | 3 | lid_anomaly（盖子异常）×2、placement_error（摆放错误）×1 |
| multiwell_plate_06 | magnetic_stirrer_01-001 | 2 | damage（主体破损）×1、lid_anomaly（盖子异常）×1 |
| multiwell_plate_06 | mixed_sample_carousel-level3-3 | 2 | lid_anomaly（盖子异常）×2 |
| multiwell_plate_06 | pipetting_station-D2 | 2 | damage（主体破损）×2 |
| multiwell_plate_06 | mixed_sample_carousel-level3-2 | 1 | lid_anomaly（盖子异常）×1 |
| multiwell_plate_06 | mixed_sample_carousel-level5-1 | 1 | lid_anomaly（盖子异常）×1 |
| multiwell_plate_06 | mixed_sample_carousel-level6-1 | 1 | lid_anomaly（盖子异常）×1 |
| multiwell_plate_06 | pipetting_station-B3 | 1 | damage（主体破损）×1 |
| multiwell_plate_06 | pipetting_station-C2 | 1 | damage（主体破损）×1 |
| multiwell_plate_11 | magnetic_stirrer_02-002 | 4 | normal（正常）×2、solid_residue（固体残留）×2 |
| multiwell_plate_11 | pipetting_station-A3 | 4 | normal（正常）×2、solid_residue（固体残留）×2 |
| multiwell_plate_11 | analytical_balance-002 | 3 | solid_residue（固体残留）×2、stain（污渍）×1 |
| multiwell_plate_11 | magnetic_stirrer_01-002 | 2 | solid_residue（固体残留）×2 |
| multiwell_plate_11 | pipetting_station-B1 | 2 | normal（正常）×2 |
| multiwell_plate_11 | pipetting_station-B2 | 2 | normal（正常）×2 |
| multiwell_plate_11 | pipetting_station-B3 | 2 | normal（正常）×2 |
| multiwell_plate_11 | pipetting_station-C1 | 2 | normal（正常）×2 |
| multiwell_plate_11 | pipetting_station-C2 | 2 | normal（正常）×2 |
| multiwell_plate_11 | pipetting_station-C3 | 2 | normal（正常）×2 |
| multiwell_plate_11 | pipetting_station-D1 | 2 | normal（正常）×2 |
| multiwell_plate_11 | pipetting_station-D2 | 2 | normal（正常）×2 |
| multiwell_plate_11 | pipetting_station-D3 | 2 | normal（正常）×2 |
| multiwell_plate_11 | transfer_stage-001 | 2 | stain（污渍）×2 |
| multiwell_plate_11 | transfer_stage-002 | 2 | stain（污渍）×2 |
| multiwell_plate_11 | magnetic_stirrer_01-001 | 1 | stain（污渍）×1 |
| multiwell_plate_11 | mixed_sample_carousel-level5-2 | 1 | lid_anomaly（盖子异常）×1 |
| multiwell_plate_11 | mixed_sample_carousel-level6-1 | 1 | solid_residue（固体残留）×1 |
| multiwell_plate_11 | mixed_sample_carousel-level6-2 | 1 | solid_residue（固体残留）×1 |
| multiwell_plate_24 | pipetting_station-C3 | 15 | lid_anomaly（盖子异常）×9、damage（主体破损）×2、label_anomaly（标签异常）×2、normal（正常）×2 |
| multiwell_plate_24 | magnetic_stirrer_02-002 | 10 | solid_residue（固体残留）×4、damage（主体破损）×3、lid_anomaly（盖子异常）×1、normal（正常）×1、placement_error（摆放错误）×1 |
| multiwell_plate_24 | analytical_balance-002 | 9 | solid_residue（固体残留）×6、liquid_residue（液体残留）×2、damage（主体破损）×1 |
| multiwell_plate_24 | analytical_balance-001 | 5 | liquid_residue（液体残留）×2、solid_residue（固体残留）×2、lid_anomaly（盖子异常）×1 |
| multiwell_plate_24 | magnetic_stirrer_01-001 | 5 | lid_anomaly（盖子异常）×2、liquid_residue（液体残留）×2、damage（主体破损）×1 |
| multiwell_plate_24 | magnetic_stirrer_02-001 | 4 | damage（主体破损）×2、solid_residue（固体残留）×2 |
| multiwell_plate_24 | transfer_stage-002 | 4 | damage（主体破损）×2、liquid_residue（液体残留）×2 |
| multiwell_plate_24 | magnetic_stirrer_01-002 | 3 | solid_residue（固体残留）×2、lid_anomaly（盖子异常）×1 |
| multiwell_plate_24 | pipetting_station-D2 | 3 | damage（主体破损）×2、label_anomaly（标签异常）×1 |
| multiwell_plate_24 | mixed_sample_carousel-level3-2 | 2 | lid_anomaly（盖子异常）×2 |
| multiwell_plate_24 | mixed_sample_carousel-level3-3 | 2 | lid_anomaly（盖子异常）×1、solid_residue（固体残留）×1 |
| multiwell_plate_24 | mixed_sample_carousel-level5-1 | 2 | lid_anomaly（盖子异常）×2 |
| multiwell_plate_24 | mixed_sample_carousel-level5-2 | 2 | lid_anomaly（盖子异常）×2 |
| multiwell_plate_24 | mixed_sample_carousel-level6-1 | 2 | lid_anomaly（盖子异常）×2 |
| multiwell_plate_24 | pipetting_station-A3 | 2 | damage（主体破损）×2 |
| multiwell_plate_24 | pipetting_station-C2 | 2 | damage（主体破损）×2 |
| multiwell_plate_24 | transfer_stage-001 | 2 | liquid_residue（液体残留）×2 |
| multiwell_plate_24 | mixed_sample_carousel-level6-2 | 1 | label_anomaly（标签异常）×1 |
| multiwell_plate_24 | pipetting_station-B1 | 1 | damage（主体破损）×1 |
| multiwell_plate_24 | pipetting_station-B2 | 1 | damage（主体破损）×1 |
| multiwell_plate_24 | pipetting_station-B3 | 1 | damage（主体破损）×1 |
| multiwell_plate_24 | pipetting_station-C1 | 1 | damage（主体破损）×1 |
| multiwell_plate_24 | pipetting_station-D3 | 1 | damage（主体破损）×1 |
| multiwell_plate_48 | analytical_balance-001 | 12 | lid_anomaly（盖子异常）×9、solid_residue（固体残留）×2、liquid_residue（液体残留）×1 |
| multiwell_plate_48 | analytical_balance-002 | 8 | lid_anomaly（盖子异常）×6、solid_residue（固体残留）×2 |
| multiwell_plate_48 | magnetic_stirrer_01-001 | 7 | lid_anomaly（盖子异常）×4、solid_residue（固体残留）×3 |
| multiwell_plate_48 | transfer_stage-002 | 7 | lid_anomaly（盖子异常）×5、damage（主体破损）×2 |
| multiwell_plate_48 | transfer_stage-001 | 6 | lid_anomaly（盖子异常）×5、solid_residue（固体残留）×1 |
| multiwell_plate_48 | magnetic_stirrer_02-001 | 5 | damage（主体破损）×2、lid_anomaly（盖子异常）×2、solid_residue（固体残留）×1 |
| multiwell_plate_48 | magnetic_stirrer_02-002 | 5 | solid_residue（固体残留）×3、placement_error（摆放错误）×2 |
| multiwell_plate_48 | magnetic_stirrer_01-002 | 4 | lid_anomaly（盖子异常）×2、solid_residue（固体残留）×2 |
| multiwell_plate_48 | pipetting_station-C3 | 4 | lid_anomaly（盖子异常）×3、damage（主体破损）×1 |
| multiwell_plate_48 | pipetting_station-D1 | 4 | damage（主体破损）×2、lid_anomaly（盖子异常）×2 |
| multiwell_plate_48 | mixed_sample_carousel-level5-2 | 2 | lid_anomaly（盖子异常）×2 |
| multiwell_plate_48 | mixed_sample_carousel-level6-1 | 2 | lid_anomaly（盖子异常）×2 |
| multiwell_plate_48 | pipetting_station-A3 | 2 | damage（主体破损）×1、solid_residue（固体残留）×1 |
| multiwell_plate_48 | pipetting_station-D2 | 2 | damage（主体破损）×2 |
| multiwell_plate_48 | mixed_sample_carousel-level3-2 | 1 | lid_anomaly（盖子异常）×1 |
| multiwell_plate_48 | mixed_sample_carousel-level5-1 | 1 | lid_anomaly（盖子异常）×1 |
| multiwell_plate_48 | pipetting_station-C2 | 1 | damage（主体破损）×1 |
| multiwell_plate_96_model_01 | magnetic_stirrer_01-002 | 6 | lid_anomaly（盖子异常）×4、damage（主体破损）×2 |
| multiwell_plate_96_model_01 | transfer_stage-001 | 6 | lid_anomaly（盖子异常）×4、damage（主体破损）×2 |
| multiwell_plate_96_model_01 | magnetic_stirrer_02-001 | 5 | lid_anomaly（盖子异常）×4、damage（主体破损）×1 |
| multiwell_plate_96_model_01 | magnetic_stirrer_02-002 | 5 | lid_anomaly（盖子异常）×3、stain（污渍）×2 |
| multiwell_plate_96_model_01 | pipetting_station-C3 | 4 | lid_anomaly（盖子异常）×4 |
| multiwell_plate_96_model_01 | analytical_balance-002 | 3 | lid_anomaly（盖子异常）×2、damage（主体破损）×1 |
| multiwell_plate_96_model_01 | magnetic_stirrer_01-001 | 3 | lid_anomaly（盖子异常）×2、damage（主体破损）×1 |
| multiwell_plate_96_model_01 | pipetting_station-D1 | 3 | lid_anomaly（盖子异常）×3 |
| multiwell_plate_96_model_01 | transfer_stage-002 | 3 | lid_anomaly（盖子异常）×2、damage（主体破损）×1 |
| multiwell_plate_96_model_01 | mixed_sample_carousel-level6-1 | 2 | lid_anomaly（盖子异常）×2 |
| multiwell_plate_96_model_01 | pipetting_station-C1 | 2 | lid_anomaly（盖子异常）×2 |
| multiwell_plate_96_model_01 | mixed_sample_carousel-level6-2 | 1 | lid_anomaly（盖子异常）×1 |
| multiwell_plate_96_model_01 | pipetting_station-C2 | 1 | lid_anomaly（盖子异常）×1 |

---
*本报告由 chosen.csv 与 raw/empty_container 对比自动生成，不含任何文件系统路径。*