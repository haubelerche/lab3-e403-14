"""
vinfast_langgraph/src/agent_v2.py — Agent v2 (B1/B2 đã fix).
"""

import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from src.file_log import ensure_file_log, log, make_logged_tool_node, preview
from src.langsmith_run import with_timestamped_run_name
from src.tools import check_price, calculate_monthly_payment, PROMOTIONS

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_PROJECT_ROOT / ".env")

TOOLS = [check_price, calculate_monthly_payment]


def _promo_table() -> str:
    month = datetime.now().month
    lines = [f"Khuyến mãi tháng {month}:"]
    for model, p in PROMOTIONS.items():
        lines.append(f"  - {model}: giảm {p['discount']:,} VNĐ tiền mặt")
    return "\n".join(lines)


def _system_v2() -> str:
    return f"""Bạn là trợ lý tư vấn mua xe VinFast. Bạn có đúng 2 công cụ:

Phạm vi bắt buộc: CHỈ tư vấn nội dung liên quan **VinFast** (giá xe, màu sắc, khuyến mãi, trả góp, mua xe, so sánh dòng VF/Lux trong danh mục tool).

Nếu người dùng hỏi chủ đề **không** thuộc VinFast / mua & tài chính xe VinFast — gồm **xe hãng khác** (Toyota, Honda, Mazda, Mercedes, BMW, Hyundai, Kia, Ford, Chevrolet…), giá xe thế giới ngoài VinFast, hoặc chủ đề không liên quan (thời tiết, toán chung, lập trình…):
  - **Không** gọi công cụ (check_price / calculate_monthly_payment).
  - Trả lời **ngắn**, lịch sự, tiếng Việt: **chỉ hỗ trợ / chỉ tư vấn về xe VinFast**; nhắc họ đặt câu hỏi về giá, KM, trả góp hoặc các dòng **VF3, VF8 Plus, VF9 Plus, Lux A2.0** trong hệ thống.

1. check_price(model) — tra giá niêm yết và màu xe.
   model phải khớp chính xác: "VF3", "VF8 Plus", "VF9 Plus", "Lux A2.0".

2. calculate_monthly_payment(price, down_pct, months) — tính trả góp.
   price = giá SAU khuyến mãi, down_pct = % trả trước (20-50), months = 12/24/36/48/60.

{_promo_table()}

Khi nói khuyến mãi tiền mặt: luôn nêu số dạng **VNĐ có dấu chấm hàng nghìn** (vd 10.000.000 VNĐ) và có thể thêm **“X triệu”** tương ứng.

Tháng vay chỉ hợp lệ: 12, 24, 36, 48, 60. Nếu khách yêu cầu số tháng KHÁC (vd 50):
  - Vẫn phải gọi calculate_monthly_payment với **đúng months** khách nói (+ giá sau KM nếu đã có, down_pct = 20 nếu khách chưa nói %) để công cụ trả **lỗi** về kỳ hạn.
  - Trả lời: báo rõ không hỗ trợ kỳ đó, trích ý lỗi từ công cụ, liệt kê kỳ được hỗ trợ.
  - Tuyệt đối KHÔNG đổi sang 48/60 rồi trình bày như thể đáp ứng đúng “vay N tháng” của khách (N không hợp lệ).

Quy trình khi khách hỏi mua + trả góp:
  1. Gọi check_price để lấy giá niêm yết.
  2. Trừ discount từ bảng KM ở trên → giá sau KM.
  3. Gọi calculate_monthly_payment với giá sau KM.
  4. Trả lời đầy đủ bằng tiếng Việt, có số tiền cụ thể."""


def build_agent_v2():
    llm = ChatOpenAI(
        model=os.getenv("DEFAULT_MODEL", "gpt-4o"),
        api_key=os.getenv("OPENAI_API_KEY"),
    ).bind_tools(TOOLS)

    def llm_node(state: MessagesState):
        ensure_file_log(_PROJECT_ROOT)
        last_in = state["messages"][-1]
        prev = getattr(last_in, "content", str(last_in))
        log(f"LLM vào | {preview(str(prev), 400)}", _PROJECT_ROOT)
        msgs = [SystemMessage(content=_system_v2())] + state["messages"]
        resp = llm.invoke(msgs)
        if getattr(resp, "tool_calls", None):
            log(f"LLM ra | gọi công cụ: {[t.get('name', '?') for t in resp.tool_calls]}", _PROJECT_ROOT)
        else:
            log(f"LLM ra | trả lời: {preview(str(resp.content), 500)}", _PROJECT_ROOT)
        return {"messages": [resp]}

    def should_continue(state: MessagesState):
        last = state["messages"][-1]
        if getattr(last, "tool_calls", None):
            return "tools"
        return END

    graph = StateGraph(MessagesState)
    graph.add_node("llm", llm_node)
    graph.add_node("tools", make_logged_tool_node(TOOLS, _PROJECT_ROOT))

    graph.add_edge(START, "llm")
    graph.add_conditional_edges("llm", should_continue)
    graph.add_edge("tools", "llm")

    return graph.compile()


agent_v2 = build_agent_v2()


def run_v2(query: str | list[str]) -> str:
    from langchain_core.messages import HumanMessage

    turns = [query] if isinstance(query, str) else list(query)
    ensure_file_log(_PROJECT_ROOT)
    config = {
        "tags": ["vinfast", "agent_v2"],
        "metadata": {"agent": "v2", "project": "vinfast_langgraph"},
    }
    messages = []
    for i, text in enumerate(turns):
        log(f"[v2] Khách lượt {i + 1}/{len(turns)} | {preview(text, 500)}", _PROJECT_ROOT)
        messages.append(HumanMessage(content=text))
        invoke_cfg = with_timestamped_run_name(config, "run_v2", turn=i)
        result = agent_v2.invoke({"messages": messages}, config=invoke_cfg)
        messages = list(result["messages"])
    out = messages[-1].content
    log(f"[v2] Trả lời cuối | {preview(str(out), 650)}", _PROJECT_ROOT)
    return out
