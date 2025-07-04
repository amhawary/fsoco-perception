import os
import glob
import yaml

# List of splits to process
splits = ['train', 'test', 'val']

# Updated class list for the new YAML file
class_names = [
    'orange_cone',
    'unknown_cone',
    'yellow_cone',
    'large_orange_cone',
    'blue_cone',
    'other'
]

# Remapping function
# meta.json order:
# 0: seg_orange_cone, 1: unknown_cone, 2: yellow_cone, 3: seg_large_orange_cone, 4: seg_blue_cone, 5: seg_unknown_cone, 6: seg_yellow_cone, 7: blue_cone, 8: orange_cone, 9: large_orange_cone
# We'll keep: orange_cone (8), unknown_cone (1), yellow_cone (2), large_orange_cone (9), blue_cone (7), other (everything else)
def remap_class_id(original_id):
    mapping = {8: 0, 1: 1, 2: 2, 9: 3, 7: 4}  # 0: orange, 1: unknown, 2: yellow, 3: large_orange, 4: blue
    return mapping.get(original_id, 5)  # 5 is 'other'

for split in splits:
    labels_dir = f'dataset02/{split}/labels'
    if not os.path.isdir(labels_dir):
        print(f"Skipping {split}: Directory not found: {labels_dir}")
        continue
    label_files = glob.glob(os.path.join(labels_dir, '**/*.txt'), recursive=True)
    print(f"[{split}] Found {len(label_files)} label files...")
    for file_path in label_files:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        new_lines = []
        for line in lines:
            parts = line.strip().split()
            if len(parts) == 5:
                class_id = int(parts[0])
                new_class_id = remap_class_id(class_id)
                coords = list(map(float, parts[1:]))
                new_line = f"{new_class_id} " + " ".join(f"{x:.6f}" for x in coords) + "\n"
                new_lines.append(new_line)
        with open(file_path, 'w') as f:
            f.writelines(new_lines)
    print(f"✅ [{split}] YOLO label files updated.")

# Write new YAML file
data_yaml = {
    'names': class_names,
    'nc': len(class_names),
    'train': 'train/images',
    'val': 'val/images',
    'test': 'test/images',
}
with open('dataset02/data_fixed.yaml', 'w') as f:
    yaml.dump(data_yaml, f, default_flow_style=False)
print("✅ New data_fixed.yaml written.")
