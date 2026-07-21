import os
from collections import defaultdict

ROOT = r'D:\myproject\2026.7research\dataset\empty_container'
OUTPUT = r'D:\myproject\2026.7research\autocapture\autocapture\empty_container_report.md'

# result[container][anomaly_cat][anomaly_subcat][position] = {'angles': [...], 'shape_counts': [...]}
result = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {'angles': [], 'shape_counts': []}))))

for dirpath, dirnames, filenames in os.walk(ROOT):
    png_files = [f for f in filenames if f.lower().endswith('.png')]
    if not png_files:
        continue

    rel_path = os.path.relpath(dirpath, ROOT)
    parts = rel_path.replace('\\', '/').split('/')

    if len(parts) == 3:
        container = parts[0]
        anomaly_cat = parts[1]
        anomaly_subcat = parts[1]
        scene_angle = parts[2]
    elif len(parts) >= 4:
        container = parts[0]
        anomaly_cat = parts[1]
        anomaly_subcat = parts[2]
        scene_angle = parts[3]
    else:
        continue

    last_dash = scene_angle.rfind('-')
    if last_dash == -1:
        position = scene_angle
        angle = '?'
    else:
        position = scene_angle[:last_dash]
        angle = scene_angle[last_dash + 1:]

    shape_count = len(png_files)
    pos_data = result[container][anomaly_cat][anomaly_subcat]
    if position not in pos_data:
        pos_data[position] = {'angles': [], 'shape_counts': []}
    pos_data[position]['angles'].append(angle)
    pos_data[position]['shape_counts'].append(shape_count)


lines = []

def w(s=''):
    lines.append(s)

cat_names = {
    'normal': '正常 (Normal)',
    'damage': '主体破损 (Damage)',
    'foreign_object_residue': '异物残留 (Foreign Object Residue)',
    'label_anomaly': '标签异常 (Label Anomaly)',
    'liquid_residue': '液体残留 (Liquid Residue)',
    'powder_residue': '粉末残留 (Powder Residue)',
    'stain': '污渍 (Stain)',
    'lid_anomaly': '盖子异常 (Lid Anomaly)',
    'placement_error': '摆放错误 (Placement Error)',
    'solid_residue': '固体残留 (Solid Residue)',
}

container_names = {
    'beaker': 'beaker (烧杯)',
    'liquid_reservoir': 'liquid_reservoir (贮液器)',
    'multiwell_plate_06': 'multiwell_plate_06 (6孔板)',
    'multiwell_plate_11': 'multiwell_plate_11 (11孔板)',
    'multiwell_plate_24': 'multiwell_plate_24 (24孔板)',
    'multiwell_plate_48': 'multiwell_plate_48 (48孔板)',
    'multiwell_plate_96_model_01': 'multiwell_plate_96_model_01 (96孔板模型1)',
}

# ==================== TITLE ====================
w('# empty_container 数据集统计报告')
w()
w(f'> **数据集路径:** `{ROOT}`')
w('>')
w('> **层级:** 目标种类 → 异常大类 → 异常小类 → 点位 → 视角/形态')
w('>')
w('> **viewRULE.txt 规则:** 文件夹命名 = `点位-视角编号`，每个视角文件夹内的图片数 = shape数量，')
w('> 某个点位的小计 = 视角数 × 平均shape数')
w()
w('---')
w()

# ==================== GRAND TOTAL TABLE ====================
w('## 📊 总览')
w()

grand_positions = set()
grand_view_angles = 0
grand_total_images = 0

container_stats = {}
for container in sorted(result.keys()):
    cdata = result[container]
    c_positions = set()
    c_views = 0
    c_images = 0
    cats = set()
    for acat in cdata:
        cats.add(acat)
        for asubcat in cdata[acat]:
            for pos in cdata[acat][asubcat]:
                pd = cdata[acat][asubcat][pos]
                c_positions.add(pos)
                for sc in pd['shape_counts']:
                    c_views += 1
                    c_images += sc
    container_stats[container] = (c_positions, c_views, c_images, cats)
    grand_positions.update(c_positions)
    grand_view_angles += c_views
    grand_total_images += c_images

w('| 指标 | 数值 |')
w('|---|---|')
w(f'| 目标种类（容器类型） | **{len(result)}** |')
w(f'| 去重点位 | **{len(grand_positions)}** |')
w(f'| 视角总数 | **{grand_view_angles}** |')
w(f'| 图片总数 | **{grand_total_images}** |')
w()

