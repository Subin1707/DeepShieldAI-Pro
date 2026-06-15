# DeepShield AI Pro - Demo Script

1. Upload an image or video from the Upload page.
2. Wait for frame extraction, face detection, model inference, heatmap generation, and report generation.
3. On the Result page, explain the main verdict: REAL/FAKE, confidence, risk score, and risk level.
4. Open the heatmap panel:
   - If `heatmapMethod = grad_cam`, explain that Grad-CAM highlights the regions most influential for the FAKE class.
   - If `heatmapMethod = saliency_fallback`, explain that the demo is using an image-forensics fallback because a compatible Keras model is not available.
5. For video, open the advanced analysis panel:
   - Mean similarity close to 1 means consecutive face crops are stable.
   - Low minimum similarity or a high similarity drop means the face changes unusually between frames.
   - Suspicious transitions indicate frame pairs that should be reviewed manually.
6. Use the AI report/chatbot to summarize the model result, Grad-CAM regions, temporal statistics, and face embedding similarity.
