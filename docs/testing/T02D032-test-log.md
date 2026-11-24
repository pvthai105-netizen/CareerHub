# Test log — T02D032

## Môi trường và lệnh

- Ngày chạy: 24/11/2026
- Python: 3.14.5 trong `backend/.venv`
- Pytest: 9.2.0
- Database test: SQLite in-memory, không dùng dữ liệu production/development MySQL
- Lệnh cuối:

```powershell
.venv\Scripts\python.exe -m pytest tests/test_notifications_api.py tests/test_applications_api.py -q
```

## Kết quả cuối

```text
....................................                                     [100%]
36 passed, 66 warnings in 1.57s
```

Phân rã: 14 test thông báo T02D032 và 22 test ứng tuyển hiện có. Không có test thất bại ở lần chạy cuối.

## Lỗi phát hiện và sửa

1. **Test harness phụ thuộc nhầm vào MySQL khi thu thập test.** Import `app.main` gọi `Base.metadata.create_all()` ngay khi nạp module, khiến pytest cố kết nối `localhost` và dừng trước khi chạy. Thay đổi: test tạo FastAPI app cô lập chỉ gồm notification router và dùng SQLite in-memory; không cần kết nối MySQL.
2. **Hai assertion cận phân trang đọc sai cấu trúc metadata của FastAPI.** Test giả định một metadata object chứa cả `ge` lẫn `le`, trong khi FastAPI/Pydantic lưu `Ge` và `Le` riêng. Thay đổi: assertion duyệt metadata để kiểm tra từng cận độc lập. Lần chạy sau đạt 36/36.
3. **Lỗi logic nghiệp vụ:** không phát hiện trong phạm vi test này; không sửa code ứng dụng.

## Ghi chú

- Lần chạy bằng Python hệ thống ban đầu không có gói `pytest`; dùng `.venv` của repo để chạy.
- 66 cảnh báo deprecation đến từ SQLAlchemy dùng `datetime.utcnow()` trong default timestamp của model; không làm test thất bại và không thuộc phạm vi thay đổi T02D032.
- `TestClient` treo ở request đầu trong môi trường hiện tại; các test gọi trực tiếp notification route/service với SQLite, đồng thời kiểm tra dependency auth và metadata giới hạn query. Vì vậy kết quả không được xem là kiểm thử HTTP end-to-end qua server đang chạy.
