# Thông Tin Deploy — Checkpoint 5

## Thông tin học viên

| Mục | Nội dung |
|---|---|
| Họ và tên | Dương Hà Đức Anh |
| Mã học viên | 2A202602977 |
| Repo | https://github.com/duonghaducanh/K4-L3B-DAY12-DuongHaDucAnh-2A202602977-CloudServicesAndDeployment |

## Trạng thái

| Mục | Nội dung |
|---|---|
| Platform | Render |
| Public URL | https://day12-agent-gu55.onrender.com |
| Ngày deploy cloud | 2026-09-29 |
| Kiểm thử local | CP1 13/13, CP3 22/22, CP4 19/19; 4 kiểm thử bổ sung đạt |
| Docker trên GitHub Actions | Build thành công; image 208.82 MB, non-root đạt |
| Toàn bộ test cuối | 95 passed, 5 skipped; grade.py 100/100 tự động |

Public HTTPS đã kiểm tra thành công. LOCAL_FALLBACK=false. Ảnh dashboard
còn cần bổ sung; kiểm thử có key chờ DEPLOY_API_KEY cục bộ.

## Tạo service từ Blueprint

1. Render dashboard → New → Blueprint → chọn repository ở trên, nhánh main.
2. Render đọc render.yaml để tạo day12-agent và day12-redis, gói free.
3. Nhập AGENT_API_KEY bằng khóa riêng được sinh ngẫu nhiên; không dùng khóa ví dụ.
4. Chờ web service Live, lấy Public URL hiển thị trên dashboard.
5. Điền Public URL vào bảng trên rồi chạy kiểm thử bên dưới.

Các biến dưới đây khai báo trong Blueprint. Service đã khởi động và /ready
trả 200, xác nhận cấu hình bắt buộc cùng kết nối Redis hoạt động:

| Biến | Nguồn |
|---|---|
| PORT | Render tự cấp, Docker CMD đọc giá trị lúc chạy |
| AGENT_API_KEY | Nhập riêng trên Render, sync: false |
| REDIS_URL | connectionString từ service day12-redis |
| RATE_LIMIT_PER_MINUTE | Blueprint, 10 |
| MONTHLY_BUDGET_USD | Blueprint, 10.0 |
| LOG_LEVEL | Blueprint, INFO |

Render Key Value free không bảo đảm persistence qua restart. Redis ngoài
process giúp chia sẻ state giữa agent; dữ liệu vẫn có thể mất nếu Redis free
restart. Dùng gói có persistence khi cần bảo toàn lịch sử/ngân sách qua sự cố
Redis. maxmemoryPolicy=noeviction tránh tự loại bỏ key ngân sách khi đầy RAM.

## Kiểm tra cloud

Đặt DEPLOY_API_KEY trong .env cục bộ bằng khóa của service, không phải token
Render. Không commit .env. Đặt PUBLIC_URL trong shell thành URL từ dashboard:

```powershell
.venv/Scripts/python.exe scripts/smoke.py $env:PUBLIC_URL --cloud
.venv/Scripts/python.exe -m pytest tests/test_cp5.py -v
```

scripts/smoke.py kiểm tra health, readiness, 401 thiếu key, 200 có key và
history tăng từ 0 lên 2. Script không in giá trị key.

## Kết quả chạy thật

Uvicorn local với fake Redis (chưa phải cloud hoặc Docker stack):

```text
/health 200 {"status":"ok","service":"day12-agent","version":"1.0.0"}
/ready 200 {"status":"ready","redis":true}
/ask 200 history_length 0
/ask 200 history_length 2
```

Kết quả cloud thực tế ngày 2026-09-29:

```text
GET /health -> 200 {"status":"ok","service":"day12-agent","version":"1.0.0"}
GET /ready -> 200 {"status":"ready","redis":true}
POST /ask (không có API key) -> 401 {"detail":"invalid or missing API key"}
```

Readiness xác nhận service kết nối được Redis thật trên Render.

## Ảnh minh chứng

Cần bổ sung screenshots/dashboard.png từ dashboard Render và
screenshots/health.png từ kết quả HTTP thực. Không chụp phần environment
hiện giá trị secret. Ảnh health.png đã chụp trực tiếp từ endpoint công khai bằng Edge headless.
Ảnh dashboard.png đang chờ người dùng lưu từ phiên Render đã đăng nhập.

## CI/CD

Workflow .github/workflows/ci.yml chạy khi push/pull request, gồm test và
build. Badge README lấy trạng thái thực từ GitHub. CP5 và kiểm tra badge được
loại khỏi job test để tránh phụ thuộc deployment và vòng lặp tự kiểm tra.

Blueprint mặc định autoDeployTrigger: checksPass: Render chỉ tự deploy sau
khi CI xanh. Nếu muốn dùng job deploy trong Actions thay cho cơ chế này:

1. Trong Render tắt Auto-Deploy để tránh deploy hai lần.
2. Tạo GitHub Actions secret RENDER_DEPLOY_HOOK_URL từ Deploy Hook của service.
3. Tạo Actions variables RENDER_DEPLOY_ENABLED=true và PUBLIC_URL.
4. Push main. Job deploy đợi test/build đạt rồi yêu cầu Render deploy đúng
   GITHUB_SHA; sau đó kiểm tra health/readiness. Probe chỉ xác nhận service
   đang phục vụ, không chứng minh commit mới đã live; đối chiếu dashboard.

Nếu chưa bật biến, job deploy được skip có chủ đích; CI xanh không tự chứng
minh đã deploy cloud.

## Chạy và scale local

```powershell
docker compose up -d --build
docker compose -f docker-compose.yml -f docker-compose.scale.yml up -d --build --scale agent=3
.venv/Scripts/python.exe scripts/smoke.py http://localhost:8000
```

Override scale gỡ port agent và đưa Nginx ra 8000 để tránh xung đột cổng.
Khi quay lại một agent, dùng --remove-orphans để dừng Nginx của stack này;
không xóa volume Redis nếu cần giữ lịch sử.

## Kết quả Docker local cuối

Compose agent/Redis healthy. User runtime UID 10001. HTTP smoke có key hợp
lệ trả 200 và history 0 rồi 2; thiếu key trả 401. Ba agent dùng chung Redis
trả history 0,2,4,6,8,10; xem benchmarks/scale-evidence.txt. SIGTERM dừng
process với exit code 0 và log Application shutdown complete. Đã khởi động
lại agent và giữ nguyên volume Redis.

Trên PowerShell trước khi chạy test hoặc grade.py, nên đặt:

```powershell
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
```
