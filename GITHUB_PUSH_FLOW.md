# Luồng push dần lên GitHub (nhóm 5 người)

Mục tiêu: **một người** đẩy **commit đầu** (khung repo), cả nhóm **clone** về, rồi **mỗi người push theo phần** — ưu tiên **theo nhóm file / chủ đề commit**, không cần (và không nên) push từng file một trừ khi conflict.

---

## Quy ước chung

| Việc | Ghi chú |
|------|---------|
| **Nhánh chính** | `main` (hoặc `master`) — luôn giữ chạy được tối thiểu: `pip install -r requirements.txt` + eval không lỗi import. |
| **Nhánh làm việc** | `feature/<tên-ngắn>` hoặc `feat/<tên>`, ví dụ `feat/tools`, `feat/agent-v2`. |
| **Không commit** | `.env` (API key), `__pycache__/`, `.venv/`, log tạm nếu quá lớn — kiểm tra `.gitignore`. |
| **Trước mỗi lần push** | `git pull origin main` (hoặc rebase) để tránh đè nhau. |

---

## Bước 1 — Một người: “first commit” lên GitHub

**Ai làm:** người được chọn làm repo owner (vd Lan hoặc lead).

### 1.1 Tạo repo trống trên GitHub

- Tạo repository mới **không** tick “Add README” (hoặc có README cũng được, sẽ merge khi push).

### 1.2 Máy local (trong thư mục dự án)

```bash
cd vinfast_langgraph
git init
git branch -M main
```

Đảm bảo `.gitignore` đã có `.env` và thư mục rác phổ biến.

### 1.3 Commit đầu nên chứa gì (gợi ý “khung”)

Đẩy **một lần** các thứ ít tranh chấp, để người khác clone có “mặt bằng”:

- `README.md` (hoặc stub ngắn)
- `.gitignore`, `.env.example`
- `requirements.txt`
- `report/MO_TA_CONG_VIEC_TUNG_THANH_VIEN.md` (hoặc `TASK_DIVISION` nếu có)

**Chưa bắt buộc** đưa hết code vào commit đầu — có thể chỉ skeleton + doc; các phần code có thể là placeholder rỗng rồi các PR sau bổ sung. Nếu code đã có sẵn cục bộ, có thể gom **một commit** kiểu `chore: initial import` cho toàn bộ (đơn giản nhất).

```bash
git add .
git status   # kiểm tra KHÔNG có .env
git commit -m "chore: initial project skeleton and docs"
git remote add origin https://github.com/<org-or-user>/<repo>.git
git push -u origin main
```

---

## Bước 2 — Mỗi thành viên: clone và làm trên nhánh riêng

```bash
git clone https://github.com/<org-or-user>/<repo>.git
cd <repo>
git checkout -b feat/<phần-của-mình>
```

Làm việc, commit theo **ý nghĩa** (vd `feat(tools): catalog and promotions`), rồi:

```bash
git fetch origin
git rebase origin/main    # hoặc: git merge origin/main
git push -u origin feat/<phần-của-mình>
```

Trên GitHub: **Pull Request** vào `main`, một người **review + merge** (hoặc merge khi đủ điều kiện lớp).

---

## Bước 3 — Chia “từng phần push” theo người (khớp phân công repo)

Không cần tách từng file; nên **một PR / vài commit** theo đúng ranh giới trách nhiệm để ít conflict.

| Thành viên | Nên push / PR gồm (gói file) | Ghi chú |
|------------|------------------------------|---------|
| **An** — tool & mock | `src/tools.py` | Thay đổi catalog/KM ảnh hưởng mọi test — merge sớm hoặc báo nhóm trước khi đổi số. |
| **Bình** — LangGraph + prompt | `src/agent_v1.py`, `src/agent_v2.py` | Thường conflict với nhau ít; conflict với `tools` hiếm nếu chỉ đổi prompt. |
| **Minh** — eval & test | `tests/test_cases.py`, `run_evaluation.py`, (tuỳ chọn) `logs/*.log` mẫu | Test đổi kỳ vọng → cả nhóm cần biết; không commit log chứa secret. |
| **Tuấn** — rubric & report template | `report/` (trừ file cá nhân đang soạn dở nếu muốn tách), file rubric nếu có trong repo | Chủ yếu Markdown — conflict dễ fix. |
| **Lan** — packaging & demo | `requirements.txt`, `.env.example`, `.gitignore`, `README.md`, `chat_demo.py`, `src/file_log.py`, `src/langsmith_run.py` | PR “infra” nên vào sau khi có code tối thiểu hoặc cập nhật nhỏ liên tục. |

**Thứ tự gợi ý merge (giảm vỡ build):**

1. An: `tools.py` + dữ liệu mock ổn định  
2. Bình: `agent_v1.py` / `agent_v2.py`  
3. Minh: `test_cases.py` + `run_evaluation.py`  
4. Lan: README, requirements, demo, logging  
5. Tuấn: report / rubric (có thể song song, ít phụ thuộc code)

Thực tế có thể **song song** nếu mỗi người sửa file khác nhau; nếu hai người sửa cùng `README.md`, ai merge sau phải **pull + giải conflict**.

---

## Ví dụ “push từng phần” bằng nhiều commit (một người)

Nếu một người ôm nhiều phần, vẫn nên **tách commit** cho dễ review, không nhất thiết tách PR:

```text
commit 1: chore: add .gitignore and env example
commit 2: feat(tools): VinFast catalog and promotions
commit 3: feat(agent): v1/v2 LangGraph and prompts
commit 4: test: evaluation cases T01–T05
commit 5: docs: group report template
```

---

## Checklist nhanh trước khi nộp bài

- [ ] `main` không chứa `.env`  
- [ ] `python run_evaluation.py` chạy được trên máy “sạch” (sau `pip install -r requirements.txt`)  
- [ ] Mỗi người có ít nhất **1 commit** hoặc **1 PR** có tên rõ (để thầy/cô thấy đóng góp)

---

*Tài liệu này chỉ mô tả quy trình Git; không thay cho yêu cầu nộp bài của môn học.*
