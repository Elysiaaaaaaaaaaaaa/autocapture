# empty_container 数据集统计报告

> **数据集路径:** `D:\myproject\2026.7research\dataset\empty_container`
>
> **层级:** 目标种类 → 异常大类 → 异常小类 → 点位 → 视角/形态
>
> **viewRULE.txt 规则:** 文件夹命名 = `点位-视角编号`，每个视角文件夹内的图片数 = shape数量，
> 某个点位的小计 = 视角数 × 平均shape数

---

## 📊 总览

| 指标 | 数值 |
|---|---|
| 目标种类（容器类型） | **7** |
| 去重点位 | **16** |
| 视角总数 | **1368** |
| 图片总数 | **4103** |

## 📦 各容器汇总

| 容器 | 点位 | 视角 | 图片 | 异常大类数 |
|---|---|---|---|---|
| **beaker (烧杯)** | 12 | 145 | 861 | 7 |
| **liquid_reservoir (贮液器)** | 5 | 181 | 522 | 8 |
| **multiwell_plate_06 (6孔板)** | 10 | 227 | 623 | 8 |
| **multiwell_plate_11 (11孔板)** | 8 | 145 | 385 | 7 |
| **multiwell_plate_24 (24孔板)** | 8 | 210 | 560 | 8 |
| **multiwell_plate_48 (48孔板)** | 8 | 219 | 553 | 8 |
| **multiwell_plate_96_model_01 (96孔板模型1)** | 8 | 241 | 599 | 8 |

## 🗺️ 全部点位列表

共 **16** 个去重点位：

 1. `analytical_balance`
 2. `beaker_sample_carousel`
 3. `magnetic_stirrer_01`
 4. `magnetic_stirrer_02`
 5. `mixed_sample_carousel`
 6. `mixed_sample_carousel-level3`
 7. `mixed_sample_carousel-level5`
 8. `mixed_sample_carousel-level6`
 9. `mixer1`
10. `mixer2`
11. `pipetting_station`
12. `stack1`
13. `stack3`
14. `tianping`
15. `transfer_stage`
16. `zhuanyi`

## 📋 异常大类 × 容器 覆盖矩阵（图片数）

| 异常大类 | beaker | liquid_reser | multiwell_pl | multiwell_pl | multiwell_pl | multiwell_pl | multiwell_pl |
|---|---|---|---|---|---|---|---|
| **主体破损 (Damage)** | 144 | 97 | 135 | - | 87 | 82 | 64 |
| **异物残留 (Foreign Object Residue)** | 72 | - | - | - | - | - | - |
| **标签异常 (Label Anomaly)** | 72 | 67 | 81 | 82 | 76 | 79 | 122 |
| **盖子异常 (Lid Anomaly)** | - | 128 | 146 | 79 | 155 | 145 | 150 |
| **液体残留 (Liquid Residue)** | 108 | 32 | 38 | 45 | 36 | 44 | 42 |
| **正常 (Normal)** | 70 | 36 | 44 | 21 | 41 | 44 | 42 |
| **摆放错误 (Placement Error)** | - | 55 | 67 | 67 | 68 | 62 | 69 |
| **粉末残留 (Powder Residue)** | 244 | - | - | - | - | - | - |
| **固体残留 (Solid Residue)** | - | 70 | 74 | 54 | 51 | 53 | 70 |
| **污渍 (Stain)** | 151 | 37 | 38 | 37 | 46 | 44 | 40 |

## 📖 详细层级报告

> 层级: 目标种类 → 异常大类 → 异常小类 → 点位 → 视角(shape数)

### beaker — beaker (烧杯)

**点位: 12 | 视角: 145 | 图片: 861**

#### damage — 主体破损 (Damage)

点位: 6 | 视角: 16 | 图片: 144

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **crack** | `analytical_balance` | 2 | 10.0 | 20 | `001`(10), `002`(10) |
| | `beaker_sample_carousel` | 6 | 9.2 | 55 | `001`(9), `002`(10), `003`(9), `004`(7), `005`(10), `006`(10) |
| | `magnetic_stirrer_01` | 2 | 8.0 | 16 | `001`(6), `002`(10) |
| | `magnetic_stirrer_02` | 2 | 7.0 | 14 | `001`(7), `002`(7) |
| | `mixed_sample_carousel` | 2 | 10.0 | 20 | `001`(10), `002`(10) |
| | `transfer_stage` | 2 | 9.5 | 19 | `001`(9), `002`(10) |

#### foreign_object_residue — 异物残留 (Foreign Object Residue)

点位: 6 | 视角: 16 | 图片: 72

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **glass_stirring_rod** | `analytical_balance` | 2 | 5.0 | 10 | `001`(5), `002`(5) |
| | `beaker_sample_carousel` | 6 | 5.0 | 30 | `001`(5), `002`(5), `003`(5), `004`(5), `005`(5), `006`(5) |
| | `magnetic_stirrer_01` | 2 | 4.5 | 9 | `001`(4), `002`(5) |
| | `magnetic_stirrer_02` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `mixed_sample_carousel` | 2 | 5.0 | 10 | `001`(5), `002`(5) |
| | `transfer_stage` | 2 | 4.5 | 9 | `001`(5), `002`(4) |

#### label_anomaly — 标签异常 (Label Anomaly)

点位: 7 | 视角: 22 | 图片: 72

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **label_damage** | `analytical_balance` | 1 | 2.0 | 2 | `002`(2) |
| | `beaker_sample_carousel` | 5 | 4.6 | 23 | `002`(5), `003`(4), `004`(5), `005`(5), `006`(4) |
| | `magnetic_stirrer_01` | 2 | 4.5 | 9 | `001`(4), `002`(5) |
| | `magnetic_stirrer_02` | 1 | 5.0 | 5 | `002`(5) |
| | `mixed_sample_carousel` | 1 | 4.0 | 4 | `002`(4) |
| | `transfer_stage` | 1 | 4.0 | 4 | `002`(4) |
| **label_soiling** | `analytical_balance` | 1 | 3.0 | 3 | `002`(3) |
| | `beaker_sample_carousel` | 4 | 2.5 | 10 | `002`(2), `004`(3), `005`(2), `006`(3) |
| | `magnetic_stirrer_01` | 2 | 2.5 | 5 | `001`(2), `002`(3) |
| | `magnetic_stirrer_02` | 1 | 1.0 | 1 | `002`(1) |
| | `mixed_sample_carousel` | 1 | 3.0 | 3 | `002`(3) |
| | `stack1` | 1 | 1.0 | 1 | `006`(1) |
| | `transfer_stage` | 1 | 2.0 | 2 | `002`(2) |

#### liquid_residue — 液体残留 (Liquid Residue)

点位: 12 | 视角: 28 | 图片: 108

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **colorless_liquid** | `analytical_balance` | 2 | 3.0 | 6 | `001`(1), `002`(5) |
| | `beaker_sample_carousel` | 4 | 3.5 | 14 | `002`(5), `003`(1), `004`(5), `006`(3) |
| | `magnetic_stirrer_01` | 2 | 3.5 | 7 | `001`(2), `002`(5) |
| | `magnetic_stirrer_02` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `mixed_sample_carousel` | 2 | 3.0 | 6 | `001`(1), `002`(5) |
| | `tianping` | 1 | 5.0 | 5 | `002`(5) |
| | `transfer_stage` | 2 | 4.0 | 8 | `001`(4), `002`(4) |
| **wall_liquid_residue** | `mixer1` | 2 | 5.0 | 10 | `001`(5), `002`(5) |
| | `mixer2` | 1 | 3.0 | 3 | `002`(3) |
| | `stack1` | 5 | 4.0 | 20 | `001`(4), `002`(5), `003`(5), `004`(5), `006`(1) |
| | `stack3` | 2 | 5.0 | 10 | `001`(5), `002`(5) |
| | `tianping` | 1 | 5.0 | 5 | `001`(5) |
| | `zhuanyi` | 2 | 5.0 | 10 | `001`(5), `002`(5) |

#### normal — 正常 (Normal)

