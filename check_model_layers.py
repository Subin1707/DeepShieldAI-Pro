#!/usr/bin/env python3
"""Check model architecture for Grad-CAM"""

import sys
import os
from pathlib import Path

# Change to backend directory
backend_dir = Path(__file__).parent / "backend"
os.chdir(backend_dir)
sys.path.insert(0, str(backend_dir))

from app.ai.model_loader import load_deepfake_model

loaded = load_deepfake_model()
if loaded is None:
    print("ERROR: Model loading failed")
    sys.exit(1)

model = loaded.model

print("=== Top-level Model Layers ===")
for i, layer in enumerate(model.layers):
    output_shape = getattr(getattr(layer, 'output', None), 'shape', None)
    print(f"{i}: {layer.name:40s} -> shape: {output_shape}")

print("\n=== EfficientNet Submodel ===")
try:
    effnet = model.get_layer('efficientnetb0')
    print(f"Type: {type(effnet)}")
    print(f"Has layers: {hasattr(effnet, 'layers')}")
    
    if hasattr(effnet, 'layers'):
        print(f"Total layers in EfficientNet: {len(effnet.layers)}")
        
        # Find conv layers
        conv_layers = []
        for layer in effnet.layers:
            output = getattr(layer, 'output', None)
            if output is not None:
                shape = getattr(output, 'shape', None)
                if shape and len(shape) == 4:
                    conv_layers.append(layer)
        
        print(f"Conv layers in EfficientNet: {len(conv_layers)}")
        
        # Print last 5 conv layers
        print("\nLast 5 conv layers:")
        for layer in conv_layers[-5:]:
            print(f"  {layer.name:50s} -> {layer.output.shape}")
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
