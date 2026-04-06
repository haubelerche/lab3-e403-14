# Báo cáo nhóm — VinFast LangGraph Agent (cập nhật theo repo hiện tại)

- **Tên nhóm:** [điền]
- **Thành viên (5):** xem phân công tại `../TASK_DIVISION_5_MEMBERS.md`
- **Rubric tham chiếu:** `../RUBRIC_LAB3_REFERENCE.md` (map từ Day-3 Lab `SCORING.md`)
- **Log phân tích v1 (minh chứng):** `logs/vinfast_20260406_090834.log`

---

## 1. Executive Summary

Cùng **StateGraph** + 2 tool (`src/tools.py`); **v1** dùng `SYSTEM_V1` mỏng, **v2** dùng `_system_v2()` có bảng KM + guardrail.

| Chỉ số | v1 | v2 |
|--------|----|----|
| Pass `run_evaluation.py` (tham chiếu log trên) | **2/5** | **5/5** |

**Điểm học:** Thiếu KM trong prompt và thiếu hướng dẫn từ chối / gọi tool đúng quy trình làm v1 fail nhiều case dù graph giống v2.

---

## 2. Kiến trúc & tool

### 2.1 LangGraph

`StateGraph(MessagesState)` → `add_node("llm", …)` → `add_node("tools", …)` → `add_edge(START, "llm")` → `add_conditional_edges("llm", should_continue)` → `"tools"` hoặc `END` → `add_edge("tools", "llm")` → `compile()`.

### 2.2 Tool

| Tool | Mục đích |
|------|----------|
| `check_price` | Giá niêm yết + màu (không trả KM) |
| `calculate_monthly_payment` | Trả góp; `months` ∈ {12,24,36,48,60}, `down_pct` 20–50 |

KM nằm trong `PROMOTIONS` — **chỉ v2** nhắc đầy đủ trong prompt qua `_promo_table()`.

### 2.3 LLM & phụ trợ

OpenAI (`ChatOpenAI`), `.env`: `OPENAI_API_KEY`, `DEFAULT_MODEL`.  
`src/file_log.py`, `src/langsmith_run.py` — trace cục bộ / LangSmith.

---

## 3. Telemetry & đánh giá

- **`python run_evaluation.py`:** T04 có **`per_turn`** (chấm từng lượt); T05 hai lượt, chấm **câu cuối** bằng `expected_contains`.
- **Log mẫu:** `vinfast_20260406_090834.log` — từng bước LLM / tool được ghi.

---

## 4. RCA v1 (đọc từ `vinfast_20260406_090834.log`)

| Case | v1 trong log | Giải thích |
|------|----------------|------------|
| **T01** | ✅ | Gọi `check_price` đúng; trả lời **1.259.000.000 VNĐ**. |
| **T02** | ❌ **B2** | Sau `check_price` chỉ có giá niêm yết; model nói *chưa có dữ liệu KM tháng 4* — **không** nêu **50.000.000** (có trong `PROMOTIONS` nhưng không vào prompt v1). |
| **T03** | ⚠️ ✅ matcher / ❌ nghiệp vụ | Gọi `calculate_monthly_payment` với **price = 1.259.000.000** (chưa trừ KM 30tr) → **21.722.549**/tháng; v2 dùng **1.229.000.000** → **21.204.935**. |
| **T04** | ❌ | **Lượt 1:** vẫn **gọi** `check_price('Toyota Camry hybrid')` → nhận `error` từ tool (chỉ sau đó mới giải thích chỉ VinFast). **Lượt 2:** tính góp trên **322.000.000**, nói *chưa có KM* — **không** đạt chuỗi **10.000.000** trong `per_turn` lượt 2. |
| **T05** | ❌ | **Lượt 1:** Khách hỏi **50 tháng**, v1 gọi tool với **`months: 48`** ngay (né lỗi tool) — không phải flow “gọi đúng 50 → nhận error” như v2. **Lượt 2** trả lời *~16,76 triệu/tháng* — **không** chứa chuỗi `16.760.846` / `16760846` trong `expected_contains` → dễ FAIL matcher. |

---

## 5. Ablation (v1 vs v2)

| Thành phần | v1 | v2 |
|------------|----|----|
| Bảng KM trong system | Không | `_promo_table()` |
| Quy trình giá sau KM trước `calculate_monthly_payment` | Không bắt buộc | Có trong prompt |
| Hãng khác | Có thể vẫn gọi tool với tên lạ | Không gọi tool; từ chối ngắn |
| Kỳ 50 tháng | Đổi thành 48, không lấy `error` từ tool | Gọi `months=50` → báo lỗi tool → lượt 2 đúng 48 |

---

## 6. Baseline vs Agent (rubric Day-3)

**Baseline:** **v1** = tool-calling nhưng prompt thiếu rule nghiệp vụ. **v2** = cùng graph, đã engineering prompt.

---

## 7. Bonus (gợi ý)

| Bonus | Minh chứng |
|-------|------------|
| Monitoring | LangSmith + `run_name` có timestamp |
| Failure / guardrail | `per_turn` T04; tool `error` tháng T05 (v2) |
| Live demo | `chat_demo.py` |

---

*Bổ sung tên nhóm và số đo mới nhất sau mỗi lần chạy eval. Template đầy đủ: `TEMPLATE_GROUP_REPORT.md`.*
