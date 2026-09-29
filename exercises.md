# Phiếu Phản Ánh — K4 Level 3B, Ngày 12

Họ và tên: Dương Hà Đức Anh — Mã học viên: 2A202602977.

Bản giải thích có hỗ trợ AI, dựa trên kiểm thử trong PROGRESS.md. Học viên cần đọc lại và giải thích được bài nộp. Các quan sát còn thiếu được ghi rõ.

### Câu 1 — Fail fast (CP1)

Khi tạo service Render nhưng quên nhập AGENT_API_KEY, Settings báo ValidationError trước khi Uvicorn nhận traffic. Nếu dùng changeme làm mặc định, service vẫn public và người biết code có thể gọi /ask. Kiểm thử thiếu biến và chuỗi rỗng đều đã chạy thành công. Lifespan gọi get_settings() để lỗi xảy ra lúc khởi động, không đợi request đầu tiên.

### Câu 2 — Log cho máy đọc (CP1)

Log thực từ Uvicorn local, REDIS_URL=fake://, sau một request /ask:

```json
{"user_id":"local-evidence","tokens_in":3,"tokens_out":41,"cost_usd":2.505e-05,"event":"ask_completed","level":"info","timestamp":"2026-09-29T03:28:56.781961+00:00"}
```

Có thể lọc theo timestamp/user_id rồi cộng cost_usd theo user/ngày để tìm người dùng tiêu nhiều nhất. Có thể tổng hợp tokens_in/tokens_out để phát hiện prompt quá lớn. Print thông báo không có các trường này thì không tổng hợp trực tiếp được. Log không chứa API key hoặc nội dung câu hỏi.

### Câu 3 — Kích thước image (CP2)

| Bản | Dung lượng đo thực tế |
|---|---|
| 1 stage, base python:3.11 | Chưa đo |
| Multi-stage, base python:3.11-slim | CI đã xác nhận dưới 500 MiB; chờ số đo local |

Docker Hub đang tải base image rất chậm trên máy local. Không lấy số MB từ ví dụ trong đề làm số đo. So sánh bản gốc python:3.11 với slim chủ yếu phản ánh các thư viện/công cụ khác nhau trong base image. Multi-stage loại những thành phần builder không copy sang runtime; bài này cài wheel, không thêm compiler, nên không thể gán toàn bộ chênh lệch dung lượng cho multi-stage.

### Câu 4 — Thứ tự lệnh trong Dockerfile (CP2)

requirements.txt được COPY trước bước cài dependency; app và utils được COPY riêng ở runtime. Khi chỉ đổi app/main.py, cache dependency builder vẫn hợp lệ; COPY app và các layer runtime phía sau được tính lại. COPY . . trước pip install làm checksum source thay đổi và vô hiệu cache bước pip. Đây là phân tích Dockerfile; quan sát cache thực tế sẽ bổ sung khi build local hoàn thành.

### Câu 5 — Vì sao không chạy bằng root (CP2)

Nếu lỗi Python cho phép thực thi lệnh, lệnh có quyền của process ứng dụng. Với UID 0, kẻ tấn công sửa được nhiều file trong container; nếu có mount nhạy cảm, Docker socket hoặc lỗi kernel/container escape thì có thể tác động host. Root trong container không tự động đồng nghĩa root trên host. USER agent (UID 10001) giảm quyền ngay tại process bị khai thác, nhưng vẫn cần tránh privileged/socket mount và vá hệ thống. CI đã chạy id -u để xác nhận non-root.

### Câu 6 — Cửa sổ trượt (CP3)

Fixed window cho phép 20 request trong hai giây quanh ranh giới phút: 10 lúc 10:00:59 và 10 lúc 10:01:00. Sliding window đếm 60 giây gần nhất nên nhóm thứ hai bị chặn khi quota 10 đã đầy. ZSET dùng timestamp làm score và UUID trong member để các request cùng thời điểm không ghi đè. Test bổ sung gửi đồng thời 30 request cùng timestamp; chỉ 5 request được nhận khi limit=5. WATCH/MULTI bảo đảm hai worker không cùng đọc quota còn trống rồi cùng vượt giới hạn.

### Câu 7 — Rate limit và cost guard (CP3)

Rate limit đo request/60 giây và trả 429; cost guard cộng USD/user/tháng UTC và trả 402. User gửi một request/phút nhưng đã tiêu 11 USD với budget 10 USD thì rate limit cho qua, cost guard chặn. User mới tiêu 0.001 USD nhưng gửi request thứ 11 trong một phút thì budget còn nhưng rate limit chặn. Test đã chứng minh budget vượt thì mock LLM không được gọi. Guard theo đề kiểm tra số đã tiêu trước request, chưa đặt trước chi phí nên không bảo đảm trần tuyệt đối khi nhiều request đồng thời hoặc một request quá đắt.

### Câu 8 — /health khác /ready (CP4)

Redis mất kết nối khiến probe kiểm tra Redis trả 503 ở cả ba instance. Nếu probe đó được dùng làm liveness và đủ số lần thất bại, orchestrator có thể restart cả ba. Khi Redis trở lại, app vẫn cần khởi động lại, kéo dài gián đoạn. Với hai endpoint riêng, /health vẫn 200 còn /ready 503 để ngừng nhận traffic; Redis phục hồi thì /ready tự về 200. Thời điểm restart phụ thuộc ngưỡng platform, không phải mọi lần mất Redis 30 giây đều restart. Test xác nhận readiness báo lỗi dependency và health không nhận dependency nào.

### Câu 9 — Stateless (CP4)

Kiểm thử hai ConversationStore dùng chung Redis xác nhận instance B đọc được message instance A ghi. Uvicorn local với fake Redis đã trả history_length 0 rồi 2 cho hai câu liên tiếp; đây chưa phải bằng chứng ba container. Cấu hình docker-compose.scale.yml bỏ port cố định của agent và đưa Nginx ra cổng 8000. Lịch sử chung tăng 0,2,4,... đến tối đa 20. Dict Python riêng từng process sẽ tạo các nhánh 0,0,2,... tùy instance nhận request và mất khi restart.

### Câu 10 — Deploy thật (CP5)

Chưa quan sát lỗi deploy Render vì đang chờ tạo Blueprint và URL công khai. Lỗi hạ tầng local thực đã gặp: `permission denied while trying to connect to the docker API at npipe`. Kiểm tra lại với quyền truy cập Docker phù hợp trả Engine 29.1.2; sau đó Docker build bắt đầu tải base image. Đây là lỗi quyền ở môi trường chạy công cụ, chưa phải lỗi ứng dụng trên Render. Câu này cần cập nhật bằng quan sát cloud thật khi có URL, không thay bằng lỗi giả.
