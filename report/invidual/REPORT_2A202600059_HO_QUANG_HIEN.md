# Individual Report: Lab 3 - Chatbot vs ReAct Agent

Student Name: Hồ Quang Hiển
Student ID: 2A202600059
Date: 06-04-2026 (DD-MM-YYYY)

- **Vai trò:** Tool layer + mock pricing 

---

## I. Đóng góp kỹ thuật

- **Module:** `src/tools.py`  
- **Nội dung:**  
  - Định nghĩa catalog xe (VF3, VF8 Plus, VF9 Plus, Lux A2.0) với giá niêm yết và `PROMOTIONS` theo model.  
  - Hai tool LangChain `@tool`: `check_price`, `calculate_monthly_payment` — ràng buộc `months` ∈ {12,24,36,48,60} và `down_pct` 20–50.  
- **Ý nghĩa:** Tool là **single source of truth** cho số liệu; agent chỉ “đọc đúng” khi prompt (v2) ép quy trình trừ KM trước khi gọi `calculate_monthly_payment`.

**Snippet (ràng buộc kỳ hạn — hỗ trợ case T05):**

```python
if months not in (12, 24, 36, 48, 60):
    return {"error": f"months phải là 12/24/36/48/60, nhận được {months}"}
```

---

## II. Case study debug / quan sát

- **Hiện tượng:** Chạy `run_evaluation.py`, T02 v1 trả lời “không có thông tin KM tháng 4” dù tool **không** chứa API KM — KM chỉ nằm trong dict `PROMOTIONS` và được **nhắc trong prompt v2**.  
- **Chẩn đoán:** Đây không phải lỗi tool mà là **B2** — thiếu context trong `SYSTEM_V1`.  
- **Bài học:** Tool-first không đủ; **business rules** (bảng KM) phải vào prompt hoặo tool riêng `get_promotion` nếu muốn tách hẳn.

---

## III. Nhận xét cá nhân

1. **LangGraph + ToolNode** giảm code so với ReAct viết tay, nhưng **prompt vẫn là điểm gãy** khi stakeholder thêm rule (KM).  
2. **v1 T05** trong log mới: né **50 tháng** bằng cách gọi **48 tháng** ngay; câu cuối dạng *16,76 triệu* có thể **không** khớp `expected_contains` — **FAIL** dù tool có thể trả `error` cho `months=50`.  
3. **Observation** tool: lỗi `Toyota` trong `check_price` vẫn không ngăn v1 gọi tool trước; KM không có trong output tool nên v1 **không** tự suy ra **50tr / 10tr** nếu không có prompt như v2.

---

## IV. Hướng cải tiến

- Thêm tool `get_promotion(model, month)` để v1 không phụ thuộc prompt dài.  
- Evaluation: assert giá sau KM hoặc monthly_payment trong khoảng cho phép.
