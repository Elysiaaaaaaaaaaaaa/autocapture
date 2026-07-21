import os
from collections import defaultdict

ROOT = r'D:\myproject\2026.7research\dataset\empty_container'

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
    last_dash = scene_angle.rfind('-')
    position = scene_angle[:last_dash] if last_dash != -1 else scene_angle
    angle = scene_angle[last_dash + 1:] if last_dash != -1 else '?'
    shape_count = len(png_files)
    pos_data = result[container][anomaly_cat][anomaly_subcat]
    if position not in pos_data:
        pos_data[position] = {'angles': [], 'shape_counts': []}
    pos_data[position]['angles'].append(angle)
    pos_data[position]['shape_counts'].append(shape_count)

# ============ SUMMARY TABLE ============
print()
print('=' * 140)
print('  empty_container SUMMARY TABLE')
print('  Level: Container -> Anomaly Category -> Anomaly Subcategory -> Position -> View/Shape')
print('=' * 140)
print(f'{"Container":<28s} {"Anomaly Category":<24s} {"Anomaly Subcategory":<30s} {"Pos":>4s} {"Views":>6s} {"Images":>7s}')
print('-' * 140)

grand_pos_all = set()
grand_views = 0
grand_imgs = 0

for container in sorted(result.keys()):
    cdata = result[container]
    for acat in sorted(cdata.keys()):
        subcats = cdata[acat]
        for asubcat in sorted(subcats.keys()):
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
            grand_pos_all.update(sc_positions)
            grand_views += sc_angles
            grand_imgs += sc_images
            print(f'{container:<28s} {acat:<24s} {asubcat:<30s} {len(sc_positions):>4d} {sc_angles:>6d} {sc_images:>7d}')

print('-' * 140)
print(f'{"TOTAL (7 containers)":<28s} {"":<24s} {"":<30s} {len(grand_pos_all):>4d} {grand_views:>6d} {grand_imgs:>7d}')
print('=' * 140)

# ============ PER-CONTAINER SUMMARY ============
print()
print('=' * 120)
print('  PER-CONTAINER SUMMARY')
print('=' * 120)
print(f'{"Container":<30s} {"Positions":>10s} {"View Angles":>12s} {"Images":>8s} {"Anomaly Cats":>13s}')
print('-' * 120)
for container in sorted(result.keys()):
    cdata = result[container]
    c_positions = set()
    c_views = 0
    c_imgs = 0
    cats = set()
    for acat in cdata:
        cats.add(acat)
        for asubcat in cdata[acat]:
            for pos in cdata[acat][asubcat]:
                pd = cdata[acat][asubcat][pos]
                c_positions.add(pos)
                for s in pd['shape_counts']:
                    c_views += 1
                    c_imgs += s
    print(f'{container:<30s} {len(c_positions):>10d} {c_views:>12d} {c_imgs:>8d} {len(cats):>13d}')
print('-' * 120)

# ============ ALL POSITIONS ============
print()
print('=' * 80)
print('  ALL UNIQUE POSITIONS (across all containers)')
print('=' * 80)
all_positions_global = set()
for container in result:
    for acat in result[container]:
        for asubcat in result[container][acat]:
            for pos in result[container][acat][asubcat]:
                all_positions_global.add(pos)
for i, p in enumerate(sorted(all_positions_global), 1):
    print(f'  {i:>2d}. {p}')
print(f'  Total: {len(all_positions_global)} unique positions')

# ============ ANOMALY CATEGORY CROSS-CONTAINER ============
print()
print('=' * 120)
print('  ANOMALY CATEGORY COVERAGE ACROSS CONTAINERS')
print('=' * 120)
all_cats = set()
for container in result:
    for acat in result[container]:
        all_cats.add(acat)

header = f'{"Anomaly Category":<30s}'
for c in sorted(result.keys()):
    header += f'{c[:12]:>14s}'
print(header)
print('-' * len(header))

for acat in sorted(all_cats):
    row = f'{acat:<30s}'
    for c in sorted(result.keys()):
        if acat in result[c]:
            subcats = result[c][acat]
            total_imgs = 0
            for asubcat in subcats:
                for pos in subcats[asubcat]:
                    pd = subcats[asubcat][pos]
                    for s in pd['shape_counts']:
                        total_imgs += s
            row += f'{total_imgs:>14d}'
        else:
            row += f'{"-":>14s}'
    print(row)
