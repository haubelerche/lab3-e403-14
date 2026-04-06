"""
Chạy từ thư mục gốc project (cùng cấp với src/, tests/):

    python run_evaluation.py
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

# Đảm bảo gốc project luôn trên PYTHONPATH (kể cả gọi từ IDE)
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from langchain_core.messages import HumanMessage

from src.agent_v1 import agent_v1, run_v1
from src.agent_v2 import agent_v2, run_v2
from src.file_log import ensure_file_log, file_log_enabled, log as file_log_line
from src.langsmith_run import with_timestamped_run_name
from tests.test_cases import TEST_CASES


def _preview(text: str, limit: int = 400) -> str:
    t = text.replace("\n", " ").strip()
    return t if len(t) <= limit else t[: limit - 1] + "…"


def _tc_user_messages(tc: dict) -> str | list[str]:
    if "turns" in tc:
        return tc["turns"]
    return tc["input"]


def _tc_question_preview(tc: dict) -> str:
    u = _tc_user_messages(tc)
    if isinstance(u, list):
        if len(u) == 1:
            return u[0][:80]
        return f"{len(u)} lượt — (1) {u[0][:40]}… (2) {u[-1][:40]}…"
    return u[:80]


def check_pass(answer: str, tc: dict) -> bool:
    a = answer.lower()
    return any(str(e).lower() in a for e in tc["expected_contains"])


def _check_turn_reply(reply: str, spec: dict) -> bool:
    a = reply.lower()
    for needle in spec.get("all", []):
        if str(needle).lower() not in a:
            return False
    if spec.get("any"):
        if not any(str(x).lower() in a for x in spec["any"]):
            return False
    return True


def _replies_per_turn(turns: list[str], version: str, case_id: str) -> list[str]:
    graph = agent_v1 if version == "v1" else agent_v2
    config = {
        "tags": ["vinfast", "eval", f"agent_{version}", case_id],
        "metadata": {"agent": version, "project": "vinfast_langgraph", "test_id": case_id},
    }
    messages: list = []
    replies: list[str] = []
    for i, text in enumerate(turns):
        messages.append(HumanMessage(content=text))
        invoke_cfg = with_timestamped_run_name(config, f"eval_{version}_{case_id}", turn=i)
        result = graph.invoke({"messages": messages}, config=invoke_cfg)
        messages = list(result["messages"])
        replies.append(str(messages[-1].content))
    return replies


def check_case_pass(tc: dict, version: str, _fn) -> tuple[str, bool]:
    if "per_turn" in tc:
        turns = list(tc["turns"])
        reps = _replies_per_turn(turns, version, tc["id"])
        specs = tc["per_turn"]
        if len(reps) != len(specs):
            return (reps[-1] if reps else "", False)
        ok = all(_check_turn_reply(reps[i], specs[i]) for i in range(len(specs)))
        return (reps[-1], ok)
    ans = _fn(_tc_user_messages(tc))
    return (ans, check_pass(ans, tc))


def run_all() -> None:
    print(f"\n{'='*72}")
    print("  VinFast LangGraph — Evaluation: Agent v1 vs v2")
    log_path = ensure_file_log(_ROOT)
    if log_path:
        print(f"  File log (cục bộ): {log_path}")
    elif not file_log_enabled():
        print("  File log: tắt (FILE_LOG=0)")
    if os.getenv("LANGCHAIN_TRACING_V2", "").lower() in ("1", "true", "yes"):
        proj = os.getenv("LANGCHAIN_PROJECT", "default")
        print(f"  LangSmith: trace → https://smith.langchain.com (project: {proj})")
    print(f"{'='*72}\n")

    results = []
    for tc in TEST_CASES:
        file_log_line(f"──────── Test {tc['id']} | {tc['type']} ────────", _ROOT)
        row: dict = {"id": tc["id"], "type": tc["type"]}
        for label, fn in [("v1", run_v1), ("v2", run_v2)]:
            t0 = time.time()
            try:
                ans, passed = check_case_pass(tc, label, fn)
                ms = int((time.time() - t0) * 1000)
            except Exception as e:
                ans = f"ERROR: {e}"
                passed = False
                ms = int((time.time() - t0) * 1000)
            row[label] = {"answer": ans, "passed": passed, "ms": ms}
        results.append(row)

        v1ok = "✅" if row["v1"]["passed"] else "❌"
        v2ok = "✅" if row["v2"]["passed"] else "❌"
        print(f"[{tc['id']}] {tc['type']:<10}  v1:{v1ok} {row['v1']['ms']:>5}ms   v2:{v2ok} {row['v2']['ms']:>5}ms")
        print(f"       Q: {_tc_question_preview(tc)}")
        print(f"       v1: {_preview(row['v1']['answer'])}")
        print(f"       v2: {_preview(row['v2']['answer'])}")
        print()

    v1_pass = sum(1 for r in results if r["v1"]["passed"])
    v2_pass = sum(1 for r in results if r["v2"]["passed"])
    n = len(TEST_CASES)
    print(f"{'─'*72}")
    print(f"  PASS RATE  v1: {v1_pass}/{n} ({v1_pass * 100 // max(n, 1)}%)    v2: {v2_pass}/{n} ({v2_pass * 100 // max(n, 1)}%)")
    print(f"{'='*72}\n")


if __name__ == "__main__":
    run_all()
