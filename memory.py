import json
import os
from datetime import datetime, timezone
from pathlib import Path

MEMORY_PATH = Path("data/memory.jsonl")


def load_recent(limit=None):
    limit = limit or int(os.environ.get("MAX_MEMORY_ITEMS", "12"))
    if not MEMORY_PATH.exists():
        return []
    lines = MEMORY_PATH.read_text(encoding="utf-8").splitlines()
    items = []
    for line in lines[-limit:]:
        try:
            items.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return items


def append_memory(item):
    MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **item,
    }
    with MEMORY_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record