点位: 6 | 视角: 16 | 图片: 70

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **(same)** | `analytical_balance` | 2 | 5.0 | 10 | `001`(5), `002`(5) |
| | `beaker_sample_carousel` | 6 | 4.8 | 29 | `001`(5), `002`(5), `003`(4), `004`(5), `005`(5), `006`(5) |
| | `magnetic_stirrer_01` | 2 | 3.5 | 7 | `001`(2), `002`(5) |
| | `magnetic_stirrer_02` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `mixed_sample_carousel` | 2 | 5.0 | 10 | `001`(5), `002`(5) |
| | `transfer_stage` | 2 | 5.0 | 10 | `001`(5), `002`(5) |

#### powder_residue — 粉末残留 (Powder Residue)

点位: 6 | 视角: 30 | 图片: 244

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **bottom_powder_residue** | `analytical_balance` | 2 | 15.0 | 30 | `001`(15), `002`(15) |
| | `beaker_sample_carousel` | 5 | 8.8 | 44 | `001`(15), `003`(4), `004`(4), `005`(10), `006`(11) |
| | `magnetic_stirrer_01` | 2 | 13.0 | 26 | `001`(11), `002`(15) |
| | `magnetic_stirrer_02` | 2 | 11.0 | 22 | `001`(11), `002`(11) |
| | `mixed_sample_carousel` | 2 | 15.0 | 30 | `001`(15), `002`(15) |
| | `transfer_stage` | 2 | 13.0 | 26 | `001`(15), `002`(11) |
| **crystalline_residue** | `analytical_balance` | 2 | 5.0 | 10 | `001`(5), `002`(5) |
| | `beaker_sample_carousel` | 5 | 5.0 | 25 | `001`(5), `002`(5), `003`(5), `005`(5), `006`(5) |
| | `magnetic_stirrer_01` | 2 | 3.5 | 7 | `001`(2), `002`(5) |
| | `magnetic_stirrer_02` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `mixed_sample_carousel` | 2 | 5.0 | 10 | `001`(5), `002`(5) |
| | `transfer_stage` | 2 | 5.0 | 10 | `001`(5), `002`(5) |

#### stain — 污渍 (Stain)

点位: 6 | 视角: 17 | 图片: 151

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **pigment_stain** | `analytical_balance` | 2 | 10.0 | 20 | `001`(10), `002`(10) |
| | `beaker_sample_carousel` | 6 | 9.5 | 57 | `001`(10), `002`(7), `003`(10), `004`(10), `005`(10), `006`(10) |
| | `magnetic_stirrer_01` | 2 | 9.5 | 19 | `001`(10), `002`(9) |
| | `magnetic_stirrer_02` | 2 | 7.0 | 14 | `001`(7), `002`(7) |
| | `mixed_sample_carousel` | 2 | 10.0 | 20 | `001`(10), `002`(10) |
| | `transfer_stage` | 2 | 10.0 | 20 | `001`(10), `002`(10) |
| **water_stain** | `beaker_sample_carousel` | 1 | 1.0 | 1 | `003`(1) |

### liquid_reservoir — liquid_reservoir (贮液器)

**点位: 5 | 视角: 181 | 图片: 522**

#### damage — 主体破损 (Damage)

点位: 5 | 视角: 32 | 图片: 97

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **crack** | `analytical_balance` | 1 | 1.0 | 1 | `002`(1) |
| | `magnetic_stirrer_01` | 2 | 1.5 | 3 | `001`(1), `002`(2) |
| | `magnetic_stirrer_02` | 1 | 4.0 | 4 | `002`(4) |
| | `pipetting_station` | 10 | 1.4 | 14 | `A3`(1), `B1`(1), `B2`(1), `B3`(2), `C1`(1), `C2`(1), `C3`(1), `D1`(2), `D2`(2), `D3`(2) |
| **cracked_lid** | `analytical_balance` | 2 | 5.0 | 10 | `001`(6), `002`(4) |
| | `magnetic_stirrer_01` | 2 | 4.0 | 8 | `001`(4), `002`(4) |
| | `magnetic_stirrer_02` | 2 | 5.0 | 10 | `001`(4), `002`(6) |
| | `pipetting_station` | 10 | 4.0 | 40 | `A3`(4), `B1`(4), `B2`(4), `B3`(4), `C1`(4), `C2`(4), `C3`(4), `D1`(4), `D2`(4), `D3`(4) |
| | `transfer_stage` | 2 | 3.5 | 7 | `001`(4), `002`(3) |

#### label_anomaly — 标签异常 (Label Anomaly)

点位: 5 | 视角: 23 | 图片: 67

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **label_contamination** | `transfer_stage` | 1 | 1.0 | 1 | `001`(1) |
| **label_detachment** | `analytical_balance` | 2 | 3.0 | 6 | `001`(4), `002`(2) |
| | `magnetic_stirrer_01` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `magnetic_stirrer_02` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `pipetting_station` | 10 | 4.0 | 40 | `A3`(4), `B1`(4), `B2`(4), `B3`(4), `C1`(4), `C2`(4), `C3`(4), `D1`(4), `D2`(4), `D3`(4) |
| | `transfer_stage` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| **label_soiling** | `analytical_balance` | 1 | 2.0 | 2 | `002`(2) |
| | `magnetic_stirrer_01` | 1 | 2.0 | 2 | `001`(2) |
| | `transfer_stage` | 2 | 2.0 | 4 | `001`(2), `002`(2) |

#### lid_anomaly — 盖子异常 (Lid Anomaly)

点位: 5 | 视角: 36 | 图片: 128

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **incorrect_lid** | `analytical_balance` | 2 | 7.0 | 14 | `001`(10), `002`(4) |
| | `magnetic_stirrer_01` | 2 | 4.5 | 9 | `001`(4), `002`(5) |
| | `magnetic_stirrer_02` | 2 | 5.0 | 10 | `001`(5), `002`(5) |
| | `pipetting_station` | 10 | 4.9 | 49 | `A3`(5), `B1`(5), `B2`(5), `B3`(5), `C1`(5), `C2`(5), `C3`(5), `D1`(5), `D2`(5), `D3`(4) |
| | `transfer_stage` | 2 | 4.0 | 8 | `001`(4), `002`(4) |
| **missing_lid** | `analytical_balance` | 2 | 3.0 | 6 | `001`(4), `002`(2) |
| | `magnetic_stirrer_01` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `magnetic_stirrer_02` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `pipetting_station` | 10 | 2.0 | 20 | `A3`(2), `B1`(2), `B2`(2), `B3`(2), `C1`(2), `C2`(2), `C3`(2), `D1`(2), `D2`(2), `D3`(2) |
| | `transfer_stage` | 2 | 2.0 | 4 | `001`(2), `002`(2) |

#### liquid_residue — 液体残留 (Liquid Residue)

点位: 4 | 视角: 17 | 图片: 32

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **colored_clear_liquid** | `analytical_balance` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `magnetic_stirrer_02` | 1 | 2.0 | 2 | `002`(2) |
| | `pipetting_station` | 10 | 2.0 | 20 | `A3`(2), `B1`(2), `B2`(2), `B3`(2), `C1`(2), `C2`(2), `C3`(2), `D1`(2), `D2`(2), `D3`(2) |
| | `transfer_stage` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| **colorless_liquid** | `analytical_balance` | 1 | 1.0 | 1 | `001`(1) |
| **(same)** | `analytical_balance` | 1 | 1.0 | 1 | `002`(1) |

#### normal — 正常 (Normal)

点位: 5 | 视角: 18 | 图片: 36

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **(same)** | `analytical_balance` | 2 | 3.0 | 6 | `001`(4), `002`(2) |
| | `magnetic_stirrer_01` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `magnetic_stirrer_02` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `pipetting_station` | 10 | 1.8 | 18 | `A3`(1), `B1`(1), `B2`(2), `B3`(2), `C1`(2), `C2`(2), `C3`(2), `D1`(2), `D2`(2), `D3`(2) |
| | `transfer_stage` | 2 | 2.0 | 4 | `001`(2), `002`(2) |

#### placement_error — 摆放错误 (Placement Error)

