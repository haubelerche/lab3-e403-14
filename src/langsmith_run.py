"""Thêm run_name có timestamp để phân biệt từng lần chạy trên LangSmith."""

from __future__ import annotations

from datetime import datetime
from typing import Any


def with_timestamped_run_name(
    base: dict[str, Any],
    prefix: str,
    *,
    turn: int | None = None,
) -> dict[str, Any]:
    """prefix ví dụ: run_v2, eval_v2_T04. turn: lượt hội thoại (0-based)."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    if turn is not None:
        run_name = f"{prefix}_t{turn:02d}_{ts}"
    else:
        run_name = f"{prefix}_{ts}"
    out = {**base, "run_name": run_name}
    meta = dict(out.get("metadata") or {})
    meta.setdefault("run_ts", ts)
    out["metadata"] = meta
    return out
