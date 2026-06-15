# DeepShieldAI-Pro

DeepShieldAI-Pro là đề tài xây dựng nền tảng web hỗ trợ phát hiện ảnh và video deepfake. Hệ thống cho phép người dùng tải lên media, trích xuất metadata, phát hiện khuôn mặt, chạy mô hình học sâu, kết hợp các kỹ thuật phân tích pháp chứng số, trực quan hóa vùng nghi vấn bằng heatmap, sinh báo cáo giải thích bằng AI và lưu lại lịch sử phân tích.

## 1. Giới thiệu đề tài

Sự phát triển của các mô hình sinh ảnh, hoán đổi khuôn mặt và chỉnh sửa video bằng AI làm cho deepfake ngày càng khó nhận biết bằng mắt thường. Deepfake có thể bị lợi dụng trong lừa đảo, giả mạo danh tính, thao túng thông tin, phát tán nội dung sai lệch hoặc gây tổn hại uy tín cá nhân/tổ chức.

Đề tài DeepShieldAI-Pro tập trung xây dựng một hệ thống kiểm tra media theo hướng thực dụng: người dùng chỉ cần tải ảnh hoặc video lên giao diện web, hệ thống tự động phân tích nhiều lớp tín hiệu và trả về kết luận REAL/FAKE, mức rủi ro, độ tin cậy, các frame/vùng đáng nghi và báo cáo diễn giải dễ hiểu.

## 2. Mục tiêu

- Xây dựng ứng dụng web có đầy đủ frontend, backend, API, lưu trữ và giao diện báo cáo.
- Phát hiện deepfake trên ảnh và video bằng mô hình học sâu kết hợp phân tích pháp chứng.
- Trích xuất khuôn mặt và frame đại diện để giảm chi phí xử lý video.
- Tạo heatmap/Grad-CAM nhằm giải thích vùng ảnh ảnh hưởng mạnh đến kết quả.
- Tính điểm rủi ro tổng hợp từ mô hình AI, metadata, FFT, artifact và thống kê theo thời gian.
- Lưu lịch sử phân tích bằng SQLite để người dùng xem lại kết quả.
- Tích hợp chatbot/báo cáo AI qua Groq, Gemini hoặc Ollama để diễn giải kết quả.
- Đóng gói bằng Docker Compose để dễ triển khai và demo.

## 3. Phạm vi chức năng

Hệ thống hỗ trợ:

- Ảnh: `.jpg`, `.jpeg`, `.png`, `.webp`.
- Video: `.mp4`, `.avi`, `.mov`, `.mkv`.
- Upload media và kiểm tra định dạng/kích thước file.
- Lấy metadata ảnh/video: kích thước, định dạng, dung lượng, FPS, số frame, thời lượng.
- Lấy mẫu frame từ video theo thời gian.
- Phát hiện và cắt khuôn mặt chính trong từng frame.
- Dự đoán xác suất deepfake cho ảnh/khuôn mặt/frame.
- Phân tích chuỗi video bằng mô hình temporal nếu có model.
- Fallback sang phân tích forensic khi không có model học sâu.
- Tạo Grad-CAM hoặc saliency heatmap.
- Xác định vùng nghi vấn trên khuôn mặt.
- Tính similarity giữa embedding khuôn mặt liên tiếp trong video.
- Sinh báo cáo `.txt` và `.json`.
- Xem lịch sử, chi tiết kết quả, tải báo cáo.
- Chatbot giải thích kết quả phân tích.

## 4. Công nghệ sử dụng

Backend:

- FastAPI, Uvicorn.
- OpenCV, Pillow, NumPy.
- TensorFlow/Keras.
- ONNX Runtime và TorchScript cho model tùy chọn.
- SQLite.
- Groq/OpenAI-compatible API, Gemini API hoặc Ollama cho phần giải thích bằng AI.

Frontend:

- React.
- Vite.
- Axios.
- React Router DOM.
- Tailwind CSS.
- Lucide React.
- Framer Motion.

Triển khai:

- Docker.
- Docker Compose.
- Named volumes cho database, storage và node_modules.

## 5. Kiến trúc tổng quan