点位: 5 | 视角: 19 | 图片: 55

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **tilte_placement** | `magnetic_stirrer_01` | 1 | 1.0 | 1 | `002`(1) |
| **tilted_placement** | `analytical_balance` | 2 | 3.5 | 7 | `001`(5), `002`(2) |
| | `magnetic_stirrer_01` | 2 | 3.5 | 7 | `001`(4), `002`(3) |
| | `magnetic_stirrer_02` | 2 | 3.0 | 6 | `001`(3), `002`(3) |
| | `pipetting_station` | 10 | 3.0 | 30 | `A3`(3), `B1`(3), `B2`(3), `B3`(3), `C1`(3), `C2`(3), `C3`(3), `D1`(3), `D2`(3), `D3`(3) |
| | `transfer_stage` | 2 | 2.0 | 4 | `001`(2), `002`(2) |

#### solid_residue — 固体残留 (Solid Residue)

点位: 5 | 视角: 18 | 图片: 70

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **powder** | `analytical_balance` | 2 | 5.0 | 10 | `001`(4), `002`(6) |
| | `magnetic_stirrer_01` | 2 | 4.0 | 8 | `001`(4), `002`(4) |
| | `magnetic_stirrer_02` | 2 | 4.0 | 8 | `001`(4), `002`(4) |
| | `pipetting_station` | 10 | 4.0 | 40 | `A3`(4), `B1`(4), `B2`(4), `B3`(4), `C1`(4), `C2`(4), `C3`(4), `D1`(4), `D2`(4), `D3`(4) |
| | `transfer_stage` | 2 | 2.0 | 4 | `001`(2), `002`(2) |

#### stain — 污渍 (Stain)

点位: 5 | 视角: 18 | 图片: 37

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **pigment_stain** | `analytical_balance` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `magnetic_stirrer_01` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `magnetic_stirrer_02` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `pipetting_station` | 10 | 2.1 | 21 | `A3`(2), `B1`(2), `B2`(2), `B3`(3), `C1`(2), `C2`(2), `C3`(2), `D1`(2), `D2`(2), `D3`(2) |
| | `transfer_stage` | 2 | 2.0 | 4 | `001`(2), `002`(2) |

### multiwell_plate_06 — multiwell_plate_06 (6孔板)

**点位: 10 | 视角: 227 | 图片: 623**

#### damage — 主体破损 (Damage)

点位: 10 | 视角: 47 | 图片: 135

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **crack** | `analytical_balance` | 2 | 1.5 | 3 | `001`(2), `002`(1) |
| | `magnetic_stirrer_01` | 2 | 1.5 | 3 | `001`(1), `002`(2) |
| | `magnetic_stirrer_02` | 1 | 1.0 | 1 | `002`(1) |
| | `mixed_sample_carousel-level3` | 2 | 2.0 | 4 | `2`(2), `3`(2) |
| | `mixed_sample_carousel-level5` | 2 | 2.0 | 4 | `1`(2), `2`(2) |
| | `mixed_sample_carousel-level6` | 2 | 2.0 | 4 | `1`(2), `2`(2) |
| | `pipetting_station` | 10 | 3.6 | 36 | `A3`(4), `B1`(4), `B2`(4), `B3`(3), `C1`(4), `C2`(3), `C3`(4), `D1`(4), `D2`(2), `D3`(4) |
| | `tianping` | 1 | 2.0 | 2 | `002`(2) |
| | `transfer_stage` | 1 | 1.0 | 1 | `002`(1) |
| | `zhuanyi` | 1 | 2.0 | 2 | `002`(2) |
| **cracked_lid** | `analytical_balance` | 2 | 4.5 | 9 | `001`(6), `002`(3) |
| | `magnetic_stirrer_01` | 2 | 4.5 | 9 | `001`(6), `002`(3) |
| | `magnetic_stirrer_02` | 2 | 4.0 | 8 | `001`(4), `002`(4) |
| | `mixed_sample_carousel-level3` | 2 | 1.0 | 2 | `2`(1), `3`(1) |
| | `mixed_sample_carousel-level5` | 1 | 1.0 | 1 | `2`(1) |
| | `mixed_sample_carousel-level6` | 2 | 1.0 | 2 | `1`(1), `2`(1) |
| | `pipetting_station` | 10 | 4.0 | 40 | `A3`(4), `B1`(4), `B2`(4), `B3`(4), `C1`(4), `C2`(4), `C3`(4), `D1`(4), `D2`(4), `D3`(4) |
| | `transfer_stage` | 2 | 2.0 | 4 | `001`(2), `002`(2) |

#### label_anomaly — 标签异常 (Label Anomaly)

点位: 8 | 视角: 24 | 图片: 81

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **label_detachment** | `analytical_balance` | 2 | 3.0 | 6 | `001`(4), `002`(2) |
| | `magnetic_stirrer_01` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `magnetic_stirrer_02` | 2 | 1.5 | 3 | `001`(2), `002`(1) |
| | `mixed_sample_carousel-level3` | 2 | 4.0 | 8 | `2`(4), `3`(4) |
| | `mixed_sample_carousel-level5` | 2 | 4.0 | 8 | `1`(4), `2`(4) |
| | `mixed_sample_carousel-level6` | 2 | 4.0 | 8 | `1`(4), `2`(4) |
| | `pipetting_station` | 10 | 4.0 | 40 | `A3`(4), `B1`(4), `B2`(4), `B3`(4), `C1`(4), `C2`(4), `C3`(4), `D1`(4), `D2`(4), `D3`(4) |
| | `transfer_stage` | 2 | 2.0 | 4 | `001`(2), `002`(2) |

#### lid_anomaly — 盖子异常 (Lid Anomaly)

点位: 8 | 视角: 45 | 图片: 146

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **incorrect_lid** | `analytical_balance` | 2 | 5.5 | 11 | `001`(8), `002`(3) |
| | `magnetic_stirrer_01` | 2 | 4.0 | 8 | `001`(4), `002`(4) |
| | `magnetic_stirrer_02` | 2 | 4.5 | 9 | `001`(5), `002`(4) |
| | `mixed_sample_carousel-level3` | 2 | 3.5 | 7 | `2`(4), `3`(3) |
| | `mixed_sample_carousel-level5` | 2 | 5.0 | 10 | `1`(5), `2`(5) |
| | `mixed_sample_carousel-level6` | 2 | 4.5 | 9 | `1`(4), `2`(5) |
| | `pipetting_station` | 9 | 5.0 | 45 | `A3`(5), `B2`(5), `B3`(5), `C1`(5), `C2`(5), `C3`(5), `D1`(5), `D2`(5), `D3`(5) |
| | `transfer_stage` | 2 | 3.5 | 7 | `001`(3), `002`(4) |
| **missing_lid** | `analytical_balance` | 2 | 3.0 | 6 | `001`(4), `002`(2) |
| | `magnetic_stirrer_01` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `magnetic_stirrer_02` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `mixed_sample_carousel-level3` | 2 | 1.0 | 2 | `2`(1), `3`(1) |
| | `mixed_sample_carousel-level5` | 2 | 1.0 | 2 | `1`(1), `2`(1) |
| | `mixed_sample_carousel-level6` | 2 | 1.0 | 2 | `1`(1), `2`(1) |
| | `pipetting_station` | 8 | 2.0 | 16 | `A3`(2), `B2`(2), `B3`(2), `C1`(2), `C2`(2), `D1`(2), `D2`(2), `D3`(2) |
| | `transfer_stage` | 2 | 2.0 | 4 | `001`(2), `002`(2) |

#### liquid_residue — 液体残留 (Liquid Residue)

点位: 7 | 视角: 23 | 图片: 38

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **colored_clear_liquid** | `analytical_balance` | 1 | 2.0 | 2 | `001`(2) |
| | `magnetic_stirrer_01` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `magnetic_stirrer_02` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `mixed_sample_carousel-level3` | 2 | 1.0 | 2 | `2`(1), `3`(1) |
| | `mixed_sample_carousel-level5` | 2 | 1.0 | 2 | `1`(1), `2`(1) |
| | `mixed_sample_carousel-level6` | 2 | 1.0 | 2 | `1`(1), `2`(1) |
| | `pipetting_station` | 10 | 1.9 | 19 | `A3`(2), `B1`(2), `B2`(2), `B3`(1), `C1`(2), `C2`(2), `C3`(2), `D1`(2), `D2`(2), `D3`(2) |
| **colorless_liquid** | `magnetic_stirrer_01` | 1 | 2.0 | 2 | `001`(2) |
| | `pipetting_station` | 1 | 1.0 | 1 | `B3`(1) |

