"""
Một file log mỗi lần chạy process: logs/vinfast_YYYYMMDD_HHMMSS.log
Tắt: FILE_LOG=0 trong .env
"""

from __future__ import annotations

import logging
import os
from datetime import datetime
from pathlib import Path

_LOGGER = logging.getLogger("vinfast.filelog")
_LOGGER.propagate = False
_READY = False
_LOG_PATH: Path | None = None


def file_log_enabled() -> bool:
    return os.getenv("FILE_LOG", "1").strip().lower() not in ("0", "false", "no", "off")


def ensure_file_log(project_root: Path | None = None) -> Path | None:
    global _READY, _LOG_PATH
    if not file_log_enabled():
        return None
    if _READY:
        return _LOG_PATH

    root = project_root or Path(__file__).resolve().parent.parent
    log_dir = root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = log_dir / f"vinfast_{ts}.log"

    _LOGGER.setLevel(logging.DEBUG)
    h = logging.FileHandler(path, encoding="utf-8")
    h.setFormatter(logging.Formatter("%(asctime)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
    _LOGGER.addHandler(h)

    _READY = True
    _LOG_PATH = path
    _LOGGER.info("======== BẮT ĐẦU PHIÊN | file: %s ========", path)
    return path


def log(msg: str, project_root: Path | None = None) -> None:
    if not file_log_enabled():
        return
    ensure_file_log(project_root)
    _LOGGER.info(msg)


def preview(text: str, limit: int = 300) -> str:
    t = (text or "").replace("\n", " ").strip()
    if len(t) <= limit:
        return t
    return t[: limit - 1] + "…"


def make_logged_tool_node(TOOLS, project_root: Path | None = None):
    from langgraph.prebuilt import ToolNode

    runner = ToolNode(TOOLS)

    def tools_node(state):
        last = state["messages"][-1]
        for tc in getattr(last, "tool_calls", None) or []:
            log(
                f"Công cụ GỌI → {tc.get('name', '?')} | tham số {tc.get('args', {})}",
                project_root,
            )
        out = runner.invoke(state)
        for m in out.get("messages", []):
            c = getattr(m, "content", str(m))
            log(f"Công cụ TRẢ VỀ ← {preview(str(c), 700)}", project_root)
        return out

    return tools_node