```text
DeepShieldAI-Pro/
|-- backend/
|   |-- main.py
|   |-- requirements.txt
|   |-- app/
|   |   |-- api/          # REST API routes
|   |   |-- ai/           # model loader, inference, face detection, preprocessing
|   |   |-- core/         # config, constants, security
|   |   |-- database/     # SQLite database/repository
|   |   |-- schemas/      # request/response schemas
|   |   |-- services/     # analysis, report, heatmap, chatbot, video/image services
|   |   +-- utils/        # file, id, response, risk helpers
|   |-- models/           # model artifacts
|   |-- scripts/          # training/data preparation scripts
|   |-- storage/          # uploads, frames, faces, heatmaps, reports
|   +-- data/             # SQLite database
|-- frontend/
|   |-- package.json
|   |-- vite.config.js
|   +-- src/
|       |-- components/
|       |-- pages/
|       |-- services/
|       +-- styles/
|-- docs/
|-- docker-compose.yml
+-- README.md
```

Luồng xử lý chính:

```text
Upload ảnh/video
  -> Kiểm tra file
  -> Lưu file vào storage/uploads
  -> Trích xuất metadata
  -> Lấy frame đại diện
  -> Phát hiện/cắt khuôn mặt
  -> Tiền xử lý ảnh
  -> Inference bằng model deepfake
  -> Phân tích forensic bổ sung
  -> Tính embedding similarity cho video
  -> Sinh Grad-CAM/heatmap
  -> Tính risk score
  -> Sinh báo cáo AI
  -> Lưu SQLite và trả kết quả cho frontend
```

## 6. Các thuật toán và phương pháp

### 6.1 Haar Cascade Face Detection

Hệ thống dùng Haar Cascade của OpenCV để phát hiện khuôn mặt trong ảnh/frame. Với mỗi frame, khuôn mặt có diện tích lớn nhất được chọn làm đối tượng chính. Vùng crop được mở rộng bằng padding để giữ lại ngữ cảnh quanh khuôn mặt.

Nếu không phát hiện được khuôn mặt, hệ thống dùng toàn bộ frame làm đầu vào thay thế để pipeline vẫn hoạt động.

### 6.2 EfficientNet-B0

EfficientNet-B0 được dùng làm backbone trích xuất đặc trưng ảnh/khuôn mặt. Model ảnh mặc định được cấu hình qua biến `MODEL_PATH`, hiện là:

```text
models/efficientnet_deepfake_thisperson.keras
```

Ảnh đầu vào được resize theo `IMAGE_MODEL_SIZE`, mặc định là `160`, chuẩn hóa pixel và đưa vào model để tạo xác suất deepfake.

### 6.3 Transfer Learning

Quá trình huấn luyện có thể dùng trọng số pretrained ImageNet, sau đó fine-tune các layer cuối cho bài toán phân loại REAL/FAKE. Cách này giúp tận dụng đặc trưng thị giác tổng quát và giảm yêu cầu dữ liệu so với huấn luyện từ đầu.

### 6.4 Spatial Attention

Script huấn luyện EfficientNet bổ sung spatial attention sau feature map của backbone. Attention giúp tăng trọng số cho vùng ảnh có tín hiệu quan trọng trước khi pooling và phân loại.

### 6.5 Grad-CAM và Saliency Fallback

`backend/app/services/gradcam_service.py` ưu tiên tạo Grad-CAM thật nếu model Keras tương thích và TensorFlow hoạt động. Grad-CAM giúp trực quan hóa vùng ảnh đóng góp mạnh vào dự đoán.

Nếu không đủ điều kiện tạo Grad-CAM, hệ thống dùng saliency fallback dựa trên residual, edge map và colormap để vẫn có ảnh heatmap phục vụ demo/giải thích.

### 6.6 Metadata Forensics

Hệ thống kiểm tra metadata/EXIF như phần mềm xử lý, camera model, thời gian tạo file và các dấu vết bất thường. Metadata không đủ để kết luận deepfake, nhưng là tín hiệu bổ sung quan trọng khi kết hợp với model.

### 6.7 FFT Frequency Analysis

Fast Fourier Transform được dùng để phân tích miền tần số. Một số ảnh/video sinh hoặc chỉnh sửa bằng AI có thể để lại pattern bất thường ở texture, nhiễu hoặc phân bố tần số.

### 6.8 AI Artifact Detection