#### normal — 正常 (Normal)

点位: 8 | 视角: 24 | 图片: 44

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **(same)** | `analytical_balance` | 2 | 3.0 | 6 | `001`(4), `002`(2) |
| | `magnetic_stirrer_01` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `magnetic_stirrer_02` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `mixed_sample_carousel-level3` | 2 | 1.0 | 2 | `2`(1), `3`(1) |
| | `mixed_sample_carousel-level5` | 2 | 1.0 | 2 | `1`(1), `2`(1) |
| | `mixed_sample_carousel-level6` | 2 | 1.0 | 2 | `1`(1), `2`(1) |
| | `pipetting_station` | 10 | 2.0 | 20 | `A3`(2), `B1`(2), `B2`(2), `B3`(2), `C1`(2), `C2`(2), `C3`(2), `D1`(2), `D2`(2), `D3`(2) |
| | `transfer_stage` | 2 | 2.0 | 4 | `001`(2), `002`(2) |

#### placement_error — 摆放错误 (Placement Error)

点位: 8 | 视角: 22 | 图片: 67

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **tilted_placement** | `analytical_balance` | 2 | 4.5 | 9 | `001`(6), `002`(3) |
| | `magnetic_stirrer_01` | 2 | 3.0 | 6 | `001`(3), `002`(3) |
| | `magnetic_stirrer_02` | 2 | 2.5 | 5 | `001`(3), `002`(2) |
| | `mixed_sample_carousel-level3` | 2 | 3.0 | 6 | `2`(3), `3`(3) |
| | `mixed_sample_carousel-level5` | 2 | 3.0 | 6 | `1`(3), `2`(3) |
| | `mixed_sample_carousel-level6` | 2 | 3.0 | 6 | `1`(3), `2`(3) |
| | `pipetting_station` | 9 | 2.9 | 26 | `A3`(3), `B2`(3), `B3`(3), `C1`(3), `C2`(3), `C3`(2), `D1`(3), `D2`(3), `D3`(3) |
| | `transfer_stage` | 1 | 3.0 | 3 | `001`(3) |

#### solid_residue — 固体残留 (Solid Residue)

点位: 8 | 视角: 24 | 图片: 74

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **powder** | `analytical_balance` | 2 | 4.0 | 8 | `001`(4), `002`(4) |
| | `magnetic_stirrer_01` | 2 | 4.0 | 8 | `001`(4), `002`(4) |
| | `magnetic_stirrer_02` | 2 | 4.0 | 8 | `001`(4), `002`(4) |
| | `mixed_sample_carousel-level3` | 2 | 1.0 | 2 | `2`(1), `3`(1) |
| | `mixed_sample_carousel-level5` | 2 | 1.0 | 2 | `1`(1), `2`(1) |
| | `mixed_sample_carousel-level6` | 2 | 1.0 | 2 | `1`(1), `2`(1) |
| | `pipetting_station` | 10 | 4.0 | 40 | `A3`(4), `B1`(4), `B2`(4), `B3`(4), `C1`(4), `C2`(4), `C3`(4), `D1`(4), `D2`(4), `D3`(4) |
| | `transfer_stage` | 2 | 2.0 | 4 | `001`(2), `002`(2) |

#### stain — 污渍 (Stain)

点位: 5 | 视角: 18 | 图片: 38

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **pigment_stain** | `analytical_balance` | 2 | 3.0 | 6 | `001`(4), `002`(2) |
| | `magnetic_stirrer_01` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `magnetic_stirrer_02` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `pipetting_station` | 10 | 2.0 | 20 | `A3`(2), `B1`(2), `B2`(2), `B3`(2), `C1`(2), `C2`(2), `C3`(2), `D1`(2), `D2`(2), `D3`(2) |
| | `transfer_stage` | 2 | 2.0 | 4 | `001`(2), `002`(2) |

### multiwell_plate_11 — multiwell_plate_11 (11孔板)

**点位: 8 | 视角: 145 | 图片: 385**

#### label_anomaly — 标签异常 (Label Anomaly)

点位: 8 | 视角: 24 | 图片: 82

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **label_detachment** | `analytical_balance` | 2 | 3.0 | 6 | `001`(4), `002`(2) |
| | `magnetic_stirrer_01` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `magnetic_stirrer_02` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `mixed_sample_carousel-level3` | 2 | 4.0 | 8 | `2`(4), `3`(4) |
| | `mixed_sample_carousel-level5` | 2 | 4.0 | 8 | `1`(4), `2`(4) |
| | `mixed_sample_carousel-level6` | 2 | 4.0 | 8 | `1`(4), `2`(4) |
| | `pipetting_station` | 10 | 4.0 | 40 | `A3`(4), `B1`(4), `B2`(4), `B3`(4), `C1`(4), `C2`(4), `C3`(4), `D1`(4), `D2`(4), `D3`(4) |
| | `transfer_stage` | 2 | 2.0 | 4 | `001`(2), `002`(2) |

#### lid_anomaly — 盖子异常 (Lid Anomaly)

点位: 8 | 视角: 25 | 图片: 79

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **incorrect_lid** | `analytical_balance` | 2 | 4.5 | 9 | `001`(7), `002`(2) |
| | `magnetic_stirrer_01` | 2 | 3.0 | 6 | `001`(3), `002`(3) |
| | `magnetic_stirrer_02` | 2 | 3.0 | 6 | `001`(3), `002`(3) |
| | `mixed_sample_carousel-level3` | 2 | 3.0 | 6 | `2`(3), `3`(3) |
| | `mixed_sample_carousel-level5` | 2 | 3.5 | 7 | `1`(3), `2`(4) |
| | `mixed_sample_carousel-level6` | 2 | 5.0 | 10 | `1`(5), `2`(5) |
| | `pipetting_station` | 10 | 3.0 | 30 | `A3`(3), `B1`(3), `B2`(3), `B3`(3), `C1`(3), `C2`(3), `C3`(3), `D1`(3), `D2`(3), `D3`(3) |
| | `transfer_stage` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| **missing_lid** | `analytical_balance` | 1 | 1.0 | 1 | `001`(1) |

#### liquid_residue — 液体残留 (Liquid Residue)

点位: 8 | 视角: 25 | 图片: 45

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **colored_clear_liquid** | `analytical_balance` | 2 | 3.0 | 6 | `001`(4), `002`(2) |
| | `magnetic_stirrer_01` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `magnetic_stirrer_02` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `mixed_sample_carousel-level3` | 1 | 1.0 | 1 | `2`(1) |
| | `mixed_sample_carousel-level5` | 2 | 1.0 | 2 | `1`(1), `2`(1) |
| | `mixed_sample_carousel-level6` | 2 | 1.0 | 2 | `1`(1), `2`(1) |
| | `pipetting_station` | 10 | 2.0 | 20 | `A3`(2), `B1`(2), `B2`(2), `B3`(2), `C1`(2), `C2`(2), `C3`(2), `D1`(2), `D2`(2), `D3`(2) |
| | `transfer_stage` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| **colorless_liquid** | `analytical_balance` | 1 | 1.0 | 1 | `001`(1) |
| | `mixed_sample_carousel-level3` | 1 | 1.0 | 1 | `3`(1) |

#### normal — 正常 (Normal)

点位: 7 | 视角: 13 | 图片: 21

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **(same)** | `analytical_balance` | 2 | 3.0 | 6 | `001`(4), `002`(2) |
| | `magnetic_stirrer_01` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `magnetic_stirrer_02` | 1 | 2.0 | 2 | `001`(2) |
| | `mixed_sample_carousel-level3` | 2 | 1.0 | 2 | `2`(1), `3`(1) |
| | `mixed_sample_carousel-level5` | 2 | 1.0 | 2 | `1`(1), `2`(1) |
| | `mixed_sample_carousel-level6` | 2 | 1.0 | 2 | `1`(1), `2`(1) |
| | `transfer_stage` | 2 | 1.5 | 3 | `001`(1), `002`(2) |

#### placement_error — 摆放错误 (Placement Error)

