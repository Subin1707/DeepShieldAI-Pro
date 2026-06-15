# DeepShield AI Pro - ML Architecture

```text
Image / Video
  -> Frame Extraction
  -> Face Detection
  -> EfficientNet-B0
  -> Attention Mechanism
  -> REAL / FAKE Classification
  -> Grad-CAM
  -> Metadata Forensics + FFT Frequency + AI Artifact Detection
  -> Face Embedding Similarity
  -> Risk Score
  -> Gemini/Groq AI Explanation
```

## Implemented Components

- **Grad-CAM**: the backend tries to generate a true Grad-CAM heatmap from the loaded Keras image model. If TensorFlow or a compatible model is not available, it falls back to the existing saliency heatmap so the demo remains usable.
- **Attention Mechanism**: the EfficientNet training script now adds a spatial attention layer after the EfficientNet-B0 feature map and before global average pooling.
- **Face Embedding Similarity**: video analysis computes lightweight face embeddings for consecutive face crops and measures cosine similarity between them.
- **Hybrid AI-generated Forensics**: image/video analysis now adds Metadata/EXIF checks, FFT frequency analysis, and AI artifact heuristics before final fusion risk scoring.
- **Risk Scoring + AI Explanation**: the final result combines prediction confidence, temporal statistics, suspicious regions, similarity signals, and the generated report/chatbot context. Set `CHATBOT_PROVIDER=gemini` to use Gemini, or keep the default Groq provider.

## Algorithm List

1. Haar Cascade Face Detection
2. EfficientNet-B0
3. Transfer Learning
4. Spatial Attention Mechanism
5. Grad-CAM
6. Face Embedding Similarity
7. Cosine Similarity
8. Metadata Forensics
9. FFT Frequency Analysis
10. AI Artifact Detection
11. Fusion Risk Scoring
12. Gemini/Groq AI Explanation

## Demo Signals

- Original face crop and Grad-CAM/saliency heatmap are shown through `heatmapUrl`.
- `heatmapMethod` indicates whether the result used `grad_cam` or `saliency_fallback`.
- `embeddingSimilarity` contains mean similarity, minimum similarity, maximum similarity drop, suspicious transition ratio, and the top suspicious frame transitions.
