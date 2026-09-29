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
| 1 stage, base python:3.11 | 1,188,388,097 bytes = 1,188.39 MB |
| Multi-stage, base python:3.11-slim | 208,822,946 bytes = 208.82 MB |

Số đo từ Docker image inspect trong GitHub Actions run 36517699543, artifact image-size-evidence (benchmarks/image-sizes.txt). MB ở đây là 1,000,000 bytes; hai image được build trên cùng runner. Bản single dùng benchmarks/Dockerfile.single giữ cấu trúc Dockerfile gốc và cùng .dockerignore an toàn. So sánh bản gốc python:3.11 với slim chủ yếu phản ánh các thư viện/công cụ khác nhau trong base image. Multi-stage loại những thành phần builder không copy sang runtime; bài này cài wheel, không thêm compiler, nên không thể gán toàn bộ chênh lệch dung lượng cho multi-stage.

### Câu 4 — Thứ tự lệnh trong Dockerfile (CP2)

requirements.txt được COPY trước bước cài dependency; app và utils được COPY riêng ở runtime. Khi chỉ đổi app/main.py, cache dependency builder vẫn hợp lệ; COPY app và các layer runtime phía sau được tính lại. COPY . . trước pip install làm checksum source thay đổi và vô hiệu cache bước pip. Đã thử thêm một comment vào app/main.py rồi build lại và khôi phục file. Log benchmarks/cache-build.txt xác nhận COPY requirements.txt, bước pip install và COPY venv đều CACHED; COPY app và COPY utils chạy lại. Đây là quan sát thực từ Docker Desktop.

### Câu 5 — Vì sao không chạy bằng root (CP2)

Nếu lỗi Python cho phép thực thi lệnh, lệnh có quyền của process ứng dụng. Với UID 0, kẻ tấn công sửa được nhiều file trong container; nếu có mount nhạy cảm, Docker socket hoặc lỗi kernel/container escape thì có thể tác động host. Root trong container không tự động đồng nghĩa root trên host. USER agent (UID 10001) giảm quyền ngay tại process bị khai thác, nhưng vẫn cần tránh privileged/socket mount và vá hệ thống. CI đã chạy id -u để xác nhận non-root.

### Câu 6 — Cửa sổ trượt (CP3)

Fixed window cho phép 20 request trong hai giây quanh ranh giới phút: 10 lúc 10:00:59 và 10 lúc 10:01:00. Sliding window đếm 60 giây gần nhất nên nhóm thứ hai bị chặn khi quota 10 đã đầy. ZSET dùng timestamp làm score và UUID trong member để các request cùng thời điểm không ghi đè. Test bổ sung gửi đồng thời 30 request cùng timestamp; chỉ 5 request được nhận khi limit=5. WATCH/MULTI bảo đảm hai worker không cùng đọc quota còn trống rồi cùng vượt giới hạn.

### Câu 7 — Rate limit và cost guard (CP3)

Rate limit đo request/60 giây và trả 429; cost guard cộng USD/user/tháng UTC và trả 402. User gửi một request/phút nhưng đã tiêu 11 USD với budget 10 USD thì rate limit cho qua, cost guard chặn. User mới tiêu 0.001 USD nhưng gửi request thứ 11 trong một phút thì budget còn nhưng rate limit chặn. Test đã chứng minh budget vượt thì mock LLM không được gọi. Guard theo đề kiểm tra số đã tiêu trước request, chưa đặt trước chi phí nên không bảo đảm trần tuyệt đối khi nhiều request đồng thời hoặc một request quá đắt.

### Câu 8 — /health khác /ready (CP4)

Redis mất kết nối khiến probe kiểm tra Redis trả 503 ở cả ba instance. Nếu probe đó được dùng làm liveness và đủ số lần thất bại, orchestrator có thể restart cả ba. Khi Redis trở lại, app vẫn cần khởi động lại, kéo dài gián đoạn. Với hai endpoint riêng, /health vẫn 200 còn /ready 503 để ngừng nhận traffic; Redis phục hồi thì /ready tự về 200. Thời điểm restart phụ thuộc ngưỡng platform, không phải mọi lần mất Redis 30 giây đều restart. Test xác nhận readiness báo lỗi dependency và health không nhận dependency nào.

### Câu 9 — Stateless (CP4)

Đã chạy ba agent thật bằng Compose với Redis thật; dùng docker exec gửi HTTP tới từng agent luân phiên, cùng X-User-Id. Kết quả 0,2,4,6,8,10 qua instance 1,2,3,1,2,3 được lưu trong benchmarks/scale-evidence.txt. Thử nghiệm gọi trực tiếp từng container, chưa chạy Nginx. Sau đó đưa stack về một agent; Redis volume được giữ nguyên. Cấu hình docker-compose.scale.yml bỏ port cố định của agent và đưa Nginx ra cổng 8000. Lịch sử chung tăng 0,2,4,... đến tối đa 20. Dict Python riêng từng process sẽ tạo các nhánh 0,0,2,... tùy instance nhận request và mất khi restart.

### Câu 10 — Deploy thật (CP5)

Khi chạy test CP5 với URL Render thật, /ready có một lần báo `httpx.ConnectTimeout: timed out` sau ngưỡng kết nối 20 giây. Ngay trước đó, gọi trực tiếp trả /health 200, /ready 200 và /ask thiếu key 401. Traceback ở bước connect_tcp, không phải response 503 của readiness, nên bằng chứng nghiêng về kết nối mạng tạm thời thay vì sai REDIS_URL. Chạy lại nguyên bộ CP5 đạt 8 passed, 5 skipped trong 65.86 giây. Không đổi code hoặc tăng timeout; kết nối đã phục hồi ở lần kiểm tra này. Năm test bỏ qua gồm bốn test local fallback và một test có key cloud chưa cấu hình.