点位: 7 | 视角: 21 | 图片: 67

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **tilted_placement** | `analytical_balance` | 2 | 5.5 | 11 | `001`(8), `002`(3) |
| | `magnetic_stirrer_02` | 2 | 3.0 | 6 | `001`(3), `002`(3) |
| | `mixed_sample_carousel-level3` | 2 | 3.0 | 6 | `2`(3), `3`(3) |
| | `mixed_sample_carousel-level5` | 2 | 3.0 | 6 | `1`(3), `2`(3) |
| | `mixed_sample_carousel-level6` | 2 | 3.0 | 6 | `1`(3), `2`(3) |
| | `pipetting_station` | 10 | 3.0 | 30 | `A3`(3), `B1`(3), `B2`(3), `B3`(3), `C1`(3), `C2`(3), `C3`(3), `D1`(3), `D2`(3), `D3`(3) |
| | `transfer_stage` | 1 | 2.0 | 2 | `002`(2) |

#### solid_residue — 固体残留 (Solid Residue)

点位: 5 | 视角: 16 | 图片: 54

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **powder** | `analytical_balance` | 2 | 3.0 | 6 | `001`(4), `002`(2) |
| | `magnetic_stirrer_01` | 1 | 4.0 | 4 | `001`(4) |
| | `magnetic_stirrer_02` | 1 | 2.0 | 2 | `001`(2) |
| | `pipetting_station` | 10 | 3.8 | 38 | `A3`(2), `B1`(4), `B2`(4), `B3`(4), `C1`(4), `C2`(4), `C3`(4), `D1`(4), `D2`(4), `D3`(4) |
| | `transfer_stage` | 2 | 2.0 | 4 | `001`(2), `002`(2) |

#### stain — 污渍 (Stain)

点位: 7 | 视角: 21 | 图片: 37

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **pigment_stain** | `analytical_balance` | 2 | 2.5 | 5 | `001`(4), `002`(1) |
| | `magnetic_stirrer_01` | 2 | 1.5 | 3 | `001`(1), `002`(2) |
| | `magnetic_stirrer_02` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `mixed_sample_carousel-level3` | 2 | 1.0 | 2 | `2`(1), `3`(1) |
| | `mixed_sample_carousel-level5` | 1 | 1.0 | 1 | `2`(1) |
| | `mixed_sample_carousel-level6` | 2 | 1.0 | 2 | `1`(1), `2`(1) |
| | `pipetting_station` | 10 | 2.0 | 20 | `A3`(2), `B1`(2), `B2`(2), `B3`(2), `C1`(2), `C2`(2), `C3`(2), `D1`(2), `D2`(2), `D3`(2) |

### multiwell_plate_24 — multiwell_plate_24 (24孔板)

**点位: 8 | 视角: 210 | 图片: 560**

#### damage — 主体破损 (Damage)

点位: 8 | 视角: 33 | 图片: 87

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **crack** | `magnetic_stirrer_01` | 2 | 1.0 | 2 | `001`(1), `002`(1) |
| | `magnetic_stirrer_02` | 1 | 1.0 | 1 | `002`(1) |
| | `mixed_sample_carousel-level3` | 2 | 1.0 | 2 | `2`(1), `3`(1) |
| | `mixed_sample_carousel-level5` | 2 | 1.0 | 2 | `1`(1), `2`(1) |
| | `mixed_sample_carousel-level6` | 1 | 1.0 | 1 | `1`(1) |
| | `pipetting_station` | 5 | 1.0 | 5 | `B1`(1), `B2`(1), `B3`(1), `C1`(1), `D3`(1) |
| **cracked_lid** | `analytical_balance` | 2 | 4.5 | 9 | `001`(5), `002`(4) |
| | `magnetic_stirrer_01` | 2 | 4.5 | 9 | `001`(4), `002`(5) |
| | `magnetic_stirrer_02` | 2 | 4.0 | 8 | `001`(4), `002`(4) |
| | `mixed_sample_carousel-level6` | 2 | 1.0 | 2 | `1`(1), `2`(1) |
| | `pipetting_station` | 10 | 3.8 | 38 | `A3`(4), `B1`(4), `B2`(4), `B3`(4), `C1`(4), `C2`(4), `C3`(2), `D1`(4), `D2`(4), `D3`(4) |
| | `transfer_stage` | 2 | 4.0 | 8 | `001`(4), `002`(4) |

#### label_anomaly — 标签异常 (Label Anomaly)

点位: 8 | 视角: 23 | 图片: 76

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **label_detachment** | `analytical_balance` | 2 | 3.0 | 6 | `001`(4), `002`(2) |
| | `magnetic_stirrer_01` | 1 | 2.0 | 2 | `002`(2) |
| | `magnetic_stirrer_02` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `mixed_sample_carousel-level3` | 2 | 4.0 | 8 | `2`(4), `3`(4) |
| | `mixed_sample_carousel-level5` | 2 | 4.0 | 8 | `1`(4), `2`(4) |
| | `mixed_sample_carousel-level6` | 2 | 4.0 | 8 | `1`(4), `2`(4) |
| | `pipetting_station` | 9 | 3.9 | 35 | `A3`(4), `B1`(4), `B2`(4), `B3`(4), `C1`(4), `C2`(4), `D1`(4), `D2`(3), `D3`(4) |
| | `transfer_stage` | 2 | 1.5 | 3 | `001`(2), `002`(1) |
| **label_soiling** | `magnetic_stirrer_01` | 1 | 2.0 | 2 | `001`(2) |

#### lid_anomaly — 盖子异常 (Lid Anomaly)

点位: 8 | 视角: 46 | 图片: 155

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **incorrect_lid** | `analytical_balance` | 2 | 8.0 | 16 | `001`(12), `002`(4) |
| | `magnetic_stirrer_01` | 2 | 5.0 | 10 | `001`(5), `002`(5) |
| | `magnetic_stirrer_02` | 2 | 4.5 | 9 | `001`(5), `002`(4) |
| | `mixed_sample_carousel-level3` | 2 | 4.5 | 9 | `2`(4), `3`(5) |
| | `mixed_sample_carousel-level5` | 2 | 4.0 | 8 | `1`(4), `2`(4) |
| | `mixed_sample_carousel-level6` | 2 | 4.0 | 8 | `1`(3), `2`(5) |
| | `pipetting_station` | 9 | 5.0 | 45 | `A3`(5), `B1`(5), `B2`(5), `B3`(5), `C1`(5), `C2`(5), `D1`(5), `D2`(5), `D3`(5) |
| | `transfer_stage` | 2 | 4.0 | 8 | `001`(4), `002`(4) |
| **missing_lid** | `analytical_balance` | 2 | 3.0 | 6 | `001`(4), `002`(2) |
| | `magnetic_stirrer_01` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `magnetic_stirrer_02` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `mixed_sample_carousel-level3` | 2 | 1.0 | 2 | `2`(1), `3`(1) |
| | `mixed_sample_carousel-level5` | 2 | 1.0 | 2 | `1`(1), `2`(1) |
| | `mixed_sample_carousel-level6` | 2 | 1.0 | 2 | `1`(1), `2`(1) |
| | `pipetting_station` | 9 | 2.0 | 18 | `A3`(2), `B1`(2), `B2`(2), `B3`(2), `C1`(2), `C2`(2), `D1`(2), `D2`(2), `D3`(2) |
| | `transfer_stage` | 2 | 2.0 | 4 | `001`(2), `002`(2) |

#### liquid_residue — 液体残留 (Liquid Residue)

点位: 7 | 视角: 21 | 图片: 36

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **colored_clear_liquid** | `analytical_balance` | 1 | 2.0 | 2 | `001`(2) |
| | `magnetic_stirrer_01` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `magnetic_stirrer_02` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `mixed_sample_carousel-level3` | 2 | 1.0 | 2 | `2`(1), `3`(1) |
| | `mixed_sample_carousel-level5` | 1 | 1.0 | 1 | `1`(1) |
| | `mixed_sample_carousel-level6` | 2 | 1.0 | 2 | `1`(1), `2`(1) |
| | `pipetting_station` | 10 | 2.0 | 20 | `A3`(2), `B1`(2), `B2`(2), `B3`(2), `C1`(2), `C2`(2), `C3`(2), `D1`(2), `D2`(2), `D3`(2) |
| **colorless_liquid** | `mixed_sample_carousel-level5` | 1 | 1.0 | 1 | `2`(1) |

