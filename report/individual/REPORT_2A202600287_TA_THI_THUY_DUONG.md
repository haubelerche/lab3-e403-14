# Báo cáo cá nhân — Tạ Thị Thùy Dương

Individual Report: Lab 3 - Chatbot vs ReAct Agent
Student Name: Tạ Thị Thùy Dương
Student ID: 2A202600287
Date: 6/4/2026

- **Vai trò:** Rubric, hướng dẫn giảng viên, template báo cáo kết quả  
- **Ngày:** 2026-04-06  
- **Tham chiếu:** `SCORING.md`, `INSTRUCTOR_GUIDE.md`, `report/evaluation_template.md`

---

## I. Đóng góp kỹ thuật & tài liệu

- **`SCORING.md`:** Chuẩn hoá bảng mục tiêu so sánh v1/v2 (simple / multi-step / edge), mapping bug B1/B2 ↔ file mã nguồn.  
- **`INSTRUCTOR_GUIDE.md`:** Timeline 30 phút, điểm học LangGraph vs prompt ablation, nhấn mạnh project chạy độc lập một folder.  
- **`report/evaluation_template.md`:** Form điền pass rate, latency, nhận xét B1/B2 sau mỗi lần chạy `run_evaluation.py`.

Mục tiêu: giảng viên và nhóm có **ngôn ngữ chung** khi chấm, không phải đoán tiêu chí.

---

## II. Case study (đồng bộ rubric với kết quả thật)

**Dữ liệu:** `logs/vinfast_20260406_090834.log` — v1 **2/5**, v2 **5/5**.

| Ô SCORING / test | Khớp log? |
|------------------|------------|
| T02 KM | v1 không nêu 50tr (B2) |
| T03 / T04 sau KM | v1 sai KM hoặc matcher T04 l2; GROUP_REPORT đã RCA theo log |
| T05 edge | v1 **không** lấy `error` tháng 50; có thể fail matcher câu cuối |

**Việc đã làm:** Đồng bộ rubric với T04 **Toyota + VF3** (`per_turn`) và T05 **hai lượt**; `evaluation_template.md` ở `report/`.

---

## III. Insight cá nhân

1. Rubric ngắn nhưng phải gắn **bằng chứng log** (screenshot / paste terminal) để tránh tranh luận “v1 có thực sự bug không”.  
2. Template nhóm giúp **5 người** không trùng nội dung: mỗi người một góc (tool / graph / eval / rubric / devops).

---

## IV. Hướng cải tiến

- Thêm tiểu mục “nghiệp vụ vs substring” vào SCORING phiên bản sau.  
- Checklist nộp bài: GROUP + 5 file `REPORT_*.md`.