# ==================== PER-CONTAINER SUMMARY ====================
w('## 📦 各容器汇总')
w()
w(f'| 容器 | 点位 | 视角 | 图片 | 异常大类数 |')
w(f'|---|---|---|---|---|')
for container in sorted(result.keys()):
    cp, cv, ci, cats = container_stats[container]
    cname = container_names.get(container, container)
    w(f'| **{cname}** | {len(cp)} | {cv} | {ci} | {len(cats)} |')
w()

# ==================== ALL POSITIONS ====================
w('## 🗺️ 全部点位列表')
w()
w(f'共 **{len(grand_positions)}** 个去重点位：')
w()
all_pos_sorted = sorted(grand_positions)
for i, p in enumerate(all_pos_sorted, 1):
    w(f'{i:>2d}. `{p}`')
w()

# ==================== ANOMALY CATEGORY COVERAGE ====================
w('## 📋 异常大类 × 容器 覆盖矩阵（图片数）')
w()

all_cats = set()
for container in result:
    for acat in result[container]:
        all_cats.add(acat)

# Build matrix
containers_sorted = sorted(result.keys())
header = '| 异常大类 | ' + ' | '.join(c[:12] for c in containers_sorted) + ' |'
w(header)
sep = '|---|' + '|'.join(['---'] * len(containers_sorted)) + '|'
w(sep)

for acat in sorted(all_cats):
    cat_display = cat_names.get(acat, acat)
    row = f'| **{cat_display}** '
    for c in containers_sorted:
        if acat in result[c]:
            subcats = result[c][acat]
            total = 0
            for asubcat in subcats:
                for pos in subcats[asubcat]:
                    pd = subcats[asubcat][pos]
                    for s in pd['shape_counts']:
                        total += s
            row += f'| {total} '
        else:
            row += f'| - '
    row += '|'
    w(row)
w()

# ==================== DETAILED REPORT PER CONTAINER ====================
w('## 📖 详细层级报告')
w()
w('> 层级: 目标种类 → 异常大类 → 异常小类 → 点位 → 视角(shape数)')
w()

for container in sorted(result.keys()):
    cdata = result[container]
    cp, cv, ci, _ = container_stats[container]
    cname = container_names.get(container, container)

    w(f'### {container} — {cname}')
    w()
    w(f'**点位: {len(cp)} | 视角: {cv} | 图片: {ci}**')
    w()

    for acat in sorted(cdata.keys()):
        cat_display = cat_names.get(acat, acat)
        subcats = cdata[acat]

        cat_positions = set()
        cat_views = 0
        cat_images = 0
        for asubcat in subcats:
            for pos in subcats[asubcat]:
                pd = subcats[asubcat][pos]
                cat_positions.add(pos)
                for sc in pd['shape_counts']:
                    cat_views += 1
                    cat_images += sc

        w(f'#### {acat} — {cat_display}')
        w()
        w(f'点位: {len(cat_positions)} | 视角: {cat_views} | 图片: {cat_images}')
        w()

        # Table per anomaly category
        w('| 异常小类 | 点位 | 视角数 | 平均Shape | 小计图片 | 视角详情 |')
        w('|---|---|---|---|---|---|')

        for asubcat in sorted(subcats.keys()):
            subcat_data = subcats[asubcat]
            sc_views = 0
            sc_images = 0
            pos_details = []
            for pos in sorted(subcat_data.keys()):
                pd = subcat_data[pos]
                angle_list = pd['angles']
                shape_list = pd['shape_counts']
                pos_views = len(angle_list)
                pos_images = sum(shape_list)
                pos_avg = pos_images / pos_views if pos_views else 0
                sc_views += pos_views
                sc_images += pos_images
                angle_detail = ', '.join(f'`{a}`({s})' for a, s in zip(angle_list, shape_list))
                pos_details.append((pos, pos_views, pos_avg, pos_images, angle_detail))

            subcat_display = asubcat if asubcat != acat else '(same)'
            first = True
            for pos, pv, pa, pi, ad in pos_details:
                if first:
                    w(f'| **{subcat_display}** | `{pos}` | {pv} | {pa:.1f} | {pi} | {ad} |')
                    first = False
                else:
                    w(f'| | `{pos}` | {pv} | {pa:.1f} | {pi} | {ad} |')

        w()

# ==================== FOOTER ====================
w('---')
w()
w('*Report generated by analyze_final.py*')
w()

# Write to file
with open(OUTPUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print(f'Report written to: {OUTPUT}')
print(f'Total: {len(result)} containers, {len(grand_positions)} positions, {grand_view_angles} views, {grand_total_images} images')