#### normal — 正常 (Normal)

点位: 8 | 视角: 23 | 图片: 41

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **(same)** | `analytical_balance` | 2 | 3.0 | 6 | `001`(4), `002`(2) |
| | `magnetic_stirrer_01` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `magnetic_stirrer_02` | 2 | 1.5 | 3 | `001`(2), `002`(1) |
| | `mixed_sample_carousel-level3` | 2 | 1.0 | 2 | `2`(1), `3`(1) |
| | `mixed_sample_carousel-level5` | 2 | 1.0 | 2 | `1`(1), `2`(1) |
| | `mixed_sample_carousel-level6` | 2 | 1.0 | 2 | `1`(1), `2`(1) |
| | `pipetting_station` | 9 | 2.0 | 18 | `A3`(2), `B1`(2), `B2`(2), `B3`(2), `C1`(2), `C2`(2), `D1`(2), `D2`(2), `D3`(2) |
| | `transfer_stage` | 2 | 2.0 | 4 | `001`(2), `002`(2) |

#### placement_error — 摆放错误 (Placement Error)

点位: 8 | 视角: 22 | 图片: 68

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **tilted_placement** | `analytical_balance` | 2 | 5.5 | 11 | `001`(8), `002`(3) |
| | `magnetic_stirrer_01` | 2 | 3.0 | 6 | `001`(3), `002`(3) |
| | `magnetic_stirrer_02` | 2 | 2.5 | 5 | `001`(3), `002`(2) |
| | `mixed_sample_carousel-level3` | 2 | 3.0 | 6 | `2`(3), `3`(3) |
| | `mixed_sample_carousel-level5` | 1 | 3.0 | 3 | `1`(3) |
| | `mixed_sample_carousel-level6` | 1 | 3.0 | 3 | `2`(3) |
| | `pipetting_station` | 10 | 3.0 | 30 | `A3`(3), `B1`(3), `B2`(3), `B3`(3), `C1`(3), `C2`(3), `C3`(3), `D1`(3), `D2`(3), `D3`(3) |
| | `transfer_stage` | 1 | 3.0 | 3 | `001`(3) |
| **titlted_placement** | `magnetic_stirrer_01` | 1 | 1.0 | 1 | `001`(1) |

#### solid_residue — 固体残留 (Solid Residue)

点位: 7 | 视角: 19 | 图片: 51

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **powder** | `analytical_balance` | 1 | 2.0 | 2 | `001`(2) |
| | `magnetic_stirrer_01` | 1 | 4.0 | 4 | `001`(4) |
| | `mixed_sample_carousel-level3` | 1 | 1.0 | 1 | `2`(1) |
| | `mixed_sample_carousel-level5` | 2 | 1.0 | 2 | `1`(1), `2`(1) |
| | `mixed_sample_carousel-level6` | 2 | 1.0 | 2 | `1`(1), `2`(1) |
| | `pipetting_station` | 10 | 3.6 | 36 | `A3`(2), `B1`(4), `B2`(4), `B3`(4), `C1`(4), `C2`(4), `C3`(4), `D1`(2), `D2`(4), `D3`(4) |
| | `transfer_stage` | 2 | 2.0 | 4 | `001`(2), `002`(2) |

#### stain — 污渍 (Stain)

点位: 8 | 视角: 23 | 图片: 46

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **pigment_stain** | `analytical_balance` | 2 | 3.5 | 7 | `001`(5), `002`(2) |
| | `magnetic_stirrer_01` | 2 | 3.0 | 6 | `001`(2), `002`(4) |
| | `magnetic_stirrer_02` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `mixed_sample_carousel-level3` | 2 | 1.0 | 2 | `2`(1), `3`(1) |
| | `mixed_sample_carousel-level5` | 2 | 1.0 | 2 | `1`(1), `2`(1) |
| | `mixed_sample_carousel-level6` | 1 | 1.0 | 1 | `2`(1) |
| | `pipetting_station` | 10 | 2.0 | 20 | `A3`(2), `B1`(2), `B2`(2), `B3`(2), `C1`(2), `C2`(2), `C3`(2), `D1`(2), `D2`(2), `D3`(2) |
| | `transfer_stage` | 2 | 2.0 | 4 | `001`(2), `002`(2) |

### multiwell_plate_48 — multiwell_plate_48 (48孔板)

**点位: 8 | 视角: 219 | 图片: 553**

#### damage — 主体破损 (Damage)

点位: 8 | 视角: 37 | 图片: 82

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **crack** | `analytical_balance` | 1 | 2.0 | 2 | `002`(2) |
| | `magnetic_stirrer_01` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `magnetic_stirrer_02` | 1 | 4.0 | 4 | `002`(4) |
| | `mixed_sample_carousel-level3` | 2 | 1.0 | 2 | `2`(1), `3`(1) |
| | `mixed_sample_carousel-level5` | 2 | 1.0 | 2 | `1`(1), `2`(1) |
| | `mixed_sample_carousel-level6` | 2 | 1.0 | 2 | `1`(1), `2`(1) |
| | `pipetting_station` | 8 | 1.6 | 13 | `A3`(1), `B1`(2), `B2`(2), `B3`(2), `C1`(2), `C2`(1), `C3`(1), `D3`(2) |
| **cracked_lid** | `analytical_balance` | 1 | 2.0 | 2 | `002`(2) |
| | `magnetic_stirrer_01` | 1 | 4.0 | 4 | `002`(4) |
| | `magnetic_stirrer_02` | 2 | 3.0 | 6 | `001`(2), `002`(4) |
| | `mixed_sample_carousel-level3` | 2 | 1.0 | 2 | `2`(1), `3`(1) |
| | `mixed_sample_carousel-level6` | 1 | 1.0 | 1 | `2`(1) |
| | `pipetting_station` | 10 | 3.5 | 35 | `A3`(4), `B1`(4), `B2`(4), `B3`(4), `C1`(4), `C2`(4), `C3`(1), `D1`(2), `D2`(4), `D3`(4) |
| | `transfer_stage` | 2 | 1.5 | 3 | `001`(2), `002`(1) |

#### label_anomaly — 标签异常 (Label Anomaly)

点位: 8 | 视角: 24 | 图片: 79

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **label_detachment** | `analytical_balance` | 2 | 3.0 | 6 | `001`(4), `002`(2) |
| | `magnetic_stirrer_01` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `magnetic_stirrer_02` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `mixed_sample_carousel-level3` | 2 | 4.0 | 8 | `2`(4), `3`(4) |
| | `mixed_sample_carousel-level5` | 2 | 4.0 | 8 | `1`(4), `2`(4) |
| | `mixed_sample_carousel-level6` | 2 | 4.0 | 8 | `1`(4), `2`(4) |
| | `pipetting_station` | 10 | 3.7 | 37 | `A3`(2), `B1`(4), `B2`(4), `B3`(4), `C1`(4), `C2`(3), `C3`(4), `D1`(4), `D2`(4), `D3`(4) |
| | `transfer_stage` | 2 | 2.0 | 4 | `001`(2), `002`(2) |

#### lid_anomaly — 盖子异常 (Lid Anomaly)

点位: 8 | 视角: 44 | 图片: 145

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **incorrect_lid** | `analytical_balance` | 2 | 5.0 | 10 | `001`(8), `002`(2) |
| | `magnetic_stirrer_01` | 1 | 5.0 | 5 | `001`(5) |
| | `magnetic_stirrer_02` | 2 | 5.0 | 10 | `001`(5), `002`(5) |
| | `mixed_sample_carousel-level3` | 2 | 4.5 | 9 | `2`(4), `3`(5) |
| | `mixed_sample_carousel-level5` | 2 | 4.5 | 9 | `1`(5), `2`(4) |
| | `mixed_sample_carousel-level6` | 2 | 4.5 | 9 | `1`(4), `2`(5) |
| | `pipetting_station` | 10 | 5.0 | 50 | `A3`(5), `B1`(5), `B2`(5), `B3`(5), `C1`(5), `C2`(5), `C3`(5), `D1`(5), `D2`(5), `D3`(5) |
| | `transfer_stage` | 2 | 3.5 | 7 | `001`(3), `002`(4) |
| **missing_lid** | `analytical_balance` | 1 | 2.0 | 2 | `001`(2) |
| | `magnetic_stirrer_01` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `magnetic_stirrer_02` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `mixed_sample_carousel-level3` | 2 | 1.0 | 2 | `2`(1), `3`(1) |
| | `mixed_sample_carousel-level5` | 2 | 1.0 | 2 | `1`(1), `2`(1) |
| | `mixed_sample_carousel-level6` | 2 | 1.0 | 2 | `1`(1), `2`(1) |
| | `pipetting_station` | 10 | 2.0 | 20 | `A3`(2), `B1`(2), `B2`(2), `B3`(2), `C1`(2), `C2`(2), `C3`(2), `D1`(2), `D2`(2), `D3`(2) |

