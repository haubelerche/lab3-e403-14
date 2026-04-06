#!/usr/bin/env python3
"""
Demo chat nhiều lượt (giữ ngữ cảnh) — chạy từ thư mục gốc project:

    python chat_demo.py        # mặc định v2
    python chat_demo.py v1     # agent v1

Cần OPENAI_API_KEY trong .env. Tắt ghi file log khi demo: FILE_LOG=0
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from langchain_core.messages import HumanMessage

from src.agent_v1 import agent_v1 as graph_v1
from src.agent_v2 import agent_v2 as graph_v2
from src.langsmith_run import with_timestamped_run_name


def main() -> None:
    version = "v2"
    if len(sys.argv) > 1 and sys.argv[1].lower() in ("v1", "v2"):
        version = sys.argv[1].lower()

    graph = graph_v1 if version == "v1" else graph_v2
    base_config = {
        "tags": ["vinfast", "chat_demo", version],
        "metadata": {"agent": version, "project": "vinfast_langgraph"},
    }

    print(f"VinFast — chat liên tục ({version}). Gõ /help xem lệnh.\n")

    messages: list = []
    msg_idx = 0
    while True:
        try:
            line = input("Bạn: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nTạm biệt.")
            break

        if not line:
            continue

        cmd = line.lower()
        if cmd in ("/quit", "/q", "quit", "exit"):
            print("Tạm biệt.")
            break
        if cmd in ("/clear", "/c"):
            messages = []
            msg_idx = 0
            print("(Đã xóa lịch sử.)\n")
            continue
        if cmd in ("/help", "/h", "?"):
            print("  /quit hoặc /q — thoát\n  /clear hoặc /c — xóa lịch sử hội thoại\n")
            continue

        messages.append(HumanMessage(content=line))
        try:
            invoke_cfg = with_timestamped_run_name(
                base_config, f"chat_{version}", turn=msg_idx
            )
            msg_idx += 1
            result = graph.invoke({"messages": messages}, config=invoke_cfg)
        except Exception as e:
            messages.pop()
            print(f"Bot: (lỗi) {e}\n")
            continue
        messages = list(result["messages"])
        last = messages[-1]
        content = getattr(last, "content", str(last))
        print(f"Bot: {content}\n")


if __name__ == "__main__":
    main()
