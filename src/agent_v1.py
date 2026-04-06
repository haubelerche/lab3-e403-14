"""
vinfast_langgraph/src/agent_v1.py — Agent v1 (bug B1/B2 chủ đích).

LangGraph: __start__ → llm → [tools | __end__]
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from src.file_log import ensure_file_log, log, make_logged_tool_node, preview
from src.langsmith_run import with_timestamped_run_name
from src.tools import check_price, calculate_monthly_payment

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_PROJECT_ROOT / ".env")

TOOLS = [check_price, calculate_monthly_payment]

SYSTEM_V1 = """Bạn là trợ lý tư vấn mua xe VinFast.
Hãy dùng các công cụ sẵn có để trả lời câu hỏi của khách hàng."""


def build_agent_v1():
    llm = ChatOpenAI(
        model=os.getenv("DEFAULT_MODEL", "gpt-4o"),
        api_key=os.getenv("OPENAI_API_KEY"),
    ).bind_tools(TOOLS)

    def llm_node(state: MessagesState):
        ensure_file_log(_PROJECT_ROOT)
        last_in = state["messages"][-1]
        prev = getattr(last_in, "content", str(last_in))
        log(f"LLM vào | {preview(str(prev), 400)}", _PROJECT_ROOT)
        msgs = [SystemMessage(content=SYSTEM_V1)] + state["messages"]
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


agent_v1 = build_agent_v1()


def run_v1(query: str | list[str]) -> str:
    from langchain_core.messages import HumanMessage

    turns = [query] if isinstance(query, str) else list(query)
    ensure_file_log(_PROJECT_ROOT)
    config = {
        "tags": ["vinfast", "agent_v1"],
        "metadata": {"agent": "v1", "project": "vinfast_langgraph"},
    }
    messages = []
    for i, text in enumerate(turns):
        log(f"[v1] Khách lượt {i + 1}/{len(turns)} | {preview(text, 500)}", _PROJECT_ROOT)
        messages.append(HumanMessage(content=text))
        invoke_cfg = with_timestamped_run_name(config, "run_v1", turn=i)
        result = agent_v1.invoke({"messages": messages}, config=invoke_cfg)
        messages = list(result["messages"])
    out = messages[-1].content
    log(f"[v1] Trả lời cuối | {preview(str(out), 650)}", _PROJECT_ROOT)
    return out
