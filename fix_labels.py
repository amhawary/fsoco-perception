import os
import glob

# Set the path to your YOLO dataset annotations (e.g., labels/train/)
labels_dir = 'dataset02/val/labels'

# Make sure it's a valid directory
assert os.path.isdir(labels_dir), f"Directory not found: {labels_dir}"

# Remapping function
def remap_class_id(original_id):
    mapping = {7: 0, 2: 1, 8: 2, 9: 3}
    return mapping.get(original_id, 4)

# Process all .txt label files
label_files = glob.glob(os.path.join(labels_dir, '**/*.txt'), recursive=True)

print(f"Found {len(label_files)} label files...")

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

print("✅ All YOLO label files updated.")
