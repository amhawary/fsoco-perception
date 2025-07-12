import os
import cv2
import matplotlib.pyplot as plt
from collections import defaultdict
import yaml
import torch
from ultralytics import YOLO

dataset = "/home/isaac/Documents/fsoco-perception/dataset02"

model = YOLO("/home/isaac/Documents/fsoco-perception/runs/detect/yolov8s(mk.3)3/weights/best.pt")

metrics = model.val(data="/home/isaac/Documents/fsoco-perception/dataset02/data.yaml", split='test')