Module forensic đánh giá các dấu hiệu như texture quá mịn, nhiễu residual, pattern biên, màu sắc bất thường, nền bị méo hoặc vùng chuyển tiếp thiếu tự nhiên.

### 6.9 Face Embedding Similarity

Với video, hệ thống tính embedding nhẹ cho các crop khuôn mặt liên tiếp, sau đó đo cosine similarity. Sự sụt giảm similarity đột ngột có thể gợi ý frame bị chỉnh sửa, thay mặt hoặc thiếu nhất quán theo thời gian.

### 6.10 Fusion Risk Scoring

Kết quả cuối cùng không chỉ dựa vào một xác suất duy nhất. Hệ thống tổng hợp:

- Xác suất từ model ảnh/frame.
- Kết quả model temporal nếu có.
- Thống kê video theo frame.
- Metadata forensic.
- FFT.
- Artifact score.
- Embedding similarity.
- Vùng heatmap nghi vấn.

Ngưỡng fake mặc định:

```text
FAKE_THRESHOLD=0.58
```

Các mức rủi ro gồm `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`.

## 7. Quy trình xử lý chi tiết

### 7.1 Tiếp nhận file

Người dùng upload file qua endpoint:

```text
POST /api/analysis
```

Backend kiểm tra phần mở rộng, giới hạn dung lượng `MAX_UPLOAD_SIZE`, tạo mã phân tích riêng và lưu file vào `backend/storage/uploads`.

### 7.2 Trích xuất metadata

Với ảnh, hệ thống lấy:

- Chiều rộng, chiều cao.
- Định dạng.
- Mode màu.
- Dung lượng byte.

Với video, hệ thống lấy:

- Chiều rộng, chiều cao.
- FPS.
- Tổng số frame.
- Thời lượng.
- Dung lượng byte.

### 7.3 Lấy mẫu frame

Với ảnh, hệ thống dùng chính ảnh đó như một frame chuẩn.

Với video, hệ thống lấy mẫu đều theo thời gian, mặc định tối đa 20 frame. Nếu video có `N` frame và cần lấy `K` frame:

```text
index_i = round(i * (N - 1) / (K - 1)), với i = 0..K-1
```

Cách này giúp giảm chi phí xử lý nhưng vẫn giữ đại diện từ đầu đến cuối video.

### 7.4 Phát hiện khuôn mặt

Mỗi frame được đưa qua detector. Khuôn mặt chính được cắt và lưu vào `storage/faces`. Nếu không có khuôn mặt, toàn bộ frame được dùng thay thế.

### 7.5 Tiền xử lý

Các ảnh/khuôn mặt được:

- Đọc bằng OpenCV.
- Chuyển BGR sang RGB.
- Resize về kích thước model.
- Chuẩn hóa pixel về `[0, 1]`.
- Gom batch để inference.

### 7.6 Suy luận deepfake

Hệ thống hỗ trợ:

- Model Keras `.keras`, `.h5`.
- Model ONNX `.onnx`.
- Model TorchScript/PyTorch `.pt`, `.pth`.
- Model video temporal `models/video_deepfake.keras`.

Nếu model không sẵn sàng trong môi trường phát triển, hệ thống có thể dùng fallback forensic. Trong môi trường production, biến `REQUIRE_MODEL_IN_PRODUCTION=true` giúp yêu cầu model thật.

### 7.7 Tổng hợp kết quả

Kết quả trả về gồm:

- `analysisId`.
- `prediction`: `REAL` hoặc `FAKE`.
- `confidence`.
- `riskLevel`.
- `riskScore`.
- `fakeProbability`.
- `realProbability`.
- `frameResults`.
- `temporalStats`.
- `suspiciousSegments`.
- `embeddingSimilarity`.
- `faceDetections`.
- `heatmapUrl`.
- `heatmapMethod`.
- `suspiciousRegions`.
- `aiReport`.
- `reportId`.
- `reportUrl`.

## 8. Giao diện người dùng

Frontend React/Vite gồm các màn hình chính:

- Trang chủ giới thiệu hệ thống.
- Trang upload ảnh/video.
- Trang kết quả phân tích.
- Trang xem báo cáo.
- Trang lịch sử phân tích.
- Trang giới thiệu đề tài.
- Chatbot giải thích kết quả.

Các component nổi bật:

