# Báo cáo cá nhân — Lương Thanh Hậu

- **Vai trò:** Packaging, môi trường, tài liệu người dùng — chạy độc lập khỏi repo lab chính  
- **Ngày:** 2026-04-06  
- **Tham chiếu:** `README.md`, `requirements.txt`, `.env.example`, `.gitignore`

---

## I. Đóng góp kỹ thuật

- **`requirements.txt`:** Ghim `langgraph`, `langchain-openai`, `langchain-core`, `python-dotenv` để cài một lần trong venv.  
- **`.env.example`:** Mẫu biến OpenAI (+ optional Gemini/local theo template) để đồng bộ với thói quen lab gốc.  
- **`.gitignore`:** Loại `.env`, `__pycache__`, `.venv` — tránh lộ key.  
- **`README.md`:** Quy trình setup từ đầu **chỉ trong folder `vinfast_langgraph`**: `venv` → `pip install` → copy `.env` → `python run_evaluation.py`.

**Entry evaluation:** `run_evaluation.py` ở gốc mini-project tự `sys.path.insert` để không cần `PYTHONPATH` thủ công.

---

## II. Case study (reproducibility)

**Vấn đề:** Nếu chạy từ repo cha với import `vinfast_langgraph.xxx` sẽ phụ thuộc layout monorepo.  
**Giải pháp:** Import nội bộ `from src...` + chạy working directory = thư mục chứa `src/`.  
**Kiểm chứng:** Lần chạy có log `logs/vinfast_20260406_090834.log`: v1 **2/5**, v2 **5/5** (phụ thuộc model; luôn lưu log khi báo cáo).

---

## III. Insight cá nhân

1. Mini-project **đó lập** giúp chấm nhanh và tách khỏi code ReAct thủ công của lab chính — phù hợp demo LangGraph.  
2. `.env` không commit là rule sống còn khi chia sẻ repo.  
3. Nên ghi rõ **phiên bản Python** tối thiểu trong README (ví dụ 3.10+) nếu CI sau này.

---

## IV. Hướng cải tiến

- Thêm `Makefile` hoặc script `scripts/setup.sh` một dòng: venv + pip + copy .env.  
- Optional: `docker run` với secret mount cho môi trường đồng nhất.
