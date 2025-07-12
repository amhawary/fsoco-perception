import os
import cv2
import matplotlib.pyplot as plt
from collections import defaultdict
import yaml
import torch
from ultralytics import YOLO

torch.cuda.empty_cache()

dataset = "/home/isaac/Documents/fsoco-perception/dataset02"

def load_class_names(yaml_path):
    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)
    # Handle both list or dict formats
    if isinstance(data['names'], dict):
        class_names = [data['names'][i] for i in sorted(data['names'])]
    else:
        class_names = data['names']
    return class_names

IMAGE_DIR = f'{dataset}/val/images'
LABEL_DIR = f'{dataset}/val/labels'

YAML_PATH = f'{dataset}/data.yaml'  # or wherever your .yaml file is
CLASS_NAMES = load_class_names(YAML_PATH)
print(CLASS_NAMES)

class_counts = defaultdict(int)
class_examples = defaultdict(list)

# Parse annotations and collect counts + examples
for label_file in os.listdir(LABEL_DIR):
    if not label_file.endswith('.txt'):
        continue
    label_path = os.path.join(LABEL_DIR, label_file)
    image_name = os.path.splitext(label_file)[0] + '.jpg'
    image_path = os.path.join(IMAGE_DIR, image_name)

    if not os.path.exists(image_path):
        continue

    with open(label_path, 'r') as f:
        for line in f:
            cls_id = int(line.strip().split()[0])
            class_counts[cls_id] += 1
            if len(class_examples[cls_id]) < 3:
                class_examples[cls_id].append((image_path, line.strip()))

total_cones = 0
for c in class_counts: 
    total_cones += class_counts[c] 

for i, cls in enumerate(CLASS_NAMES):
    print(f"Class {i} - {cls}: {class_counts[i]} occurences ({round(class_counts[i]/total_cones, 2)*100}%)")

print(f"Total: {total_cones}")

model = YOLO("yolo11s.pt")

# Train with small batch size and limited workers
# for next run lower the saturation range
results = model.train(
    data='/home/isaac/Documents/fsoco-perception/dataset02/data.yaml',
    epochs=400,
    imgsz=1080,    
    batch=0.9,
    patience= 10,
    name = "yolov11s(mk.4)",
    save_period = 10,
    workers=15,         # Avoid multiprocessing overhead
    device=0,           # Make sure it uses the GPU
    hsv_h = 0.015,
    hsv_s = 0.1,
    hsv_v = 0.2,
    degrees = 12.0,
    translate = 0.15,
    scale = 0.0,
    shear = 5.0,
    perspective = 0.0,
    flipud = 0.0,
    fliplr = 0.5,
    mosaic = 0.5,
    mixup = 0.0,
    # cutmix = 0.25
)

model.export()

metrics = model.val(data="dataset02/data.yaml", split='test')  # uses test images

# Optional: print metrics
print(metrics.box.map)      # mAP@0.5:0.95
print(metrics.box.map50)    # mAP@0.5

print(metrics.box.p)
print(metrics.box.r)