#### liquid_residue — 液体残留 (Liquid Residue)

点位: 8 | 视角: 24 | 图片: 44

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **colored_clear_liquid** | `analytical_balance` | 2 | 3.0 | 6 | `001`(4), `002`(2) |
| | `magnetic_stirrer_01` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `magnetic_stirrer_02` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `mixed_sample_carousel-level3` | 1 | 1.0 | 1 | `2`(1) |
| | `mixed_sample_carousel-level5` | 2 | 1.0 | 2 | `1`(1), `2`(1) |
| | `mixed_sample_carousel-level6` | 2 | 1.0 | 2 | `1`(1), `2`(1) |
| | `pipetting_station` | 10 | 2.0 | 20 | `A3`(2), `B1`(2), `B2`(2), `B3`(2), `C1`(2), `C2`(2), `C3`(2), `D1`(2), `D2`(2), `D3`(2) |
| | `transfer_stage` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| **colorless_liquid** | `mixed_sample_carousel-level3` | 1 | 1.0 | 1 | `3`(1) |

#### normal — 正常 (Normal)

点位: 8 | 视角: 24 | 图片: 44

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **(same)** | `analytical_balance` | 2 | 3.0 | 6 | `001`(4), `002`(2) |
| | `magnetic_stirrer_01` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `magnetic_stirrer_02` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `mixed_sample_carousel-level3` | 2 | 1.0 | 2 | `2`(1), `3`(1) |
| | `mixed_sample_carousel-level5` | 2 | 1.0 | 2 | `1`(1), `2`(1) |
| | `mixed_sample_carousel-level6` | 2 | 1.0 | 2 | `1`(1), `2`(1) |
| | `pipetting_station` | 10 | 2.0 | 20 | `A3`(2), `B1`(2), `B2`(2), `B3`(2), `C1`(2), `C2`(2), `C3`(2), `D1`(2), `D2`(2), `D3`(2) |
| | `transfer_stage` | 2 | 2.0 | 4 | `001`(2), `002`(2) |

#### placement_error — 摆放错误 (Placement Error)

点位: 8 | 视角: 20 | 图片: 62

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **tilted_placement** | `analytical_balance` | 2 | 5.0 | 10 | `001`(7), `002`(3) |
| | `magnetic_stirrer_01` | 1 | 3.0 | 3 | `001`(3) |
| | `magnetic_stirrer_02` | 2 | 2.0 | 4 | `001`(3), `002`(1) |
| | `mixed_sample_carousel-level3` | 2 | 3.0 | 6 | `2`(3), `3`(3) |
| | `mixed_sample_carousel-level5` | 1 | 3.0 | 3 | `1`(3) |
| | `mixed_sample_carousel-level6` | 2 | 3.0 | 6 | `1`(3), `2`(3) |
| | `pipetting_station` | 9 | 3.0 | 27 | `A3`(3), `B1`(3), `B2`(3), `B3`(3), `C1`(3), `C2`(3), `C3`(3), `D1`(3), `D2`(3) |
| | `transfer_stage` | 1 | 3.0 | 3 | `001`(3) |

#### solid_residue — 固体残留 (Solid Residue)

点位: 8 | 视角: 22 | 图片: 53

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **powder** | `analytical_balance` | 2 | 2.5 | 5 | `001`(2), `002`(3) |
| | `magnetic_stirrer_01` | 1 | 1.0 | 1 | `001`(1) |
| | `magnetic_stirrer_02` | 2 | 1.0 | 2 | `001`(1), `002`(1) |
| | `mixed_sample_carousel-level3` | 1 | 1.0 | 1 | `2`(1) |
| | `mixed_sample_carousel-level5` | 2 | 1.0 | 2 | `1`(1), `2`(1) |
| | `mixed_sample_carousel-level6` | 2 | 1.0 | 2 | `1`(1), `2`(1) |
| | `pipetting_station` | 10 | 3.7 | 37 | `A3`(3), `B1`(4), `B2`(4), `B3`(4), `C1`(4), `C2`(4), `C3`(4), `D1`(2), `D2`(4), `D3`(4) |
| | `transfer_stage` | 2 | 1.5 | 3 | `001`(1), `002`(2) |

#### stain — 污渍 (Stain)

点位: 8 | 视角: 24 | 图片: 44

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **pigment_stain** | `analytical_balance` | 2 | 3.0 | 6 | `001`(4), `002`(2) |
| | `magnetic_stirrer_01` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `magnetic_stirrer_02` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `mixed_sample_carousel-level3` | 2 | 1.0 | 2 | `2`(1), `3`(1) |
| | `mixed_sample_carousel-level5` | 2 | 1.0 | 2 | `1`(1), `2`(1) |
| | `mixed_sample_carousel-level6` | 2 | 1.0 | 2 | `1`(1), `2`(1) |
| | `pipetting_station` | 10 | 2.0 | 20 | `A3`(2), `B1`(2), `B2`(2), `B3`(2), `C1`(2), `C2`(2), `C3`(2), `D1`(2), `D2`(2), `D3`(2) |
| | `transfer_stage` | 2 | 2.0 | 4 | `001`(2), `002`(2) |

### multiwell_plate_96_model_01 — multiwell_plate_96_model_01 (96孔板模型1)

**点位: 8 | 视角: 241 | 图片: 599**

#### damage — 主体破损 (Damage)

点位: 8 | 视角: 30 | 图片: 64

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **crack** | `analytical_balance` | 1 | 1.0 | 1 | `002`(1) |
| | `magnetic_stirrer_01` | 1 | 1.0 | 1 | `001`(1) |
| | `magnetic_stirrer_02` | 1 | 1.0 | 1 | `001`(1) |
| | `mixed_sample_carousel-level3` | 2 | 1.0 | 2 | `2`(1), `3`(1) |
| | `mixed_sample_carousel-level5` | 2 | 1.0 | 2 | `1`(1), `2`(1) |
| | `mixed_sample_carousel-level6` | 2 | 1.0 | 2 | `1`(1), `2`(1) |
| | `transfer_stage` | 1 | 1.0 | 1 | `002`(1) |
| **cracked_lid** | `analytical_balance` | 2 | 3.0 | 6 | `001`(4), `002`(2) |
| | `magnetic_stirrer_01` | 1 | 6.0 | 6 | `001`(6) |
| | `magnetic_stirrer_02` | 1 | 1.0 | 1 | `002`(1) |
| | `mixed_sample_carousel-level3` | 2 | 1.0 | 2 | `2`(1), `3`(1) |
| | `mixed_sample_carousel-level5` | 2 | 1.0 | 2 | `1`(1), `2`(1) |
| | `mixed_sample_carousel-level6` | 2 | 1.0 | 2 | `1`(1), `2`(1) |
| | `pipetting_station` | 9 | 3.7 | 33 | `A3`(4), `B1`(4), `B2`(4), `B3`(4), `C1`(2), `C2`(4), `D1`(3), `D2`(4), `D3`(4) |
| | `transfer_stage` | 1 | 2.0 | 2 | `002`(2) |

#### label_anomaly — 标签异常 (Label Anomaly)