- `UploadBox`: kéo thả/chọn file.
- `FilePreview`: xem trước file.
- `AnalysisProgress`: trạng thái xử lý.
- `VerdictCard`: kết luận REAL/FAKE.
- `RiskScoreGauge`: điểm rủi ro.
- `HeatmapViewer`: xem vùng nghi vấn.
- `AdvancedAnalysisCard`: thống kê nâng cao như similarity và suspicious transition.
- `AIReportCard`: báo cáo giải thích bằng AI.
- `ChatbotWidget`: hỏi đáp về kết quả.

## 9. API chính

| Method | Endpoint | Mô tả |
| --- | --- | --- |
| `GET` | `/` | Kiểm tra backend đang chạy |
| `GET` | `/health` | Health check |
| `POST` | `/api/analysis` | Upload ảnh/video và chạy phân tích |
| `GET` | `/api/history?page=1&page_size=10` | Lấy lịch sử phân tích |
| `GET` | `/api/history/{analysis_id}` | Lấy chi tiết một phân tích |
| `GET` | `/api/reports` | Liệt kê báo cáo |
| `GET` | `/api/reports/{report_id}` | Xem nội dung báo cáo |
| `GET` | `/api/reports/{report_id}/download` | Tải báo cáo |
| `POST` | `/api/chatbot/explain` | Chatbot giải thích kết quả |
| `GET` | `/api/chatbot/suggestions` | Gợi ý câu hỏi |

Ví dụ upload:

```bash
curl -X POST "http://127.0.0.1:8000/api/analysis" \
  -F "file=@sample.mp4"
```

Trên Windows CMD:

```bat
curl -X POST "http://127.0.0.1:8000/api/analysis" ^
  -F "file=@sample.mp4"
```

## 10. Cài đặt và chạy dự án

### 10.1 Chạy bằng Docker Compose

```bash
docker compose up --build
```

Backend:

```text
http://127.0.0.1:8000
```

Frontend:

```text
http://127.0.0.1:5173
```

Docker sử dụng named volumes:

- `deepshield_data`: SQLite database tại `/app/data/deepshield.db`.
- `deepshield_storage`: uploads, frames, faces, heatmaps, reports tại `/app/storage`.
- `frontend_node_modules`: dependencies của frontend container.

Model được mount từ `backend/models` vào `/app/models`.

### 10.2 Chạy backend thủ công

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn main:app --reload
```

Swagger/OpenAPI:

```text
http://127.0.0.1:8000/docs
```

### 10.3 Chạy frontend thủ công

```bash
cd frontend
npm install
npm run dev
```

Nếu cần đổi API URL, tạo `frontend/.env`:

```env
VITE_API_URL=http://127.0.0.1:8000
```

## 11. Biến môi trường backend

Các biến quan trọng trong `backend/.env`:

```env
APP_NAME=DeepShield AI Pro
APP_VERSION=1.0.0
APP_DESCRIPTION=Deepfake Detection Platform using EfficientNet-B0, Grad-CAM and Groq AI
ENVIRONMENT=development
API_PREFIX=/api

MODEL_PATH=models/efficientnet_deepfake_thisperson.keras
IMAGE_MODEL_SIZE=160
FAKE_THRESHOLD=0.58
REVIEW_MARGIN=0.08
SUSPICIOUS_FRAME_THRESHOLD=0.55
FORENSIC_STRICT_THRESHOLD=58
REQUIRE_MODEL_IN_PRODUCTION=true

VIDEO_MODEL_PATH=models/video_deepfake.keras
VIDEO_SEQUENCE_LENGTH=4
VIDEO_IMAGE_SIZE=128

UPLOAD_DIR=storage/uploads
FRAME_DIR=storage/frames
FACE_DIR=storage/faces
HEATMAP_DIR=storage/heatmaps
REPORT_DIR=storage/reports
DATABASE_URL=sqlite:///data/deepshield.db

CHATBOT_PROVIDER=groq
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=llama3.1:8b
GROQ_API_KEY=your_groq_api_key_here
GROQ_BASE_URL=https://api.groq.com/openai/v1
GROQ_MODEL=llama-3.1-8b-instant
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta
GEMINI_MODEL=gemini-2.5-flash

CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
MAX_UPLOAD_SIZE=209715200
```

## 12. Huấn luyện model

### 12.1 Huấn luyện model ảnh EfficientNet

Script:

```bash
cd backend
python scripts/train_efficientnet.py --data-dir path/to/dataset --output models/efficientnet_deepfake_thisperson.keras
```

Cấu trúc dataset:

```text
dataset/
|-- real/
+-- fake/
```

Quy trình:

- Đọc dữ liệu bằng `image_dataset_from_directory`.
- Chia train/validation.
- Resize ảnh.
- Tăng cường dữ liệu bằng flip, rotation, zoom, contrast.
- Dùng EfficientNetB0 pretrained ImageNet.
- Thêm spatial attention.
- Phân loại bằng Dense sigmoid.
- Tối ưu Adam và binary crossentropy.
- Theo dõi accuracy, AUC, precision, recall.
- Dùng checkpoint, early stopping và reduce learning rate.
- Fine-tune các layer cuối.

### 12.2 Huấn luyện model video temporal

Script:

```bash
cd backend
python scripts/train_video_temporal.py --source path/to/faceforensics_c23 --output models/video_deepfake.keras
```

Quy trình:

- Đọc video thật từ thư mục `original`.
- Đọc video giả từ các phương pháp FaceForensics++ như Deepfakes, Face2Face, FaceSwap, FaceShifter, NeuralTextures.
- Cân bằng số lượng real/fake nếu cần.
- Lấy chuỗi frame đều theo thời gian.
- Cắt khuôn mặt hoặc fallback về frame đầy đủ.
- Dùng frame encoder `tiny`, `mobilenet` hoặc `efficientnet`.
- Đưa đặc trưng qua `Bidirectional GRU`.
- Xuất xác suất deepfake bằng sigmoid.

## 13. Lưu trữ dữ liệu

Các file sinh ra trong quá trình phân tích:

- `backend/storage/uploads`: file người dùng tải lên.
- `backend/storage/frames`: frame được trích xuất.
- `backend/storage/faces`: crop khuôn mặt.
- `backend/storage/heatmaps`: ảnh heatmap/Grad-CAM.
- `backend/storage/reports`: báo cáo text/json.
- `backend/data/deepshield.db`: SQLite database.

## 14. Ý nghĩa thực tiễn

DeepShieldAI-Pro có thể dùng làm:

- Công cụ demo phát hiện deepfake trong môi trường học tập/nghiên cứu.
- Nền tảng thử nghiệm các mô hình phân loại ảnh/video giả mạo.
- Hệ thống hỗ trợ phân tích media trước khi chia sẻ hoặc sử dụng làm bằng chứng.
- Cơ sở để phát triển dashboard kiểm duyệt nội dung hoặc xác minh danh tính.

## 15. Hạn chế

- Kết quả phụ thuộc mạnh vào chất lượng model và dữ liệu huấn luyện.
- Fallback forensic chỉ mang tính tham khảo, không thay thế model học sâu.
- Ảnh/video nén mạnh, mờ, thiếu khuôn mặt hoặc góc quay phức tạp có thể làm giảm độ chính xác.
- Deepfake thế hệ mới có thể che giấu nhiều artifact truyền thống.
- Metadata có thể bị xóa hoặc chỉnh sửa nên không thể dùng riêng để kết luận.

## 16. Hướng phát triển

- Bổ sung model transformer/video foundation model cho chuỗi frame dài hơn.
- Thêm face tracking để theo dõi nhiều người trong cùng video.
- Thêm xác thực nguồn media và kiểm tra watermark/C2PA nếu có.
- Bổ sung dashboard thống kê tập trung cho nhiều người dùng.
- Thêm cơ chế phân quyền, đăng nhập và quản lý phiên phân tích.
- Mở rộng bộ benchmark và test tự động cho từng thuật toán.
- Cải thiện giải thích AI theo hướng có trích dẫn từ dữ liệu phân tích.

## 17. Kết luận

DeepShieldAI-Pro là một hệ thống phát hiện deepfake hoàn chỉnh ở mức ứng dụng, kết hợp học sâu, phân tích pháp chứng, trực quan hóa heatmap, báo cáo AI và giao diện web. Đề tài không chỉ đưa ra kết luận REAL/FAKE mà còn cung cấp các tín hiệu giải thích để người dùng hiểu vì sao media bị đánh giá là đáng tin cậy hoặc đáng nghi.
