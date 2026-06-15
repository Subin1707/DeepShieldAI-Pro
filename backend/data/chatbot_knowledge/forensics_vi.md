# DeepShield AI Pro - Kiến thức giải thích Forensics

## Nguyên tắc trả lời

- Luôn nói rõ kết quả là hỗ trợ phân tích, không phải kết luận pháp lý tuyệt đối.
- Ưu tiên giải thích bằng tiếng Việt có dấu, ngắn gọn nhưng đủ ý.
- Khi có điểm nghi ngờ, cần nêu: vùng nào, vì sao đáng chú ý, cách kiểm tra thủ công.
- Nếu độ tin cậy thấp hoặc video mờ/nén mạnh/khuôn mặt nhỏ, phải nói rõ giới hạn.
- Không khẳng định đã xem file gốc nếu hệ thống chỉ cung cấp metadata hoặc kết quả phân tích.

## Các vùng thường lộ lỗi deepfake

### Vùng mắt

Dấu hiệu đáng chú ý:
- Mí mắt méo, biên mí không tự nhiên.
- Hai mắt có phản chiếu ánh sáng không đồng nhất.
- Chớp mắt thiếu tự nhiên hoặc không khớp giữa các frame.
- Con ngươi hoặc vùng trắng mắt bị nhiễu, bệt màu, rung nhẹ.

Cách kiểm tra:
- Phóng to từng mắt và so sánh trái/phải.
- Xem chậm nhiều frame liên tiếp.
- Chú ý phản chiếu ánh sáng trong mắt và viền mí.

### Vùng miệng

Dấu hiệu đáng chú ý:
- Khẩu hình không khớp âm thanh.
- Răng bị bệt, mờ, biến dạng hoặc thay đổi hình dạng giữa các frame.
- Viền môi rung, nhòe, hoặc dính vào vùng da xung quanh.
- Miệng mở/đóng thiếu tự nhiên khi nói.

Cách kiểm tra:
- Xem đoạn có nói chuyện ở tốc độ chậm.
- So khớp âm thanh với khẩu hình.
- Dừng ở các frame có miệng mở để xem răng, môi và viền miệng.

### Viền khuôn mặt

Dấu hiệu đáng chú ý:
- Viền mặt có ánh sáng lạ, lệch màu so với cổ/nền.
- Vùng cằm, má, tóc, tai hoặc cổ bị méo.
- Ranh giới giữa mặt và nền bị rung khi video chuyển động.
- Texture da ở mặt không khớp vùng cổ hoặc tai.

Cách kiểm tra:
- Theo dõi viền mặt qua nhiều frame.
- So sánh màu da giữa mặt, cổ và tai.
- Xem kỹ vùng tóc, má, cằm và đường hàm.

### Vùng mũi

Dấu hiệu đáng chú ý:
- Bóng mũi không khớp hướng sáng tổng thể.
- Sống mũi bị méo, texture da quanh mũi bị nhiễu.
- Vùng chuyển tiếp giữa mũi và má bị bệt hoặc nhòe.

Cách kiểm tra:
- So sánh bóng đổ ở mũi với bóng ở má/cằm.
- Xem nhiều frame gần nhau để phát hiện rung hoặc biến dạng.

### Kết cấu da

Dấu hiệu đáng chú ý:
- Da quá mịn, mất lỗ chân lông hoặc chi tiết tự nhiên.
- Texture bị lặp, bệt màu hoặc khác rõ giữa vùng mặt và cổ.
- Có nhiễu tần số cao bất thường quanh mắt, miệng, viền mặt.

Cách kiểm tra:
- Phóng to vùng má, trán, cằm.
- So texture mặt với cổ/tai.
- Nếu video nén mạnh, cần thận trọng vì nén video cũng tạo nhiễu giả.

## Cách hiểu chỉ số

### Prediction

- FAKE: hệ thống thấy tín hiệu nghi giả mạo đủ mạnh.
- REAL: hệ thống chưa thấy dấu hiệu giả mạo rõ ràng.
- UNKNOWN hoặc không chắc: cần kiểm tra thêm, không nên kết luận.

### Confidence

Confidence là mức chắc chắn của dự đoán hiện tại. Confidence cao không đồng nghĩa chắc chắn tuyệt đối, nhất là khi video mờ, bị nén, thiếu sáng hoặc khuôn mặt quá nhỏ.

### Risk level

- Thấp: chưa có nhiều tín hiệu đáng ngại, nhưng vẫn nên kiểm tra thủ công nếu nội dung quan trọng.
- Trung bình: có một số vùng cần xem lại, nên đối chiếu frame và nguồn gốc file.
- Cao: có nhiều tín hiệu bất thường hoặc điểm nghi ngờ mạnh, cần kiểm tra kỹ hơn.
- Rất cao: nhiều tín hiệu cùng hướng, nên coi là nội dung cần điều tra sâu.

### Heatmap

Heatmap cho biết vùng nào có tín hiệu nổi bật với mô hình hoặc phân tích ảnh. Heatmap không phải bằng chứng tuyệt đối; nó chỉ giúp người dùng biết nên nhìn kỹ vùng nào trước.

## Khi nào kết quả dễ sai

- Video độ phân giải thấp hoặc bị crop quá sát.
- Khuôn mặt quá nhỏ, nghiêng mạnh, bị che bởi tay/kính/khẩu trang.
- Ánh sáng yếu, ngược sáng hoặc có filter làm đẹp.
- Video bị nén mạnh, quay màn hình, upload lại nhiều lần.
- Chỉ có một frame ảnh, không có chuyển động để kiểm tra theo thời gian.

## Khuyến nghị trả lời chatbot

Khi người dùng hỏi “vì sao fake/real”, hãy trả lời theo cấu trúc:

1. Kết luận sơ bộ.
2. Độ tin cậy và mức rủi ro.
3. Các vùng nghi ngờ chính.
4. Vì sao từng vùng đáng chú ý.
5. Cách kiểm tra thủ công.
6. Giới hạn của kết quả.

Khi người dùng hỏi cách cải thiện độ chính xác:

- Dùng video gốc nếu có.
- Tránh video đã bị nén nhiều lần.
- Chọn đoạn có mặt rõ, đủ sáng, nhìn thẳng.
- Cung cấp đoạn có nói chuyện hoặc chuyển động mặt.
- Train thêm dataset cân bằng real/fake và kiểm tra AUC, precision, recall.