点位: 8 | 视角: 47 | 图片: 122

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **label_damage** | `analytical_balance` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `magnetic_stirrer_01` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `magnetic_stirrer_02` | 1 | 2.0 | 2 | `002`(2) |
| | `mixed_sample_carousel-level3` | 2 | 1.0 | 2 | `2`(1), `3`(1) |
| | `mixed_sample_carousel-level5` | 2 | 1.0 | 2 | `1`(1), `2`(1) |
| | `mixed_sample_carousel-level6` | 1 | 1.0 | 1 | `2`(1) |
| | `pipetting_station` | 10 | 2.0 | 20 | `A3`(2), `B1`(2), `B2`(2), `B3`(2), `C1`(2), `C2`(2), `C3`(2), `D1`(2), `D2`(2), `D3`(2) |
| | `transfer_stage` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| **label_detachment** | `analytical_balance` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `magnetic_stirrer_01` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `magnetic_stirrer_02` | 2 | 3.0 | 6 | `001`(2), `002`(4) |
| | `mixed_sample_carousel-level3` | 2 | 4.0 | 8 | `2`(4), `3`(4) |
| | `mixed_sample_carousel-level5` | 2 | 4.0 | 8 | `1`(4), `2`(4) |
| | `mixed_sample_carousel-level6` | 2 | 4.5 | 9 | `1`(5), `2`(4) |
| | `pipetting_station` | 10 | 3.8 | 38 | `A3`(4), `B1`(2), `B2`(4), `B3`(4), `C1`(4), `C2`(4), `C3`(4), `D1`(4), `D2`(4), `D3`(4) |
| | `transfer_stage` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| **label_soiling** | `magnetic_stirrer_02` | 1 | 2.0 | 2 | `001`(2) |

#### lid_anomaly — 盖子异常 (Lid Anomaly)

点位: 8 | 视角: 46 | 图片: 150

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **incorrect_lid** | `analytical_balance` | 2 | 5.0 | 10 | `001`(5), `002`(5) |
| | `magnetic_stirrer_01` | 2 | 4.0 | 8 | `001`(3), `002`(5) |
| | `magnetic_stirrer_02` | 2 | 5.0 | 10 | `001`(5), `002`(5) |
| | `mixed_sample_carousel-level3` | 2 | 5.0 | 10 | `2`(5), `3`(5) |
| | `mixed_sample_carousel-level5` | 1 | 5.0 | 5 | `1`(5) |
| | `mixed_sample_carousel-level6` | 2 | 3.5 | 7 | `1`(3), `2`(4) |
| | `pipetting_station` | 10 | 4.9 | 49 | `A3`(5), `B1`(5), `B2`(5), `B3`(5), `C1`(5), `C2`(4), `C3`(5), `D1`(5), `D2`(5), `D3`(5) |
| | `transfer_stage` | 2 | 5.0 | 10 | `001`(5), `002`(5) |
| **missing_lid** | `analytical_balance` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `magnetic_stirrer_01` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `magnetic_stirrer_02` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `mixed_sample_carousel-level3` | 2 | 1.0 | 2 | `2`(1), `3`(1) |
| | `mixed_sample_carousel-level5` | 1 | 1.0 | 1 | `1`(1) |
| | `mixed_sample_carousel-level6` | 2 | 1.0 | 2 | `1`(1), `2`(1) |
| | `pipetting_station` | 10 | 2.0 | 20 | `A3`(2), `B1`(2), `B2`(2), `B3`(2), `C1`(2), `C2`(2), `C3`(2), `D1`(2), `D2`(2), `D3`(2) |
| | `transfer_stage` | 2 | 2.0 | 4 | `001`(2), `002`(2) |

#### liquid_residue — 液体残留 (Liquid Residue)

点位: 8 | 视角: 24 | 图片: 42

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **colored_clear_liquid** | `analytical_balance` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `magnetic_stirrer_01` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `magnetic_stirrer_02` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `mixed_sample_carousel-level3` | 2 | 1.0 | 2 | `2`(1), `3`(1) |
| | `mixed_sample_carousel-level5` | 2 | 1.0 | 2 | `1`(1), `2`(1) |
| | `mixed_sample_carousel-level6` | 2 | 1.0 | 2 | `1`(1), `2`(1) |
| | `pipetting_station` | 10 | 2.0 | 20 | `A3`(2), `B1`(2), `B2`(2), `B3`(2), `C1`(2), `C2`(2), `C3`(2), `D1`(2), `D2`(2), `D3`(2) |
| | `transfer_stage` | 2 | 2.0 | 4 | `001`(2), `002`(2) |

#### normal — 正常 (Normal)

点位: 8 | 视角: 24 | 图片: 42

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **(same)** | `analytical_balance` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `magnetic_stirrer_01` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `magnetic_stirrer_02` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `mixed_sample_carousel-level3` | 2 | 1.0 | 2 | `2`(1), `3`(1) |
| | `mixed_sample_carousel-level5` | 2 | 1.0 | 2 | `1`(1), `2`(1) |
| | `mixed_sample_carousel-level6` | 2 | 1.0 | 2 | `1`(1), `2`(1) |
| | `pipetting_station` | 10 | 2.0 | 20 | `A3`(2), `B1`(2), `B2`(2), `B3`(2), `C1`(2), `C2`(2), `C3`(2), `D1`(2), `D2`(2), `D3`(2) |
| | `transfer_stage` | 2 | 2.0 | 4 | `001`(2), `002`(2) |

#### placement_error — 摆放错误 (Placement Error)

点位: 8 | 视角: 23 | 图片: 69

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **tilted_placement** | `analytical_balance` | 2 | 3.0 | 6 | `001`(3), `002`(3) |
| | `magnetic_stirrer_01` | 2 | 3.0 | 6 | `001`(3), `002`(3) |
| | `magnetic_stirrer_02` | 2 | 3.0 | 6 | `001`(3), `002`(3) |
| | `mixed_sample_carousel-level3` | 2 | 3.0 | 6 | `2`(3), `3`(3) |
| | `mixed_sample_carousel-level5` | 1 | 3.0 | 3 | `1`(3) |
| | `mixed_sample_carousel-level6` | 2 | 3.0 | 6 | `1`(3), `2`(3) |
| | `pipetting_station` | 10 | 3.0 | 30 | `A3`(3), `B1`(3), `B2`(3), `B3`(3), `C1`(3), `C2`(3), `C3`(3), `D1`(3), `D2`(3), `D3`(3) |
| | `transfer_stage` | 2 | 3.0 | 6 | `001`(3), `002`(3) |

#### solid_residue — 固体残留 (Solid Residue)

点位: 8 | 视角: 24 | 图片: 70

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **powder** | `analytical_balance` | 2 | 3.0 | 6 | `001`(2), `002`(4) |
| | `magnetic_stirrer_01` | 2 | 3.0 | 6 | `001`(4), `002`(2) |
| | `magnetic_stirrer_02` | 2 | 3.0 | 6 | `001`(2), `002`(4) |
| | `mixed_sample_carousel-level3` | 2 | 1.0 | 2 | `2`(1), `3`(1) |
| | `mixed_sample_carousel-level5` | 2 | 1.0 | 2 | `1`(1), `2`(1) |
| | `mixed_sample_carousel-level6` | 2 | 1.0 | 2 | `1`(1), `2`(1) |
| | `pipetting_station` | 10 | 3.8 | 38 | `A3`(4), `B1`(4), `B2`(4), `B3`(4), `C1`(2), `C2`(4), `C3`(4), `D1`(4), `D2`(4), `D3`(4) |
| | `transfer_stage` | 2 | 4.0 | 8 | `001`(4), `002`(4) |

#### stain — 污渍 (Stain)

点位: 8 | 视角: 23 | 图片: 40

| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |
|---|---|---|---|---|---|
| **pigment_stain** | `analytical_balance` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `magnetic_stirrer_01` | 2 | 2.0 | 4 | `001`(2), `002`(2) |
| | `magnetic_stirrer_02` | 1 | 2.0 | 2 | `001`(2) |
| | `mixed_sample_carousel-level3` | 2 | 1.0 | 2 | `2`(1), `3`(1) |
| | `mixed_sample_carousel-level5` | 2 | 1.0 | 2 | `1`(1), `2`(1) |
| | `mixed_sample_carousel-level6` | 2 | 1.0 | 2 | `1`(1), `2`(1) |
| | `pipetting_station` | 10 | 2.0 | 20 | `A3`(2), `B1`(2), `B2`(2), `B3`(2), `C1`(2), `C2`(2), `C3`(2), `D1`(2), `D2`(2), `D3`(2) |
| | `transfer_stage` | 2 | 2.0 | 4 | `001`(2), `002`(2) |

---

*Report generated by analyze_final.py*
