# VinFast LangGraph

So sánh **agent v1** (prompt mỏng, lỗi B1/B2) và **agent v2** (cùng graph, prompt đầy đủ + KM + guardrail) — tư vấn xe VinFast, **LangGraph** + OpenAI.

## Cấu trúc chính

| Đường dẫn | Vai trò |
|-----------|---------|
| `src/tools.py` | `check_price`, `calculate_monthly_payment`, mock `CATALOG` / `PROMOTIONS` |
| `src/agent_v1.py`, `src/agent_v2.py` | `StateGraph(MessagesState)` → `llm` ↔ `tools` → `END` |
| `src/file_log.py`, `src/langsmith_run.py` | Log cục bộ `logs/`; `run_name` có thời gian cho LangSmith |
| `tests/test_cases.py` | 5 case (trong đó T04/T05 nhiều lượt; T04 dùng `per_turn`) |
| `run_evaluation.py` | So v1/v2 từng case |
| `chat_demo.py` | Chat terminal nhiều lượt (`/quit`, `/clear`) |
| `report/` | Báo cáo nhóm `group_report/`, template cá nhân `individual_reports/`, rubric Lab 3 |

Chi tiết phân công 5 người: `report/MO_TA_CONG_VIEC_TUNG_THANH_VIEN.md`. Rubric mini-lab: `SCORING.md`.

## Setup & chạy

```bash
cd vinfast_langgraph
python3 -m venv .venv && source .venv/bin/activate   # tùy chọn
pip install -r requirements.txt
cp .env.example .env   # điền OPENAI_API_KEY, tuỳ chỉnh DEFAULT_MODEL, LANGCHAIN_*, FILE_LOG
python run_evaluation.py
python chat_demo.py     # hoặc chat_demo.py v1
```

Luôn chạy từ thư mục gốc (cùng cấp `src/`). `FILE_LOG=0` nếu không muốn ghi `logs/`.

## Luồng graph (tóm tắt)

`START` → node **`llm`** → `add_conditional_edges`: còn **`tool_calls`** thì vào node **`tools`** (ToolNode), không thì **`END`**. Sau `tools` quay lại **`llm`**; kết quả tool được **append** vào `state["messages"]`.

Xem thêm sơ đồ chi tiết (Mermaid) có thể mở `EVALUATION.md` hoặc lịch sử README trong git nếu đã gỡ bớt — logic không đổi.

## Thêm test / tool

- Case mới: `tests/test_cases.py` (`input` hoặc `turns`; nếu chấm từng lượt thêm `per_turn`).
- Tool mới: `src/tools.py` + ghép vào `TOOLS` trong cả hai agent.
