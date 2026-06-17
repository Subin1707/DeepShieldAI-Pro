#!/usr/bin/env python3
"""Debug script to test Grad-CAM functionality"""

import sys
import os
import logging
from pathlib import Path

# Setup path
sys.path.insert(0, str(Path(__file__).parent / "backend"))
os.chdir(str(Path(__file__).parent / "backend"))

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    # Check TensorFlow
    import tensorflow as tf
    logger.info(f"✓ TensorFlow: {tf.__version__}")
except ImportError as e:
    logger.error(f"✗ TensorFlow not found: {e}")
    sys.exit(1)

try:
    # Check OpenCV
    import cv2
    logger.info(f"✓ OpenCV: {cv2.__version__}")
except ImportError as e:
    logger.error(f"✗ OpenCV not found: {e}")
    sys.exit(1)

try:
    # Import app modules
    from app.core.config import settings
    from app.ai.model_loader import load_deepfake_model
    from app.ai.preprocess import preprocess_image_file
    from app.ai.face_detector import detect_largest_face
    from app.services.gradcam_service import make_gradcam_heatmap, _build_saliency_map
    import numpy as np
    
    logger.info("✓ App imports successful")
except ImportError as e:
    logger.error(f"✗ App import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test image path
test_image = Path("storage/faces").glob("*.jpg")
test_images = list(test_image)

if not test_images:
    logger.warning("No test images found in storage/faces/")
    # Try uploads
    test_image = Path("storage/uploads").glob("*")
    test_images = list(test_image)

if not test_images:
    logger.error("No test images found. Please run an analysis first.")
    sys.exit(1)

test_path = str(test_images[0])
logger.info(f"Testing with: {test_path}")

# Test 1: Load model
logger.info("\n=== Test 1: Loading Model ===")
try:
    loaded = load_deepfake_model()
    if loaded is None:
        logger.error("✗ Model loading returned None")
        sys.exit(1)
    logger.info(f"✓ Model loaded: backend={loaded.backend}")
    
    if loaded.backend != "keras":
        logger.error(f"✗ Model backend is {loaded.backend}, not keras")
        sys.exit(1)
    
    model = loaded.model
    logger.info(f"✓ Keras model found")
    logger.info(f"  Model layers: {len(model.layers)}")
    
    # Check conv layers
    conv_layers = [layer for layer in model.layers if 'conv' in layer.name.lower()]
    logger.info(f"  Conv layers: {[l.name for l in conv_layers]}")
    
except Exception as e:
    logger.error(f"✗ Model loading failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Preprocess
logger.info("\n=== Test 2: Image Preprocessing ===")
try:
    img_array = preprocess_image_file(test_path)
    logger.info(f"✓ Preprocessing successful")
    logger.info(f"  Shape: {img_array.shape}")
    logger.info(f"  Dtype: {img_array.dtype}")
    logger.info(f"  Range: [{img_array.min():.4f}, {img_array.max():.4f}]")
except Exception as e:
    logger.error(f"✗ Preprocessing failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Grad-CAM
logger.info("\n=== Test 3: Grad-CAM Generation ===")
try:
    heatmap = make_gradcam_heatmap(img_array, model, "top_conv")
    logger.info(f"✓ Grad-CAM successful with 'top_conv'")
    logger.info(f"  Shape: {heatmap.shape}")
    logger.info(f"  Range: [{heatmap.min():.4f}, {heatmap.max():.4f}]")
except Exception as e:
    logger.error(f"✗ Grad-CAM failed with 'top_conv': {e}")
    
    # Try auto-detection
    logger.info("  Trying auto-detection of conv layer...")
    try:
        from app.services.gradcam_service import _find_last_conv_layer_name
        auto_layer = _find_last_conv_layer_name(model)
        logger.info(f"  Auto-detected layer: {auto_layer}")
        
        if auto_layer:
            heatmap = make_gradcam_heatmap(img_array, model, auto_layer)
            logger.info(f"✓ Grad-CAM successful with '{auto_layer}'")
            logger.info(f"  Shape: {heatmap.shape}")
            logger.info(f"  Range: [{heatmap.min():.4f}, {heatmap.max():.4f}]")
        else:
            logger.error("  No conv layer found")
    except Exception as e2:
        logger.error(f"  Auto-detection also failed: {e2}")

# Test 4: Saliency Fallback
logger.info("\n=== Test 4: Saliency Fallback ===")
try:
    img = cv2.imread(test_path)
    if img is None:
        raise ValueError(f"Could not read image: {test_path}")
    
    saliency = _build_saliency_map(img)
    logger.info(f"✓ Saliency map successful")
    logger.info(f"  Shape: {saliency.shape}")
    logger.info(f"  Range: [{saliency.min()}, {saliency.max()}]")
except Exception as e:
    logger.error(f"✗ Saliency fallback failed: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Face detection
logger.info("\n=== Test 5: Face Detection ===")
try:
    img = cv2.imread(test_path)
    if img is None:
        raise ValueError(f"Could not read image: {test_path}")
    
    face_box = detect_largest_face(img)
    if face_box:
        logger.info(f"✓ Face detected: {face_box}")
    else:
        logger.warning("⚠ No face detected (will use fallback)")
except Exception as e:
    logger.error(f"✗ Face detection failed: {e}")
    import traceback
    traceback.print_exc()

logger.info("\n=== Debugging Complete ===")
