#!/usr/bin/env python3
"""Test fixed Grad-CAM"""
import sys
import os
from pathlib import Path

backend_dir = Path(__file__).parent / "backend"
os.chdir(backend_dir)
sys.path.insert(0, str(backend_dir))

from app.services.gradcam_service import make_gradcam_heatmap
from app.ai.model_loader import load_deepfake_model
from app.ai.preprocess import preprocess_image_file
import numpy as np

print("Loading model...")
m = load_deepfake_model()

print("Preprocessing image...")
img = preprocess_image_file('storage/faces/ANL-20260618-73E3B292_face_1.jpg')

print("Computing Grad-CAM...")
hm = make_gradcam_heatmap(img, m.model, 'efficientnetb0')

print('[OK] Grad-CAM Test:')
print(f'  Result: {hm is not None}')
if hm is not None:
    print(f'  Shape: {hm.shape}')
    print(f'  Min: {hm.min():.6f}, Max: {hm.max():.6f}')
    print(f'  Non-zero count: {np.count_nonzero(hm)}')
    print(f'  Mean: {hm.mean():.6f}')
else:
    print('  Grad-CAM returned None (will use saliency fallback)')

# Also test full pipeline
print("\nTesting full heatmap generation pipeline...")
from app.services.gradcam_service import generate_saliency_heatmap

result = generate_saliency_heatmap('storage/faces/ANL-20260618-73E3B292_face_1.jpg', 'TEST-GRADCAM')
print('[OK] Full pipeline result:')
print(f'  Method: {result.get("method")}')
print(f'  Regions found: {len(result.get("regions", []))}')
print(f'  Face detected: {result.get("faceDetected")}')

