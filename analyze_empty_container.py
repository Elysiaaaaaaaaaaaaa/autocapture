import os
from collections import defaultdict

ROOT = r'D:\myproject\2026.7research\dataset\empty_container'

# Structure: container -> anomaly_cat -> anomaly_subcat -> position -> {angles: [], shape_counts: []}
result = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {'angles': [], 'shape_counts': []}))))

for dirpath, dirnames, filenames in os.walk(ROOT):
    png_files = [f for f in filenames if f.lower().endswith('.png')]
    if not png_files:
        continue

    rel_path = os.path.relpath(dirpath, ROOT)
    parts = rel_path.replace('\\', '/').split('/')

    if len(parts) < 4:
        continue

    container = parts[0]
    anomaly_cat = parts[1]
    anomaly_subcat = parts[2]
    scene_angle = parts[3]

    # Split into position and angle (last dash)
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

# Display name mappings
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

grand_positions = set()
grand_view_angle_count = 0
grand_total_images = 0

print('=' * 130)
print('  empty_container 数据集统计报告')
print('  (层级: 目标种类 → 异常大类 → 异常小类 → 点位 → 视角/形态)')
print('=' * 130)
print(f'  容器种类: {len(result)} 种')
print()

for container in sorted(result.keys()):
    cdata = result[container]
    cname = container_names.get(container, container)

    # Count per container
    c_view_angles = 0
    c_images = 0
    c_positions = set()

    for acat in cdata:
        for asubcat in cdata[acat]:
            for pos in cdata[acat][asubcat]:
                pd = cdata[acat][asubcat][pos]
                c_positions.add(pos)
                for sc in pd['shape_counts']:
                    c_view_angles += 1
                    c_images += sc

    print(f'  {"-" * 125}')
    print(f'  【{container}】{cname}')
    print(f'      位置(点位)数: {len(c_positions)} | 视角总数: {c_view_angles} | 图片总数: {c_images}')
    print()

    for acat in sorted(cdata.keys()):
        cat_display = cat_names.get(acat, acat)
        subcats = cdata[acat]

        cat_positions = set()
        cat_angles = 0
        cat_images = 0
        for asubcat in subcats:
            for pos in subcats[asubcat]:
                pd = subcats[asubcat][pos]
                cat_positions.add(pos)
                for sc in pd['shape_counts']:
                    cat_angles += 1
                    cat_images += sc

        print(f'    ├─ 异常大类: {acat} {cat_display}')
        print(f'    │    位置数: {len(cat_positions)} | 视角数: {cat_angles} | 图片数: {cat_images}')

        subcat_keys = sorted(subcats.keys())
        for i, asubcat in enumerate(subcat_keys):
            is_last_subcat = (i == len(subcat_keys) - 1)
            prefix_sub = '    │  ' if not is_last_subcat else '       '
            branch_sub = '    └─' if is_last_subcat else '    ├─'

            subcat_data = subcats[asubcat]

            sc_positions = set()
            sc_angles = 0
            sc_images = 0
            for pos in subcat_data:
                pd = subcat_data[pos]
                sc_positions.add(pos)
                for s in pd['shape_counts']:
                    sc_angles += 1
                    sc_images += s

            print(f'    {branch_sub} 异常小类: {asubcat}')
            print(f'    {prefix_sub}   位置数: {len(sc_positions)} | 视角数: {sc_angles} | 图片数: {sc_images}')

            # Per position
            pos_items = sorted(subcat_data.items())
            for j, (pos, pd) in enumerate(pos_items):
                is_last_pos = (j == len(pos_items) - 1)
                branch_pos = '   └─' if is_last_pos else '   ├─'

                angle_list = pd['angles']
                shape_list = pd['shape_counts']

                total_shapes_at_pos = sum(shape_list)
                avg_shapes = total_shapes_at_pos / len(angle_list) if angle_list else 0

                # Build angle details
                angle_details = []
                for aidx, (ang, sc) in enumerate(zip(angle_list, shape_list)):
                    angle_details.append(f'{ang}({sc}张)')

                print(f'    {prefix_sub}{branch_pos} 点位: {pos}')
                print(f'    {prefix_sub}    视角数: {len(angle_list)} | 平均Shape数: {avg_shapes:.1f} | 小计图片: {total_shapes_at_pos}')
                print(f'    {prefix_sub}    视角详情: {", ".join(angle_details)}')

            if not is_last_subcat:
                print(f'    {prefix_sub}')

        print()

    grand_positions.update(c_positions)
    grand_view_angle_count += c_view_angles
    grand_total_images += c_images

print('  ' + '=' * 125)
print(f'  【总计】')
print(f'    容器种类: {len(result)}')
print(f'    去重点位数: {len(grand_positions)}')
print(f'    视角总数: {grand_view_angle_count}')
print(f'    图片总数: {grand_total_images}')
print('  ' + '=' * 125)
